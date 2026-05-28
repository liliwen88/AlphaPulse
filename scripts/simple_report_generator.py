"""Simplified report generator for layman-friendly investment analysis."""

from __future__ import annotations
from datetime import datetime, timezone
from decision_card import DecisionCard, Signal, Confidence
from models import MarketSnapshot, IndicatorSet, NewsBundle, ScoreResult, StrategyResult
from terminology import get_simple_term, TERMINOLOGY_MAP
from typing import Optional


def format_percentage(value: float, signed: bool = True) -> str:
    """Format a percentage with optional sign."""
    sign = "+" if (value >= 0 and signed) else ""
    return f"{sign}{value:.2f}%"


def create_layman_summary(
    ticker: str,
    snapshot: MarketSnapshot,
    score: ScoreResult,
    strategy: StrategyResult,
    decision_card: DecisionCard,
) -> str:
    """Create a layman-friendly summary of the investment analysis."""
    
    # Determine signal description
    if strategy.signal == "BUY":
        signal_desc = "👉 **推荐买入** - 现在是不错的买点"
    elif strategy.signal == "SELL":
        signal_desc = "⛔ **建议卖出** - 考虑获利了结或规避风险"
    else:
        signal_desc = "⏸️ **持有观望** - 继续持有或等待更好的机会"
    
    # Conviction assessment
    conviction = score.conviction_level
    if conviction == "High":
        conviction_msg = "信号非常明确，信心很强 🔴"
    elif conviction == "Medium":
        conviction_msg = "信号还可以，但有一些不确定性 🟡"
    else:
        conviction_msg = "信号不够明确，建议等待 🟢"
    
    # Current situation
    price_change = format_percentage(snapshot.day_change)
    volume_change = format_percentage(snapshot.volume_change)
    
    # Build the summary
    summary = f"""
# 📊 {ticker} 投资分析速览

**分析日期**: {datetime.now(timezone.utc).strftime('%Y年%m月%d日 %H:%M UTC')}

---

## ⚡ 投资建议

{signal_desc}

**信心评级**: {conviction_msg}

---

## 📈 当前股价状态

- **现价**: ${snapshot.current_price:.2f}
- **今日涨跌**: {price_change} ({snapshot.day_change:+.2f}% 的股价变动)
- **成交量**: {volume_change} （对比平均）
- **52周范围**: ${snapshot.low_52_week:.2f} - ${snapshot.high_52_week:.2f}

**简单理解**: 股价现在{('在52周中期部分' if snapshot.day_change > 0 else '处于相对低位')}

---

## 💡 简单分析说明

"""
    
    # Add simple technical explanation
    if snapshot.rsi is not None:
        rsi = snapshot.rsi
        if rsi < 30:
            rsi_explanation = f"买卖热度很低 ({rsi:.0f})，可能存在反弹机会"
        elif rsi > 70:
            rsi_explanation = f"买卖热度很高 ({rsi:.0f})，可能面临回调"
        else:
            rsi_explanation = f"买卖热度适中 ({rsi:.0f})，市场情绪稳定"
        summary += f"- **买卖热度**: {rsi_explanation}\n"
    
    # Add news sentiment
    if hasattr(score, 'news_score'):
        if score.news_score > 60:
            news_desc = "最近有不少积极消息，看好因素较多"
        elif score.news_score < 40:
            news_desc = "最近消息面较为负面，需要谨慎"
        else:
            news_desc = "消息面混合，没有特别明显的倾向"
        summary += f"- **新闻面**: {news_desc}\n"
    
    # Add price target
    summary += f"""
---

## 🎯 价格目标

- **推荐入场价**: ${decision_card.entry_price:.2f}
- **目标价格范围**: ${decision_card.target_price_low:.2f} - ${decision_card.target_price_high:.2f}
- **止损位（保护本金）**: ${decision_card.stop_loss_price:.2f}
- **止盈位（锁定收益）**: ${decision_card.take_profit_price:.2f}

**简单理解**: 
- 如果价格跌到 ${decision_card.entry_price:.2f}，那是个不错的买点
- 目标是让股价涨到 ${decision_card.target_price_high:.2f} 左右
- 如果亏损超过止损位，就卖出保护本金
- 赚到止盈位的收益，就可以考虑获利了结

---

## 📊 概率分析

| 可能性 | 概率 |
|-------|------|
| 📈 股价上升 | {decision_card.upside_probability:.0f}% |
| 📉 股价下降 | {decision_card.downside_probability:.0f}% |
| ➡️ 价格盘整 | {decision_card.sideways_probability:.0f}% |

**简单理解**: 根据目前的分析，有 {decision_card.upside_probability:.0f}% 的概率股价会上升。

---

## ⏰ 关键看点

**什么会让我们更看好？**
{decision_card.bullish_catalyst}

**什么会让我们更看衰？**
{decision_card.bearish_catalyst}

---

## ⚠️ 需要警惕的风险

"""
    
    for risk in decision_card.key_risks:
        summary += f"- {risk}\n"
    
    summary += f"""
---

## 💰 操作建议（不是财务建议）

1. **对于想买的人**: {('在 $' + f'{decision_card.entry_price:.2f} 附近买入，分批建仓' if strategy.signal == 'BUY' else '等待更好的价格或更清晰的信号')}
2. **对于已持有的人**: {('继续持有，可以考虑逢低加仓' if strategy.signal == 'BUY' else ('考虑减仓或离场' if strategy.signal == 'SELL' else '继续观察'))}
3. **资金管理**: 不要押上全部身家，风险承受能力有限的话只投资 1-5% 的资本

---

**免责声明**: 这只是基于公开数据的分析参考，不构成投资建议。请根据自己的情况做出投资决定，必要时咨询专业财务顾问。
"""
    
    return summary


def generate_simple_markdown_report(
    snapshot: MarketSnapshot,
    indicators: IndicatorSet,
    news: NewsBundle,
    score: ScoreResult,
    strategy: StrategyResult,
    decision_card: DecisionCard,
) -> str:
    """Generate a simplified markdown report focused on clarity and actionability."""
    
    ticker = snapshot.ticker
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    
    # Build the report
    report = f"""# {ticker} 投资分析报告

**生成时间**: {ts}  
**数据新鲜度**: 价格数据 ≤5分钟 | 新闻 ≤24小时 | 宏观数据最新发布

---

## 📋 决策卡 (投资决策速查表)

{decision_card.to_markdown()}

---

## 白话分析

{create_layman_summary(ticker, snapshot, score, strategy, decision_card)}

---

## 📖 详细分析

### 当前市场状况

**价格信息**:
- 现价: ${snapshot.current_price:.2f}
- 今日变化: {format_percentage(snapshot.day_change)} 
- 成交量: {format_percentage(snapshot.volume_change)} vs 平均
- 52周高: ${snapshot.high_52_week:.2f} | 52周低: ${snapshot.low_52_week:.2f}

**技术位置**:
- 支撑位: ${snapshot.support_level:.2f}
- 阻力位: ${snapshot.resistance_level:.2f}

### 分数详解

**整体评分**: {score.overall_score:.0f}/100 (分数越高越看好)

- 技术面 (30%权重): {score.technical_score:.0f}/100
- 基本面 (25%权重): {score.fundamental_score:.0f}/100  
- 新闻面 (20%权重): {score.news_score:.0f}/100
- 情绪面 (15%权重): {score.sentiment_score:.0f}/100
- 宏观面 (10%权重): {score.macro_score:.0f}/100

---

## 📰 最近新闻

"""
    
    if news.articles:
        for article in news.articles[:5]:
            emoji = "✅" if article.impact == "Positive" else ("❌" if article.impact == "Negative" else "ℹ️")
            date_str = article.date.strftime("%Y-%m-%d")
            report += f"{emoji} **{date_str}**: {article.headline}\n"
    else:
        report += "最近暂无重大新闻。\n"
    
    report += f"""

---

## 数据来源与免责声明

- 价格数据: Yahoo Finance
- 新闻: Reuters, Bloomberg, Yahoo Finance
- 分析时间: {ts}

**重要提示**: 本分析仅供参考，不构成投资建议。投资有风险，请自行判断或咨询专业人士。

"""
    
    return report
