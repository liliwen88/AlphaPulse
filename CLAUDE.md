# AlphaPulse

AI-powered global market intelligence for US equities, macro trends, and institutional flow analysis.

## Project Identity

AlphaPulse is a cross-platform Python SDK that provides professional US & global equity market analysis. It is designed to be consumed by any AI agent framework (Claude, ChatGPT, Gemini) via structured JSON output.

## Tech Stack

- Python >= 3.10
- Built with: yfinance, pandas, numpy, pydantic v2, httpx
- Package manager: pip / hatchling
- Testing: pytest, pytest-asyncio, vcrpy
- Linting: ruff, mypy (strict)

## Conventions

- All data sourced from authoritative overseas financial platforms only
- Never use or reference Chinese market data sources
- All financial metrics use standard English abbreviations
- Every analysis result model inherits from `BaseResult` and carries a mandatory `disclaimer` field
- Async-first architecture with lazy-loaded service modules
- Pure numpy/pandas for technical indicators — no external TA library dependency
- Pydantic v2 models for all return types — JSON serialization is `.model_dump_json()`
- Environment config via `ALPHAPULSE_` prefixed variables

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check alphapulse/
mypy alphapulse/
```
