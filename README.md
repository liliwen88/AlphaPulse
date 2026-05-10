# AlphaPulse

AI-powered global market intelligence for US equities, macro trends, and institutional flow analysis.

> ⚠️ This project is for informational and educational purposes only. Not financial advice.

---

## English

**AlphaPulse** is a cross-platform Python SDK that delivers professional-grade US & global equity market intelligence. Designed to be consumed by any AI agent framework (Claude, ChatGPT, Gemini) via structured JSON output, it sources all data from authoritative overseas financial platforms — never from Chinese market data sources.

### Features

- **Quote** — Real-time price, volume, market cap, P/E, 52-week range (Yahoo Finance)
- **Fundamentals** — SEC filings, financial statements, DCF valuation, peer comparison
- **Technical** — SMA/EMA, MACD, RSI, Bollinger Bands, support/resistance, volume profile
- **Hotspots** — Sector rotation, top movers, unusual volume, thematic baskets
- **Macro** — FOMC calendar, CPI/PCE, yield curve, FedWatch probabilities, DXY, VIX, WTI
- **Flow** — Insider transactions, options flow, short interest, institutional holdings
- **Risk** — Historical/implied volatility, Beta, VaR, drawdown, position sizing

### Installation

```bash
pip install -e .
# With optional FRED API support:
pip install -e ".[fred]"
```

### Quick Start

```python
from alphapulse import AlphaPulse

ap = AlphaPulse()

# Get a quote
quote = await ap.quote.get("AAPL")
print(quote.model_dump_json(indent=2))

# Scan market hotspots
hotspots = await ap.hotspots.scan()
print(hotspots.summary)

# Full fundamental analysis
fundamentals = await ap.fundamentals.analyze("NVDA")
print(f"Conviction: {fundamentals.conviction}")

# Risk assessment with position sizing
risk = await ap.risk.assess("TSLA", portfolio_value=100_000)
print(f"Risk: {risk.risk_score}, Max Position: {risk.position_sizing.max_position_pct}%")
```

### AI Agent Integration

```python
def get_stock_quote(symbol: str) -> str:
    """Tool for AI agent: get real-time US stock quote."""
    ap = AlphaPulseSync()
    return ap.quote.get(symbol).model_dump_json()
```

Every result inherits from `BaseResult` and carries a mandatory `disclaimer` field.

### Data Sources

Yahoo Finance · SEC EDGAR · FRED · CME FedWatch · BLS · Bloomberg · Reuters · CNBC · MarketWatch · TradingView · Finviz · WhaleWisdom · Dataroma · Morningstar · Macrotrends · ETF.com · Barchart · Market Chameleon

---

## 中文

**AlphaPulse** 是一个跨平台 Python SDK，提供专业级美股及全球证券市场情报（非中国市场）。设计为任意 AI Agent 框架（Claude、ChatGPT、Gemini）可直接调用，所有数据均来自海外权威金融平台。

### 功能模块

- **行情速览** — 实时价格、成交量、市值、PE、52周高低
- **深度基本面** — SEC 财报、DCF 估值、同业对比
- **技术分析** — 均线、MACD、RSI、布林带、支撑阻力、量价分析
- **市场热点** — 板块轮动、涨跌幅榜、异常成交量、主题篮子
- **宏观分析** — FOMC、CPI、收益率曲线、FedWatch、DXY、VIX、WTI
- **机构流分析** — 内部人交易、期权异动、做空比率
- **风险管理** — 波动率、Beta、VaR、回撤、头寸规模建议

### 安装

```bash
pip install -e .
pip install -e ".[all]"  # 包含全部可选依赖
```

### AI Agent 集成

```python
def get_stock_quote(symbol: str) -> str:
    """AI Agent 工具函数：获取实时美股行情"""
    ap = AlphaPulseSync()
    return ap.quote.get(symbol).model_dump_json()
```

所有分析结果均继承 `BaseResult`，强制包含 `disclaimer` 风控声明。

---

## 日本語

**AlphaPulse** はクロスプラットフォームの Python SDK であり、プロフェッショナルグレードの米国株・グローバル市場インテリジェンスを提供します。あらゆる AI エージェントフレームワーク（Claude、ChatGPT、Gemini）から直接利用可能で、すべてのデータは海外の信頼できる金融プラットフォームから取得しています。

### 機能

- **株価** — リアルタイム価格、出来高、時価総額、PER、52週高安
- **ファンダメンタル** — SEC 提出書類、DCF バリュエーション、競合比較
- **テクニカル** — 移動平均、MACD、RSI、ボリンジャーバンド、支持/抵抗線
- **ホットスポット** — セクターローテーション、値上がり/値下がり、異常出来高
- **マクロ** — FOMC、CPI、イールドカーブ、FedWatch、DXY、VIX、WTI
- **フロー** — インサイダー取引、オプションフロー、空売り比率
- **リスク** — ボラティリティ、ベータ、VaR、ドローダウン、ポジションサイジング

### インストール

```bash
pip install -e .
pip install -e ".[all]"
```

### AI エージェント統合

```python
def get_stock_quote(symbol: str) -> str:
    """AIエージェントツール: 米国株のリアルタイム株価を取得"""
    ap = AlphaPulseSync()
    return ap.quote.get(symbol).model_dump_json()
```

すべての分析結果は `BaseResult` を継承し、`disclaimer` フィールドを必須で含みます。

---

## Project Structure

```text
AlphaPulse/
├── alphapulse/
│   ├── __init__.py
│   ├── client.py              # AlphaPulse / AlphaPulseSync facade
│   ├── core/                   # Config, models, cache, HTTP client
│   ├── quote/                  # Real-time quotes
│   ├── fundamentals/           # Deep fundamental analysis
│   ├── technical/              # Technical indicators & levels
│   ├── hotspots/               # Market scanning & sector rotation
│   ├── macro/                  # Economic calendar & macro regime
│   ├── flow/                   # Institutional flow & insider tracking
│   └── risk/                   # Risk assessment & position sizing
├── tests/
├── examples/
├── docs/
├── pyproject.toml
├── CLAUDE.md
├── README.md
└── LICENSE
```

## License

MIT
