"""Shared configuration constants for AlphaPulse scripts."""

# ---- Market Data ----
DEFAULT_PERIOD = "6mo"
DEFAULT_INTERVAL = "1d"
YFINANCE_TIMEOUT = 15

# ---- Technical Indicators ----
DEFAULT_RSI_PERIOD = 14
DEFAULT_MACD_FAST = 12
DEFAULT_MACD_SLOW = 26
DEFAULT_MACD_SIGNAL = 9
DEFAULT_BOLLINGER_PERIOD = 20
DEFAULT_BOLLINGER_STD = 2
DEFAULT_SMA_PERIODS = [20, 50, 200]
DEFAULT_INDICATORS = ["rsi", "macd", "bollinger"]
SUPPORT_RESISTANCE_LOOKBACK = 20
SUPPORT_RESISTANCE_THRESHOLD = 0.02

# ---- News ----
DEFAULT_NEWS_DAYS = 7
DEFAULT_NEWS_SOURCES = ["reuters", "bloomberg", "yahoo"]
MAX_ARTICLES_PER_SOURCE = 10

# ---- Scoring Weights ----
WEIGHTS = {
    "technical": 0.30,
    "fundamental": 0.25,
    "news": 0.20,
    "sentiment": 0.15,
    "macro": 0.10,
}
CONVICTION_HIGH_THRESHOLD = 70
CONVICTION_MEDIUM_THRESHOLD = 40

# ---- Strategy ----
DEFAULT_POSITION_SIZE = 5.0
POSITION_SIZE_HIGH_CONVICTION = 8.0
POSITION_SIZE_LOW_CONVICTION = 2.0
STOP_LOSS_ATR_MULTIPLIER = 2.0
TAKE_PROFIT_ATR_MULTIPLIER = 3.0

# ---- Chart ----
CHART_FIGSIZE = (12, 8)
CHART_DPI = 150
CHART_FORMAT = "png"
CHART_STYLE = "charles"

# ---- Output ----
DEFAULT_OUTPUT_DIR = "./analysis_output"
