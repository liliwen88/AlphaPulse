"""Complete investment advisor with structured markdown report generation."""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fetch_market_data import fetch_market_data
from calculate_indicators import calculate_all_indicators
from fetch_news import fetch_all_news
from score_engine import calculate_overall_score
from strategy_generator import generate_strategy
from config import DEFAULT_PERIOD, DEFAULT_INDICATORS

TIMEFRAME_PERIOD_MAP = {"short": "1mo", "medium": "6mo", "long": "1y"}


def gather_report_data(ticker: str, period: str, timeframe: str):
    """Gather all data needed for a report. Returns raw models."""
    snapshot = fetch_market_data(ticker)
    indicators = calculate_all_indicators(ticker, period, DEFAULT_INDICATORS)
    news = fetch_all_news(ticker)
    score = calculate_overall_score(ticker.upper(), snapshot, indicators, news)
    strategy = generate_strategy(ticker.upper(), snapshot, indicators, score)
    return snapshot, indicators, news, score, strategy


def _format_pct(val: float) -> str:
    """Format a float as a signed percentage string."""
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}%"


def generate_markdown_report(snapshot, indicators, news, score, strategy, timeframe: str) -> str:
    """Render a full investment analysis report in markdown following README template."""
    ticker = snapshot.ticker
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")

    # Build news items
    news_items = ""
    for a in news.articles[:5]:
        emoji = {"Positive": "🟢", "Negative": "🔴", "Neutral": "⚪"}.get(a.impact, "⚪")
        date_str = a.date.strftime("%Y-%m-%d")
        news_items += f"1. **{date_str}**: {a.headline} — 影响: {emoji} {a.impact}\n"
    if not news_items:
        news_items = "_无近期新闻数据_\n"

    # Score dimensions
    dimension_rows = ""
    for d in score.dimensions:
        dimension_rows += f"| {d.dimension.capitalize()} | {d.weight*100:.0f}% | {d.raw_score:.1f} | {d.weighted_score:.1f} |\n"

    # Price target
    if strategy.signal == "BUY":
        expected_move = f"+{round((strategy.take_profit - snapshot.current_price) / snapshot.current_price * 100, 1)}%" if strategy.take_profit else "N/A"
        best_case = f"+{round((strategy.take_profit * 1.05 - snapshot.current_price) / snapshot.current_price * 100, 1)}%" if strategy.take_profit else "N/A"
    elif strategy.signal == "SELL":
        expected_move = f"{round((strategy.stop_loss - snapshot.current_price) / snapshot.current_price * 100, 1)}%"
        best_case = "N/A"
    else:
        expected_move = "区间震荡"
        best_case = "取决于突破方向"

    worst_case = f"{round((strategy.stop_loss - snapshot.current_price) / snapshot.current_price * 100, 1)}%"

    direction_emoji = {"BUY": "📈 看涨", "HOLD": "➡️ 中性", "SELL": "📉 看跌"}.get(strategy.signal, "➡️ 中性")

    # Build markdown
    md = f"""# {ticker} 投资分析报告

**分析日期**: {ts}
**数据新鲜度**: {snapshot.data_freshness}
**信念级别**: {score.conviction}

---

## 执行摘要

综合评分 **{score.overall_score}/100**（{score.conviction} 信念）。当前价格处于52周区间的 **{snapshot.fifty_two_week_position_pct:.0f}%** 位置，信号为 **{strategy.signal}**。

**核心要点**: {strategy.rationale}

---

## 当前市场状态

- **价格**: ${snapshot.current_price:.2f} ({_format_pct(snapshot.day_change_pct)} 今日)
- **成交量**: {snapshot.volume/1e6:.1f}M (vs 均量 {_format_pct((snapshot.volume_ratio - 1) * 100)})
- **52周区间**: ${snapshot.fifty_two_week_low:.2f} - ${snapshot.fifty_two_week_high:.2f} (当前位置: {snapshot.fifty_two_week_position_pct:.0f}%)
- **市值**: ${snapshot.market_cap/1e9:.1f}B
- **关键技术位**: 支撑 ${snapshot.support_level or 'N/A'} | 阻力 ${snapshot.resistance_level or 'N/A'}

---

## 基本面分析

### 估值
- P/E: {snapshot.pe_ratio or 'N/A'}
- 股息率: {f'{snapshot.dividend_yield}%' if snapshot.dividend_yield else 'N/A'}

---

## 技术面分析

| 指标 | 数值 | 信号 |
|------|------|------|
| RSI(14) | {indicators.rsi or 'N/A'} | {"超卖" if indicators.rsi and indicators.rsi < 30 else "超买" if indicators.rsi and indicators.rsi > 70 else "中性"} |
| MACD | {indicators.macd or 'N/A'} | {"看涨" if indicators.macd_histogram and indicators.macd_histogram > 0 else "看跌" if indicators.macd_histogram and indicators.macd_histogram < 0 else "N/A"} |
| SMA 20 | {indicators.sma_20 or 'N/A'} | {"高于SMA20" if indicators.sma_20 and snapshot.current_price > indicators.sma_20 else "低于SMA20" if indicators.sma_20 else ""} |
| SMA 50 | {indicators.sma_50 or 'N/A'} | {"高于SMA50" if indicators.sma_50 and snapshot.current_price > indicators.sma_50 else "低于SMA50" if indicators.sma_50 else ""} |
| 布林上轨 | {indicators.bollinger_upper or 'N/A'} | |
| 布林下轨 | {indicators.bollinger_lower or 'N/A'} | |

---

## 新闻与催化剂

### 近期动态 (近{news.lookback_days}日)
{news_items}

---

## 综合评分

| 维度 | 权重 | 原始分 | 加权分 |
|------|------|--------|--------|
{dimension_rows}
| **总计** | **100%** | | **{score.overall_score}** |

---

## 风险评估

### 下行风险
- 止损位: ${strategy.stop_loss:.2f} ({worst_case})
- 仓位建议: {strategy.position_size_pct}%

---

## 投资策略

**信号**: {direction_emoji}

**操作建议**:
- 信号: **{strategy.signal}**
- 入场价: ${strategy.entry_price:.2f} (若适用)
- 止盈价: ${strategy.take_profit:.2f} (若适用)
- 止损价: ${strategy.stop_loss:.2f}
- 建议仓位: {strategy.position_size_pct}%

---

## 快速投资摘要

**方向**: {direction_emoji}

**价格目标 (未来1-3个月)**:
- 预期变动: {expected_move}
- 最佳情况: {best_case}
- 最差情况: {worst_case}

**简明建议**:
{strategy.rationale}

---

## 数据来源与时间戳

- 价格数据: yfinance 截至 {snapshot.data_freshness}
- 新闻: {', '.join(news.sources_succeeded) if news.sources_succeeded else 'N/A'}
- 技术指标: 基于 {indicators.period} 数据计算

**免责声明**: 本分析仅供信息参考，不构成投资建议。投资涉及风险，请自行研究并咨询合格财务顾问后再做决策。数据可能存在延迟或误差，请以官方来源核实。
"""
    return md


def generate_json_report(snapshot, indicators, news, score, strategy, timeframe: str) -> str:
    """Serialize report data as formatted JSON."""
    report = {
        "ticker": snapshot.ticker,
        "analysis_date": datetime.now(timezone.utc).isoformat(),
        "conviction": score.conviction,
        "overall_score": score.overall_score,
        "signal": strategy.signal,
        "market_snapshot": snapshot.model_dump(),
        "indicators": indicators.model_dump(),
        "news_summary": {
            "total_articles": len(news.articles),
            "positive": sum(1 for a in news.articles if a.impact == "Positive"),
            "negative": sum(1 for a in news.articles if a.impact == "Negative"),
            "neutral": sum(1 for a in news.articles if a.impact == "Neutral"),
        },
        "scores": {d.dimension: {"raw": d.raw_score, "weighted": d.weighted_score, "details": d.details} for d in score.dimensions},
        "strategy": strategy.model_dump(),
        "disclaimer": "本分析仅供信息参考，不构成投资建议。",
    }
    return json.dumps(report, indent=2, default=str, ensure_ascii=False)


def run_investment_advisor(
    ticker: str,
    period: str = DEFAULT_PERIOD,
    timeframe: str = "medium",
    output_format: str = "json",
    output_path: str | None = None,
) -> str:
    """Run full investment analysis and generate report."""
    # Map timeframe to actual period if using default
    actual_period = TIMEFRAME_PERIOD_MAP.get(timeframe, period)

    snapshot, indicators, news, score, strategy = gather_report_data(ticker, actual_period, timeframe)

    if output_format == "md":
        content = generate_markdown_report(snapshot, indicators, news, score, strategy, timeframe)
        ext = "md"
    else:
        content = generate_json_report(snapshot, indicators, news, score, strategy, timeframe)
        ext = "json"

    if output_path:
        out = Path(output_path)
        if out.suffix != f".{ext}":
            out = out.with_suffix(f".{ext}")
    else:
        out = Path(f"./{ticker.upper()}_investment_report.{ext}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return str(out)


def main():
    parser = argparse.ArgumentParser(description="Generate investment analysis report")
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument("--period", "-p", default=DEFAULT_PERIOD, help="Data period (default: 6mo)")
    parser.add_argument("--timeframe", choices=["short", "medium", "long"], default="medium", help="Investment timeframe")
    parser.add_argument("--format", "-f", choices=["json", "md"], default="json", help="Output format")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    try:
        path = run_investment_advisor(
            args.ticker,
            period=args.period,
            timeframe=args.timeframe,
            output_format=args.format,
            output_path=args.output,
        )
        print(f"Report saved to {path}")
    except Exception as e:
        print(f"Error generating investment report: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
