"""Decision card for clear investment action recommendations."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    """Investment signal: BUY, SELL, or HOLD."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Confidence(Enum):
    """Confidence level in the signal."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class DecisionCard:
    """Structured investment decision card with clear actions."""
    
    ticker: str
    signal: Signal
    confidence: Confidence
    
    # Price targets
    target_price_low: float
    target_price_high: float
    entry_price: float  # Suggested buy price
    stop_loss_price: float
    take_profit_price: float
    
    # Probabilities
    upside_probability: float  # 0-100
    downside_probability: float
    sideways_probability: float
    
    # Key catalysts and risks
    bullish_catalyst: str
    bearish_catalyst: str
    key_risks: list[str]
    
    def to_markdown(self) -> str:
        """Format decision card as markdown."""
        emoji_signal = {
            Signal.BUY: "📈",
            Signal.SELL: "📉",
            Signal.HOLD: "➡️",
        }[self.signal]
        
        emoji_confidence = {
            Confidence.HIGH: "🔴",
            Confidence.MEDIUM: "🟡",
            Confidence.LOW: "🟢",
        }[self.confidence]
        
        content = f"""
## 📊 {self.ticker} 投资决策卡

| 项目 | 建议 |
|------|------|
| **信号** | {emoji_signal} {self.signal.value} |
| **信心度** | {emoji_confidence} {self.confidence.value} |
| **时间框架** | 1-3个月 |

### 价格目标

| 类型 | 价格 |
|------|------|
| **目标价格范围** | ${self.target_price_low:.2f} - ${self.target_price_high:.2f} |
| **推荐入场价** | ${self.entry_price:.2f} |
| **止损价（风险控制）** | ${self.stop_loss_price:.2f} |
| **止盈价（获利了结）** | ${self.take_profit_price:.2f} |

### 概率评估

| 走势 | 概率 |
|------|------|
| 📈 **向上** | {self.upside_probability:.0f}% |
| 📉 **向下** | {self.downside_probability:.0f}% |
| ➡️ **盘整** | {self.sideways_probability:.0f}% |

### 关键触发事件

**看涨触发**: {self.bullish_catalyst}

**看跌触发**: {self.bearish_catalyst}

### ⚠️ 风险清单

"""
        for i, risk in enumerate(self.key_risks, 1):
            content += f"{i}. {risk}\n"
        
        return content

    def to_simple_text(self) -> str:
        """Format as simple one-liner for quick reference."""
        emoji_signal = {
            Signal.BUY: "📈",
            Signal.SELL: "📉",
            Signal.HOLD: "➡️",
        }[self.signal]
        
        emoji_confidence = {
            Confidence.HIGH: "🔴",
            Confidence.MEDIUM: "🟡",
            Confidence.LOW: "🟢",
        }[self.confidence]
        
        return (
            f"{emoji_signal} {self.signal.value} @ ${self.entry_price:.2f} "
            f"→ ${self.target_price_high:.2f} | "
            f"Stop: ${self.stop_loss_price:.2f} | "
            f"Confidence: {emoji_confidence} {self.confidence.value}"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "ticker": self.ticker,
            "signal": self.signal.value,
            "confidence": self.confidence.value,
            "target_price": {
                "low": self.target_price_low,
                "high": self.target_price_high,
            },
            "entry_price": self.entry_price,
            "stop_loss_price": self.stop_loss_price,
            "take_profit_price": self.take_profit_price,
            "probability": {
                "upside": self.upside_probability,
                "downside": self.downside_probability,
                "sideways": self.sideways_probability,
            },
            "catalysts": {
                "bullish": self.bullish_catalyst,
                "bearish": self.bearish_catalyst,
            },
            "key_risks": self.key_risks,
        }
