# AlphaPulse API Reference

## Installation

```bash
pip install -e .
# With optional dependencies:
pip install -e ".[all]"
```

## Quick Start

```python
from alphapulse import AlphaPulse

ap = AlphaPulse()

# Quote
quote = await ap.quote.get("AAPL")
print(quote.model_dump_json())

# Technical Analysis
tech = await ap.technical.analyze("AAPL")
print(tech.posture, tech.posture_detail)

# Fundamentals
fundamentals = await ap.fundamentals.analyze("AAPL")
print(f"Conviction: {fundamentals.conviction}")

# Market Hotspots
hotspots = await ap.hotspots.scan()
print(hotspots.summary)

# Macro Outlook
macro = await ap.macro.outlook()
print(macro.regime_summary)

# Institutional Flow
flow = await ap.flow.analyze("AAPL")
print(flow.summary)

# Risk Assessment
risk = await ap.risk.assess("AAPL", portfolio_value=100_000)
print(f"Risk Score: {risk.risk_score}")
```

## Configuration

```python
from alphapulse import AlphaPulseConfig

config = AlphaPulseConfig(
    cache_ttl_seconds=120,
    fred_api_key="your-key-here",  # optional
    log_level="INFO",
)
```

Environment variables (`ALPHAPULSE_` prefix):
- `ALPHAPULSE_FRED_API_KEY`
- `ALPHAPULSE_CACHE_TTL_SECONDS`
- `ALPHAPULSE_LOG_LEVEL`

## All Models Include

Every analysis result inherits from `BaseResult` and includes:
- `disclaimer: str` — Mandatory risk disclaimer (frozen, cannot be changed)
- `timestamp: datetime` — When data was fetched (UTC)
- `data_sources: list[str]` — Data provenance
- `model_dump_json()` — Serialize to JSON for AI agent consumption
