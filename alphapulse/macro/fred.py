from __future__ import annotations

import logging

from alphapulse.core.config import AlphaPulseConfig

logger = logging.getLogger(__name__)


async def get_cpi_yoy(config: AlphaPulseConfig | None = None) -> float | None:
    """Get CPI YoY from FRED. Requires fredapi or FRED_API_KEY."""
    cfg = config or AlphaPulseConfig()
    if not cfg.fred_api_key:
        logger.info("No FRED API key configured, skipping CPI fetch")
        return None
    try:
        from fredapi import Fred

        fred = Fred(api_key=cfg.fred_api_key)
        series = fred.get_series("CPIAUCSL")
        if len(series) >= 13:
            return round((series.iloc[-1] / series.iloc[-13] - 1) * 100, 2)
        return None
    except ImportError:
        logger.info("fredapi not installed, skipping CPI. Install with: pip install alphapulse[fred]")
        return None
    except Exception as e:
        logger.warning(f"Failed to fetch CPI: {e}")
        return None


async def get_unemployment(config: AlphaPulseConfig | None = None) -> float | None:
    cfg = config or AlphaPulseConfig()
    if not cfg.fred_api_key:
        return None
    try:
        from fredapi import Fred

        fred = Fred(api_key=cfg.fred_api_key)
        series = fred.get_series("UNRATE")
        return round(float(series.iloc[-1]), 1) if len(series) > 0 else None
    except Exception as e:
        logger.warning(f"Failed to fetch unemployment: {e}")
        return None


async def get_gdp(config: AlphaPulseConfig | None = None) -> float | None:
    cfg = config or AlphaPulseConfig()
    if not cfg.fred_api_key:
        return None
    try:
        from fredapi import Fred

        fred = Fred(api_key=cfg.fred_api_key)
        series = fred.get_series("GDP")
        return round(float(series.iloc[-1]), 2) if len(series) > 0 else None
    except Exception as e:
        logger.warning(f"Failed to fetch GDP: {e}")
        return None


async def get_pce(config: AlphaPulseConfig | None = None) -> float | None:
    cfg = config or AlphaPulseConfig()
    if not cfg.fred_api_key:
        return None
    try:
        from fredapi import Fred

        fred = Fred(api_key=cfg.fred_api_key)
        series = fred.get_series("PCEPILFE")  # Core PCE
        if len(series) >= 13:
            return round((series.iloc[-1] / series.iloc[-13] - 1) * 100, 2)
        return None
    except Exception as e:
        logger.warning(f"Failed to fetch PCE: {e}")
        return None
