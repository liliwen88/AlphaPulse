"""Tests for Pydantic models and BaseResult contract."""

import pytest

from alphapulse.core.disclaimer import RISK_DISCLAIMER
from alphapulse.core.models import BaseResult, DataFreshness, DataSource
from alphapulse.quote.models import StockQuote
from alphapulse.technical.models import TechnicalAnalysis, MovingAverages, MACDResult, RSIResult, BollingerBands, SupportResistanceLevels, VolumeProfile
from alphapulse.hotspots.models import MarketHotspots
from alphapulse.fundamentals.models import FundamentalAnalysis, CompanyProfile, FinancialHealth
from alphapulse.macro.models import MacroOutlook, MacroRegime
from alphapulse.flow.models import InstitutionalFlow
from alphapulse.risk.models import RiskAssessment, VolatilityMetrics, DrawdownMetrics, VaRMetrics


class TestBaseResult:
    def test_disclaimer_is_present(self):
        result = BaseResult()
        assert result.disclaimer == RISK_DISCLAIMER
        assert len(result.disclaimer) > 50

    def test_disclaimer_is_frozen(self):
        result = BaseResult()
        with pytest.raises(Exception):
            result.disclaimer = "changed"

    def test_json_serialization(self):
        result = BaseResult(data_sources=["yahoo_finance"])
        data = result.model_dump_json()
        assert "disclaimer" in data
        assert "timestamp" in data


class TestStockQuote:
    def test_inherits_base_result(self):
        quote = StockQuote(
            symbol="AAPL",
            current_price=175.0,
            previous_close=173.5,
            change=1.5,
            change_percent=0.86,
            volume=55_000_000,
        )
        assert quote.disclaimer == RISK_DISCLAIMER
        assert quote.symbol == "AAPL"

    def test_json_output(self):
        quote = StockQuote(
            symbol="AAPL",
            current_price=175.0,
            previous_close=173.5,
            change=1.5,
            change_percent=0.86,
            volume=55_000_000,
            data_sources=["yahoo_finance"],
        )
        data = quote.model_dump_json()
        assert '"symbol":"AAPL"' in data
        assert '"disclaimer"' in data
        assert '"current_price":175.0' in data


class TestAllResultsHaveDisclaimer:
    """Every BaseResult subclass must include the risk disclaimer."""

    def test_technical_analysis(self):
        ta = TechnicalAnalysis(
            symbol="AAPL",
            period="6mo",
            interval="1d",
            current_price=175.0,
            moving_averages=MovingAverages(),
            macd=MACDResult(macd_line=0, signal_line=0, histogram=0, signal="above_zero"),
            rsi=RSIResult(value=50, signal="neutral"),
            bollinger=BollingerBands(upper=180, middle=175, lower=170, bandwidth=0.06, position="inside"),
            levels=SupportResistanceLevels(),
            volume=VolumeProfile(current_volume=1000000, avg_volume_20d=1000000, volume_ratio=1.0, signal="normal"),
            posture="Neutral/Rangebound",
        )
        assert ta.disclaimer == RISK_DISCLAIMER

    def test_market_hotspots(self):
        mh = MarketHotspots()
        assert mh.disclaimer == RISK_DISCLAIMER

    def test_fundamental_analysis(self):
        fa = FundamentalAnalysis(
            profile=CompanyProfile(symbol="AAPL"),
            financial_health=FinancialHealth(),
        )
        assert fa.disclaimer == RISK_DISCLAIMER

    def test_macro_outlook(self):
        mo = MacroOutlook(
            current_week_events=[],
            upcoming_events=[],
            regime=MacroRegime(),
        )
        assert mo.disclaimer == RISK_DISCLAIMER

    def test_institutional_flow(self):
        flow = InstitutionalFlow(symbol="AAPL")
        assert flow.disclaimer == RISK_DISCLAIMER

    def test_risk_assessment(self):
        ra = RiskAssessment(
            symbol="AAPL",
            volatility=VolatilityMetrics(),
            drawdown=DrawdownMetrics(),
            var=VaRMetrics(),
        )
        assert ra.disclaimer == RISK_DISCLAIMER
