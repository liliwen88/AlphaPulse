"""Two-stage Discounted Cash Flow valuation model."""

from __future__ import annotations

from alphapulse.fundamentals.models import DCFAssumptions, DCFValuation


def build_dcf(
    base_fcf: float,
    growth_rate: float,
    terminal_growth: float = 0.03,
    discount_rate: float = 0.10,
    stage1_years: int = 5,
    shares_outstanding: int | None = None,
    net_debt: float = 0.0,
    current_price: float | None = None,
) -> DCFValuation:
    """Two-stage DCF model.

    Stage 1: High growth period (stage1_years)
    Stage 2: Terminal value via Gordon Growth Model

    Args:
        base_fcf: Starting free cash flow (in millions).
        growth_rate: Stage 1 annual growth rate (e.g., 0.12 = 12%).
        terminal_growth: Perpetual growth rate (e.g., 0.03 = 3%).
        discount_rate: WACC (e.g., 0.10 = 10%).
        stage1_years: Number of high-growth years.
        shares_outstanding: Shares outstanding in millions.
        net_debt: Total debt - cash (in millions).
        current_price: Current stock price for margin of safety calculation.
    """
    assumptions = DCFAssumptions(
        base_fcf=base_fcf,
        growth_rate_stage1=growth_rate,
        stage1_years=stage1_years,
        terminal_growth_rate=terminal_growth,
        discount_rate=discount_rate,
    )

    # Stage 1: PV of projected FCFs
    pv_fcf_sum = 0.0
    fcf = base_fcf
    for year in range(1, stage1_years + 1):
        fcf = fcf * (1 + growth_rate)
        pv = fcf / ((1 + discount_rate) ** year)
        pv_fcf_sum += pv

    # Stage 2: Terminal value (Gordon Growth)
    terminal_fcf = fcf * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    pv_terminal = terminal_value / ((1 + discount_rate) ** stage1_years)

    enterprise_value = pv_fcf_sum + pv_terminal
    equity_value = enterprise_value - net_debt

    intrinsic_per_share = None
    margin_of_safety = None
    if shares_outstanding and shares_outstanding > 0:
        intrinsic_per_share = equity_value / shares_outstanding
        if current_price and current_price > 0:
            margin_of_safety = round(
                (intrinsic_per_share - current_price) / intrinsic_per_share * 100, 1
            )

    return DCFValuation(
        assumptions=assumptions,
        enterprise_value=round(enterprise_value, 2),
        equity_value=round(equity_value, 2),
        intrinsic_value_per_share=round(intrinsic_per_share, 2) if intrinsic_per_share is not None else 0.0,
        margin_of_safety_pct=margin_of_safety,
    )
