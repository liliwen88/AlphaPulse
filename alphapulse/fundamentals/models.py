from __future__ import annotations

from pydantic import BaseModel, Field

from alphapulse.core.models import BaseResult


class CompanyProfile(BaseModel):
    symbol: str
    company_name: str = ""
    sector: str = ""
    industry: str = ""
    employees: int | None = None
    website: str | None = None
    business_summary: str | None = None


class IncomeStatementSummary(BaseModel):
    fiscal_year: int
    total_revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    eps_diluted: float


class BalanceSheetSummary(BaseModel):
    fiscal_year: int
    total_assets: float
    total_liabilities: float
    total_equity: float
    cash_and_equivalents: float
    long_term_debt: float


class CashFlowSummary(BaseModel):
    fiscal_year: int
    operating_cash_flow: float
    capital_expenditure: float
    free_cash_flow: float


class FinancialHealth(BaseModel):
    revenue_cagr_3y: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None
    fcf_yield: float | None = None
    debt_to_equity: float | None = None
    current_ratio: float | None = None
    roe: float | None = None
    roic: float | None = None


class DCFAssumptions(BaseModel):
    base_fcf: float
    growth_rate_stage1: float
    stage1_years: int = 5
    terminal_growth_rate: float = 0.03
    discount_rate: float = 0.10


class DCFValuation(BaseModel):
    assumptions: DCFAssumptions
    enterprise_value: float
    equity_value: float
    intrinsic_value_per_share: float
    margin_of_safety_pct: float | None = None


class PeerMetric(BaseModel):
    symbol: str
    company_name: str
    market_cap_billions: float | None = None
    pe_ratio: float | None = None
    ev_ebitda: float | None = None
    revenue_growth_pct: float | None = None
    net_margin_pct: float | None = None


class PeerComparison(BaseModel):
    primary_symbol: str
    peers: list[PeerMetric]


class FundamentalAnalysis(BaseResult):
    profile: CompanyProfile
    income_statements: list[IncomeStatementSummary] = Field(default_factory=list)
    balance_sheets: list[BalanceSheetSummary] = Field(default_factory=list)
    cash_flows: list[CashFlowSummary] = Field(default_factory=list)
    financial_health: FinancialHealth
    dcf_valuation: DCFValuation | None = None
    peer_comparison: PeerComparison | None = None
    risks: list[str] = Field(default_factory=list)
    catalysts: list[str] = Field(default_factory=list)
    conviction: str = "Medium"
