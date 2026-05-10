"""Tests for DCF valuation model."""

from alphapulse.fundamentals.dcf import build_dcf


class TestDCF:
    def test_basic_two_stage(self):
        dcf = build_dcf(
            base_fcf=100_000,
            growth_rate=0.10,
            terminal_growth=0.03,
            discount_rate=0.10,
            stage1_years=5,
            shares_outstanding=1_000,
            net_debt=100_000,
            current_price=100.0,
        )
        assert dcf.enterprise_value > 0
        assert dcf.equity_value > 0
        assert dcf.intrinsic_value_per_share > 0

    def test_margin_of_safety(self):
        dcf = build_dcf(
            base_fcf=100_000,
            growth_rate=0.12,
            terminal_growth=0.03,
            discount_rate=0.08,
            stage1_years=5,
            shares_outstanding=1_000,
            net_debt=0,
            current_price=500.0,
        )
        assert dcf.margin_of_safety_pct is not None

    def test_no_shares_no_mos(self):
        dcf = build_dcf(
            base_fcf=100_000,
            growth_rate=0.10,
        )
        assert dcf.margin_of_safety_pct is None


class TestDCFEdgeCases:
    def test_zero_growth(self):
        dcf = build_dcf(base_fcf=50_000, growth_rate=0.0)
        assert dcf.enterprise_value > 0

    def test_high_growth(self):
        dcf = build_dcf(base_fcf=10_000, growth_rate=0.30)
        assert dcf.enterprise_value > 0
