"""Multi-dimensional scoring engine.

Weights: Technical(30%) + Fundamental(25%) + News(20%) + Sentiment(15%) + Macro(10%)
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from models import MarketSnapshot, IndicatorSet, NewsBundle, DimensionScore, ScoreResult
from config import (
    WEIGHTS,
    CONVICTION_HIGH_THRESHOLD,
    CONVICTION_MEDIUM_THRESHOLD,
)


def score_technical(snapshot: MarketSnapshot, indicators: IndicatorSet) -> DimensionScore:
    """Score technical posture (0-100) based on RSI, MACD, Bollinger, SMA, volume."""
    details: list[str] = []
    score = 50.0

    # RSI analysis
    rsi = indicators.rsi
    if rsi is not None:
        if rsi < 30:
            details.append(f"RSI at {rsi:.1f} indicates oversold conditions — bullish")
            score += 15
        elif rsi > 70:
            details.append(f"RSI at {rsi:.1f} indicates overbought conditions — bearish")
            score -= 15
        elif rsi > 60:
            details.append(f"RSI at {rsi:.1f} shows bullish momentum")
            score += 10
        elif rsi < 40:
            details.append(f"RSI at {rsi:.1f} shows bearish momentum")
            score -= 10
        else:
            details.append(f"RSI at {rsi:.1f} — neutral zone")

    # MACD analysis
    macd_hist = indicators.macd_histogram
    if macd_hist is not None:
        if macd_hist > 0:
            details.append(f"MACD histogram positive ({macd_hist:.4f}) — bullish momentum")
            score += 10
        else:
            details.append(f"MACD histogram negative ({macd_hist:.4f}) — bearish momentum")
            score -= 10

    # SMA alignment
    sma_20 = indicators.sma_20
    sma_50 = indicators.sma_50
    if sma_20 is not None and sma_50 is not None:
        if sma_20 > sma_50:
            details.append(f"SMA 20 ({sma_20:.2f}) above SMA 50 ({sma_50:.2f}) — short-term uptrend")
            score += 8
        else:
            details.append(f"SMA 20 ({sma_20:.2f}) below SMA 50 ({sma_50:.2f}) — short-term downtrend")
            score -= 8

    # Price vs Bollinger Bands
    price = snapshot.current_price
    upper = indicators.bollinger_upper
    lower = indicators.bollinger_lower
    if upper is not None and lower is not None and price > 0:
        if price > upper:
            details.append(f"Price above upper Bollinger Band — potentially overextended")
            score -= 8
        elif price < lower:
            details.append(f"Price below lower Bollinger Band — potentially oversold")
            score += 8
        else:
            band_width = upper - lower
            if band_width > 0:
                pct_b = (price - lower) / band_width
                details.append(f"Price at Bollinger %B = {pct_b:.2f}")

    # Volume confirmation
    if snapshot.volume_ratio > 1.5:
        if snapshot.day_change_pct > 0:
            details.append(f"High volume ({snapshot.volume_ratio:.1f}x avg) confirms upward move")
            score += 5
        else:
            details.append(f"High volume ({snapshot.volume_ratio:.1f}x avg) on decline — distribution")
            score -= 5

    # 52-week position
    pos = snapshot.fifty_two_week_position_pct
    if pos > 80:
        details.append(f"Near 52-week high ({pos:.0f}%) — possible resistance")
        score -= 3
    elif pos < 20:
        details.append(f"Near 52-week low ({pos:.0f}%) — possible support")
        score += 3
    else:
        details.append(f"Mid-range position in 52-week band ({pos:.0f}%)")

    clamped = max(0.0, min(100.0, score))
    return DimensionScore(
        dimension="technical",
        weight=WEIGHTS["technical"],
        raw_score=round(clamped, 1),
        weighted_score=round(clamped * WEIGHTS["technical"], 1),
        details=details,
    )


def score_fundamental(snapshot: MarketSnapshot) -> DimensionScore:
    """Score fundamentals (0-100) based on valuation metrics."""
    details: list[str] = []
    score = 50.0

    pe = snapshot.pe_ratio
    if pe is not None:
        if pe <= 0:
            details.append(f"Negative P/E ({pe:.1f}) — company not profitable")
            score -= 20
        elif pe < 15:
            details.append(f"Low P/E ({pe:.1f}) — potentially undervalued")
            score += 12
        elif pe < 25:
            details.append(f"Moderate P/E ({pe:.1f}) — reasonable valuation")
            score += 5
        elif pe < 40:
            details.append(f"High P/E ({pe:.1f}) — growth premium priced in")
            score -= 5
        else:
            details.append(f"Very high P/E ({pe:.1f}) — speculative valuation")
            score -= 12
    else:
        details.append("P/E data unavailable — no adjustment")

    div_yield = snapshot.dividend_yield
    if div_yield is not None and div_yield > 0:
        if div_yield > 3:
            details.append(f"Attractive dividend yield ({div_yield:.1f}%)")
            score += 8
        else:
            details.append(f"Dividend yield: {div_yield:.1f}%")

    market_cap = snapshot.market_cap
    if market_cap is not None:
        if market_cap > 200e9:
            details.append(f"Large cap (${market_cap/1e9:.0f}B) — stable")
            score += 3
        elif market_cap > 10e9:
            details.append(f"Mid cap (${market_cap/1e9:.0f}B)")
        elif market_cap > 0:
            details.append(f"Small cap (${market_cap/1e9:.1f}B) — higher volatility risk")
            score -= 5

    clamped = max(0.0, min(100.0, score))
    return DimensionScore(
        dimension="fundamental",
        weight=WEIGHTS["fundamental"],
        raw_score=round(clamped, 1),
        weighted_score=round(clamped * WEIGHTS["fundamental"], 1),
        details=details,
    )


def score_news(news_bundle: NewsBundle) -> DimensionScore:
    """Score news sentiment (0-100) based on article impact distribution."""
    details: list[str] = []
    articles = news_bundle.articles

    if not articles:
        details.append("No news articles found — neutral score")
        return DimensionScore(
            dimension="news",
            weight=WEIGHTS["news"],
            raw_score=50.0,
            weighted_score=round(50.0 * WEIGHTS["news"], 1),
            details=details,
        )

    positive = sum(1 for a in articles if a.impact == "Positive")
    negative = sum(1 for a in articles if a.impact == "Negative")
    neutral = sum(1 for a in articles if a.impact == "Neutral")
    total = len(articles)

    pos_ratio = positive / total
    neg_ratio = negative / total

    score = 50 + (pos_ratio - neg_ratio) * 40
    details.append(f"{positive} positive / {negative} negative / {neutral} neutral out of {total} articles")
    details.append(f"Sources succeeded: {', '.join(news_bundle.sources_succeeded) if news_bundle.sources_succeeded else 'none'}")

    clamped = max(0.0, min(100.0, score))
    return DimensionScore(
        dimension="news",
        weight=WEIGHTS["news"],
        raw_score=round(clamped, 1),
        weighted_score=round(clamped * WEIGHTS["news"], 1),
        details=details,
    )


def score_sentiment(news_bundle: NewsBundle) -> DimensionScore:
    """Sentiment score (0-100). Derived from news data as social sentiment proxy."""
    details: list[str] = []
    articles = news_bundle.articles

    if not articles:
        details.append("No sentiment data available — neutral score")
        return DimensionScore(
            dimension="sentiment",
            weight=WEIGHTS["sentiment"],
            raw_score=50.0,
            weighted_score=round(50.0 * WEIGHTS["sentiment"], 1),
            details=details,
        )

    # Weight recent articles more heavily
    now = datetime.now(timezone.utc)
    weighted_total = 0.0
    weight_sum = 0.0
    for a in articles:
        days_old = (now - a.date).total_seconds() / 86400
        recency_weight = max(1.0, 7.0 - days_old)
        if a.impact == "Positive":
            weighted_total += recency_weight
        elif a.impact == "Negative":
            weighted_total -= recency_weight
        weight_sum += recency_weight

    score = 50 + (weighted_total / weight_sum * 30) if weight_sum > 0 else 50.0
    details.append("Sentiment derived from news article tone with recency weighting")
    details.append("Social media data (Twitter/X, Reddit) requires API keys for direct analysis")

    clamped = max(0.0, min(100.0, round(score, 1)))
    return DimensionScore(
        dimension="sentiment",
        weight=WEIGHTS["sentiment"],
        raw_score=clamped,
        weighted_score=round(clamped * WEIGHTS["sentiment"], 1),
        details=details,
    )


def score_macro(ticker: str) -> DimensionScore:
    """Macro score (0-100). Returns neutral until live macro data feeds are wired."""
    return DimensionScore(
        dimension="macro",
        weight=WEIGHTS["macro"],
        raw_score=50.0,
        weighted_score=round(50.0 * WEIGHTS["macro"], 1),
        details=[
            "Macro score currently neutral — live macro data (CPI, FOMC, GDP) requires dedicated API integration",
            f"Ticker {ticker} — market-specific macro factors not yet assessed",
        ],
    )


def calculate_overall_score(
    ticker: str,
    snapshot: MarketSnapshot,
    indicators: IndicatorSet,
    news: NewsBundle,
) -> ScoreResult:
    """Compute weighted multi-dimensional score and conviction level."""
    dimensions = [
        score_technical(snapshot, indicators),
        score_fundamental(snapshot),
        score_news(news),
        score_sentiment(news),
        score_macro(ticker),
    ]

    overall = sum(d.weighted_score for d in dimensions)

    if overall >= CONVICTION_HIGH_THRESHOLD:
        conviction = "High"
    elif overall >= CONVICTION_MEDIUM_THRESHOLD:
        conviction = "Medium"
    else:
        conviction = "Low"

    return ScoreResult(
        ticker=ticker,
        timestamp=datetime.now(timezone.utc),
        overall_score=round(overall, 1),
        conviction=conviction,
        dimensions=dimensions,
    )
