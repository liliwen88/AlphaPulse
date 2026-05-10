from __future__ import annotations

import asyncio
import logging

import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.models import DataSource
from alphapulse.fundamentals.dcf import build_dcf
from alphapulse.fundamentals.models import (
    BalanceSheetSummary,
    CashFlowSummary,
    CompanyProfile,
    FinancialHealth,
    FundamentalAnalysis,
    IncomeStatementSummary,
)
from alphapulse.fundamentals.peer import find_peers
from alphapulse.fundamentals.sec_client import get_company_facts, get_filing_list, lookup_cik

logger = logging.getLogger(__name__)


class FundamentalService:
    """Service for deep fundamental analysis of stocks."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()

    async def analyze(
        self,
        symbol: str,
        include_dcf: bool = True,
        include_peers: bool = True,
    ) -> FundamentalAnalysis:
        symbol = symbol.strip().upper()
        t = await asyncio.to_thread(lambda: yf.Ticker(symbol))
        info = await asyncio.to_thread(lambda: t.info)

        profile = CompanyProfile(
            symbol=symbol,
            company_name=(
                info.get("longName") or info.get("shortName") or ""
            ),
            sector=info.get("sector") or "",
            industry=info.get("industry") or "",
            employees=info.get("fullTimeEmployees"),
            website=info.get("website"),
            business_summary=info.get("longBusinessSummary"),
        )

        # Financial statements
        income = self._parse_income_statements(t)
        balance = self._parse_balance_sheets(t)
        cash = self._parse_cash_flows(t)

        # Financial health metrics
        health = self._compute_health(info, income, balance, cash)

        # DCF
        dcf = None
        fcf = cash[0].free_cash_flow if cash else None
        shares = info.get("sharesOutstanding")
        net_debt = 0.0
        if balance:
            net_debt = balance[0].long_term_debt - balance[0].cash_and_equivalents
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        growth_est = info.get("revenueGrowth") or 0.05

        if include_dcf and fcf and shares and current_price:
            try:
                dcf = build_dcf(
                    base_fcf=fcf,
                    growth_rate=max(growth_est, 0.03),
                    shares_outstanding=shares / 1e6,
                    net_debt=net_debt,
                    current_price=current_price,
                )
            except Exception as e:
                logger.warning(f"DCF build failed: {e}")

        # Peers
        peer_comp = None
        if include_peers:
            try:
                peer_comp = await find_peers(symbol, config=self._config)
            except Exception as e:
                logger.warning(f"Peer analysis failed: {e}")

        # Risks and catalysts
        risks = self._identify_risks(info, health)
        catalysts = self._identify_catalysts(info)

        # Conviction
        conviction = self._determine_conviction(health, dcf, peer_comp)

        sources = [DataSource.YAHOO_FINANCE.value]

        # Optionally check SEC for filings
        try:
            cik = await lookup_cik(symbol, self._config)
            if cik:
                sources.append(DataSource.SEC_EDGAR.value)
        except Exception:
            pass

        return FundamentalAnalysis(
            profile=profile,
            income_statements=income,
            balance_sheets=balance,
            cash_flows=cash,
            financial_health=health,
            dcf_valuation=dcf,
            peer_comparison=peer_comp,
            risks=risks,
            catalysts=catalysts,
            conviction=conviction,
            data_sources=sources,
        )

    @staticmethod
    def _parse_income_statements(t) -> list[IncomeStatementSummary]:
        try:
            fs = t.financials  # annual
            if fs is None or fs.empty:
                return []
            results = []
            for year in fs.columns[:3]:
                row = fs[year]
                results.append(IncomeStatementSummary(
                    fiscal_year=year.year if hasattr(year, "year") else 0,
                    total_revenue=round(float(row.get("Total Revenue", 0)) / 1e6, 1),
                    gross_profit=round(float(row.get("Gross Profit", 0)) / 1e6, 1),
                    operating_income=round(float(row.get("Operating Income", 0)) / 1e6, 1),
                    net_income=round(float(row.get("Net Income", 0)) / 1e6, 1),
                    eps_diluted=round(float(row.get("Diluted EPS", 0)), 2),
                ))
            return results
        except Exception as e:
            logger.warning(f"Failed to parse income statements: {e}")
            return []

    @staticmethod
    def _parse_balance_sheets(t) -> list[BalanceSheetSummary]:
        try:
            bs = t.balance_sheet
            if bs is None or bs.empty:
                return []
            results = []
            for year in bs.columns[:3]:
                row = bs[year]
                results.append(BalanceSheetSummary(
                    fiscal_year=year.year if hasattr(year, "year") else 0,
                    total_assets=round(float(row.get("Total Assets", 0)) / 1e6, 1),
                    total_liabilities=round(float(row.get("Total Liabilities Net Minority Interest", 0)) / 1e6, 1),
                    total_equity=round(float(row.get("Stockholders Equity", 0)) / 1e6, 1),
                    cash_and_equivalents=round(float(row.get("Cash And Cash Equivalents", 0)) / 1e6, 1),
                    long_term_debt=round(float(row.get("Long Term Debt", 0)) / 1e6, 1),
                ))
            return results
        except Exception as e:
            logger.warning(f"Failed to parse balance sheets: {e}")
            return []

    @staticmethod
    def _parse_cash_flows(t) -> list[CashFlowSummary]:
        try:
            cf = t.cashflow
            if cf is None or cf.empty:
                return []
            results = []
            for year in cf.columns[:3]:
                row = cf[year]
                ocf = float(row.get("Operating Cash Flow", 0)) / 1e6
                capex = float(row.get("Capital Expenditure", 0)) / 1e6
                results.append(CashFlowSummary(
                    fiscal_year=year.year if hasattr(year, "year") else 0,
                    operating_cash_flow=round(ocf, 1),
                    capital_expenditure=round(capex, 1),
                    free_cash_flow=round(ocf + capex, 1),  # capex is negative in yfinance
                ))
            return results
        except Exception as e:
            logger.warning(f"Failed to parse cash flows: {e}")
            return []

    @staticmethod
    def _compute_health(
        info: dict,
        income: list,
        balance: list,
        cash: list,
    ) -> FinancialHealth:
        health = FinancialHealth()

        if income and len(income) >= 3:
            revs = [s.total_revenue for s in income[:3]]
            if revs[2] and revs[2] != 0:
                health.revenue_cagr_3y = round(
                    ((revs[0] / revs[2]) ** (1 / 3) - 1) * 100, 1
                )

        if income:
            s = income[0]
            if s.total_revenue and s.total_revenue != 0:
                health.gross_margin = round(s.gross_profit / s.total_revenue * 100, 1)
                health.operating_margin = round(s.operating_income / s.total_revenue * 100, 1)
                health.net_margin = round(s.net_income / s.total_revenue * 100, 1)

        if cash and info.get("marketCap"):
            fcf = cash[0].free_cash_flow
            health.fcf_yield = round(fcf / (info["marketCap"] / 1e6) * 100, 1)

        if balance:
            s = balance[0]
            if s.total_equity and s.total_equity != 0:
                health.debt_to_equity = round(s.long_term_debt / s.total_equity, 2)
                health.current_ratio = round(
                    (s.total_assets - s.long_term_debt - s.total_equity + s.total_liabilities)
                    / (s.total_liabilities - s.long_term_debt)
                    if (s.total_liabilities - s.long_term_debt) != 0
                    else 99,
                    2,
                )

        roe = info.get("returnOnEquity")
        if roe:
            health.roe = round(roe * 100, 1)

        roic = info.get("returnOnCapital")
        if roic:
            health.roic = round(roic * 100, 1)

        return health

    @staticmethod
    def _identify_risks(info, health):
        risks = []
        if health.debt_to_equity and health.debt_to_equity > 2.0:
            risks.append("High leverage: Debt/Equity > 2.0x")
        if health.current_ratio and health.current_ratio < 1.0:
            risks.append("Liquidity concern: Current Ratio < 1.0")
        if health.net_margin is not None and health.net_margin < 0:
            risks.append("Negative net margin — unprofitable")
        beta = info.get("beta")
        if beta and beta > 2.0:
            risks.append(f"High beta ({beta:.1f}) — elevated systematic risk")
        short_pct = info.get("shortPercentOfFloat")
        if short_pct and short_pct > 0.20:
            risks.append(f"High short interest ({short_pct * 100:.0f}%) — potential squeeze or bearish signal")
        return risks

    @staticmethod
    def _identify_catalysts(info):
        catalysts = []
        earnings_date = info.get("earningsDate")
        if earnings_date:
            catalysts.append("Upcoming earnings announcement")
        growth = info.get("revenueGrowth")
        if growth and growth > 0.15:
            catalysts.append(f"Strong revenue growth trend ({growth * 100:.0f}% YoY)")
        peg = info.get("pegRatio")
        if peg and peg < 1.0:
            catalysts.append(f"PEG < 1.0 ({peg:.2f}) — potentially undervalued growth")
        return catalysts

    @staticmethod
    def _determine_conviction(health, dcf, peers):
        score = 0
        if health.revenue_cagr_3y and health.revenue_cagr_3y > 10:
            score += 1
        if health.net_margin and health.net_margin > 15:
            score += 1
        if health.fcf_yield and health.fcf_yield > 3:
            score += 1
        if health.roic and health.roic > 15:
            score += 1
        if dcf and dcf.margin_of_safety_pct and dcf.margin_of_safety_pct > 20:
            score += 1
        if health.debt_to_equity and health.debt_to_equity < 1:
            score += 1

        if score >= 4:
            return "High"
        if score >= 2:
            return "Medium"
        return "Low"
