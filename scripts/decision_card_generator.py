"""Generate decision cards with probability assessments and clear investment actions."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models import MarketSnapshot, IndicatorSet, ScoreResult
from decision_card import DecisionCard, Signal, Confidence
from strategy_generator import (
    determine_signal,
    calculate_entry_price,
    calculate_exit_prices,
    calculate_position_size,
)


def map_conviction_to_confidence(conviction: str) -> Confidence:
    """Map conviction string to Confidence enum."""
    if conviction == "High":
        return Confidence.HIGH
    elif conviction == "Low":
        return Confidence.LOW
    else:
        return Confidence.MEDIUM


def calculate_probabilities(
    score: ScoreResult,
    snapshot: MarketSnapshot,
) -> tuple[float, float, float]:
    """Calculate probabilities of upside, downside, sideways movements.
    
    Returns: (upside_prob, downside_prob, sideways_prob)
    """
    overall = score.overall_score
    
    # Base probability calculation on overall score
    # Score 0-33: bearish, 33-67: neutral, 67-100: bullish
    if overall >= 70:
        upside = min(75, 50 + (overall - 50) * 0.5)
        downside = max(10, 30 - (overall - 50) * 0.3)
    elif overall >= 50:
        upside = min(65, 40 + (overall - 50) * 0.5)
        downside = max(15, 35 - (overall - 50) * 0.3)
    elif overall >= 30:
        upside = 35
        downside = 40
    else:
        upside = min(20, 10 + overall * 0.2)
        downside = min(80, 70 + (30 - overall) * 0.3)
    
    # Adjust based on RSI extremes
    if snapshot.rsi is not None:
        if snapshot.rsi < 20:  # Heavily oversold
            upside += 10
            downside = max(0, downside - 10)
        elif snapshot.rsi > 80:  # Heavily overbought
            upside = max(10, upside - 10)
            downside += 10
    
    sideways = max(0, 100 - upside - downside)
    upside = max(0, min(100, upside))
    downside = max(0, min(100, downside))
    
    # Normalize to sum to 100
    total = upside + downside + sideways
    if total > 0:
        upside = (upside / total) * 100
        downside = (downside / total) * 100
        sideways = (sideways / total) * 100
    
    return round(upside, 1), round(downside, 1), round(sideways, 1)


def generate_decision_card(
    ticker: str,
    snapshot: MarketSnapshot,
    indicators: IndicatorSet,
    score: ScoreResult,
) -> DecisionCard:
    """Generate a structured decision card with clear investment action."""
    
    # Determine signal
    signal_str = determine_signal(score, indicators)
    signal = Signal[signal_str]
    
    # Get confidence level
    confidence = map_conviction_to_confidence(score.conviction)
    
    # Calculate prices
    entry_price = calculate_entry_price(snapshot, indicators)
    take_profit, stop_loss = calculate_exit_prices(snapshot, indicators, signal_str)
    
    # Target price: range from entry to take_profit or above
    if take_profit is not None:
        target_low = entry_price
        target_high = take_profit * 1.15  # 15% above take profit as best case
    else:
        # For SELL signal, estimate conservative target
        target_low = snapshot.current_price * 0.90
        target_high = snapshot.current_price * 0.85
    
    # Calculate probabilities
    upside_prob, downside_prob, sideways_prob = calculate_probabilities(score, snapshot)
    
    # Determine catalysts
    if score.news_score > 60:
        bullish_catalyst = f"正面新闻面支持：{score.conviction} 看多信号"
    elif score.technical_score > 70:
        bullish_catalyst = "技术面突破：多条均线向上排列"
    else:
        bullish_catalyst = "估值吸引力：价格处于相对低位"
    
    if score.news_score < 40:
        bearish_catalyst = f"负面新闻：需要确认是否反转"
    elif score.technical_score < 30:
        bearish_catalyst = "技术面破位：下跌趋势未改"
    else:
        bearish_catalyst = "估值风险：价格可能回到支撑位"
    
    # Key risks
    risks = []
    if score.macro_score < 40:
        risks.append("宏观经济不确定性可能冲击市场")
    if snapshot.volume_change < -30:
        risks.append("成交量萎缩，可能缺乏上升动力")
    if score.sentiment_score < 30:
        risks.append("市场情绪悲观，可能出现抛售")
    if len(risks) == 0:
        risks.append("市场波动风险始终存在，建议分批操作")
    
    return DecisionCard(
        ticker=ticker,
        signal=signal,
        confidence=confidence,
        target_price_low=round(target_low, 2),
        target_price_high=round(target_high, 2),
        entry_price=round(entry_price, 2),
        stop_loss_price=round(stop_loss, 2),
        take_profit_price=round(take_profit, 2) if take_profit else round(entry_price * 1.10, 2),
        upside_probability=upside_prob,
        downside_probability=downside_prob,
        sideways_probability=sideways_prob,
        bullish_catalyst=bullish_catalyst,
        bearish_catalyst=bearish_catalyst,
        key_risks=risks,
    )
