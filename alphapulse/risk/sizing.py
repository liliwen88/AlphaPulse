from __future__ import annotations

from alphapulse.risk.models import PositionSizing


def kelly_criterion(win_prob: float, win_loss_ratio: float) -> float:
    """Kelly criterion for optimal position sizing.

    Args:
        win_prob: Probability of a winning trade (0.0 to 1.0).
        win_loss_ratio: Ratio of avg win to avg loss (e.g., 2.0 = 2:1 reward:risk).
    """
    if win_loss_ratio <= 0:
        return 0.0
    loss_prob = 1 - win_prob
    kelly = win_prob - (loss_prob / win_loss_ratio)
    return max(0.0, kelly)


def vol_targeted_size(
    portfolio_value: float,
    annualized_vol: float,
    target_vol: float = 0.15,
    max_pct: float = 0.25,
    current_price: float = 1.0,
) -> PositionSizing:
    """Position sizing based on volatility targeting.

    Scale the position so that the stock's contribution to portfolio vol equals target_vol.

    Args:
        portfolio_value: Total portfolio value in USD.
        annualized_vol: The stock's annualized volatility (e.g., 0.35 = 35%).
        target_vol: Target annualized volatility contribution (e.g., 0.15 = 15%).
        max_pct: Maximum portfolio allocation percent (cap).
        current_price: Current stock price.
    """
    if annualized_vol <= 0:
        annualized_vol = 0.30

    raw_pct = target_vol / annualized_vol
    position_pct = min(raw_pct, max_pct)
    position_value = portfolio_value * position_pct
    shares = int(position_value / current_price) if current_price > 0 else 0

    stop_loss = None
    if current_price > 0:
        stop_loss = round(current_price * (1 - annualized_vol * 0.5), 2)

    return PositionSizing(
        portfolio_value=portfolio_value,
        method="vol_targeted",
        max_position_pct=round(position_pct * 100, 1),
        recommended_shares=shares,
        stop_loss_price=stop_loss,
        rationale=(
            f"Vol-targeted sizing: {annualized_vol * 100:.0f}% annualized vol → "
            f"{position_pct * 100:.1f}% allocation (target vol contribution: {target_vol * 100:.0f}%). "
            f"Max cap: {max_pct * 100:.0f}%."
        ),
    )


def equal_weight_size(
    portfolio_value: float,
    num_positions: int,
    current_price: float = 1.0,
) -> PositionSizing:
    """Equal-weight position sizing."""
    if num_positions <= 0:
        num_positions = 10
    allocation = portfolio_value / num_positions
    pct = 1.0 / num_positions
    shares = int(allocation / current_price) if current_price > 0 else 0

    return PositionSizing(
        portfolio_value=portfolio_value,
        method="equal_weight",
        max_position_pct=round(pct * 100, 1),
        recommended_shares=shares,
        rationale=f"Equal weight: 1/{num_positions} positions → {pct * 100:.1f}% each.",
    )
