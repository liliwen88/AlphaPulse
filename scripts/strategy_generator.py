"""Generate actionable investment strategies: signal, entry, exit, stop-loss, position sizing."""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models import MarketSnapshot, IndicatorSet, ScoreResult, StrategyResult
from config import (
    DEFAULT_POSITION_SIZE,
    POSITION_SIZE_HIGH_CONVICTION,
    POSITION_SIZE_LOW_CONVICTION,
    STOP_LOSS_ATR_MULTIPLIER,
    TAKE_PROFIT_ATR_MULTIPLIER,
)


def determine_signal(score: ScoreResult, indicators: IndicatorSet) -> str:
    """Determine BUY/HOLD/SELL based on overall score and indicator confirmation."""
    overall = score.overall_score
    rsi = indicators.rsi

    if overall >= 70:
        if rsi is not None and rsi < 70:
            return "BUY"
        return "HOLD"  # Good score but overbought
    if overall < 30:
        return "SELL"
    if overall >= 50:
        if rsi is not None and rsi < 30:
            return "BUY"  # Oversold bounce potential
    if overall < 40:
        if rsi is not None and rsi > 70:
            return "SELL"  # Overbought with poor score

    return "HOLD"


def calculate_entry_price(snapshot: MarketSnapshot, indicators: IndicatorSet) -> float:
    """Suggested entry price: nearest support or 2% below current, whichever is higher."""
    support = snapshot.support_level
    sma_50 = indicators.sma_50
    discount_2pct = snapshot.current_price * 0.98

    candidates = [discount_2pct]
    if support is not None:
        candidates.append(support)
    if sma_50 is not None:
        candidates.append(sma_50)

    return round(max(c for c in candidates if c < snapshot.current_price), 2)


def calculate_exit_prices(
    snapshot: MarketSnapshot,
    indicators: IndicatorSet,
    signal: str,
) -> tuple[float | None, float]:
    """Return (take_profit, stop_loss)."""
    current = snapshot.current_price
    resistance = snapshot.resistance_level

    # Stop-loss: below nearest support or fixed percentage
    support = snapshot.support_level
    if support is not None:
        stop_loss = round(min(support * 0.98, current * 0.95), 2)
    else:
        stop_loss = round(current * 0.93, 2)

    # Take-profit: nearest resistance or fixed percentage
    if signal == "SELL":
        return None, stop_loss

    if resistance is not None and resistance > current:
        take_profit = round(resistance * 0.98, 2)
    else:
        take_profit = round(current * 1.10, 2)

    return take_profit, stop_loss


def calculate_position_size(conviction: str) -> float:
    """Map conviction to position size percentage."""
    if conviction == "High":
        return POSITION_SIZE_HIGH_CONVICTION
    if conviction == "Low":
        return POSITION_SIZE_LOW_CONVICTION
    return DEFAULT_POSITION_SIZE


def generate_strategy(
    ticker: str,
    snapshot: MarketSnapshot,
    indicators: IndicatorSet,
    score: ScoreResult,
) -> StrategyResult:
    """Orchestrate: determine signal, entry/exit, position size."""
    signal = determine_signal(score, indicators)
    take_profit, stop_loss = calculate_exit_prices(snapshot, indicators, signal)
    position_pct = calculate_position_size(score.conviction)

    entry = calculate_entry_price(snapshot, indicators) if signal == "BUY" else None

    # Build rationale
    parts = [
        f"Overall score: {score.overall_score}/100 ({score.conviction} conviction)",
        f"Signal: {signal}",
    ]
    if entry:
        parts.append(f"Entry target: ${entry}")
    if take_profit:
        parts.append(f"Take-profit: ${take_profit}")
    parts.append(f"Stop-loss: ${stop_loss}")
    parts.append(f"Position size: {position_pct}% of portfolio")

    return StrategyResult(
        ticker=ticker,
        timestamp=datetime.now(timezone.utc),
        signal=signal,
        entry_price=entry,
        take_profit=take_profit,
        stop_loss=stop_loss,
        position_size_pct=position_pct,
        rationale=" | ".join(parts),
    )
