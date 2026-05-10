from __future__ import annotations

import asyncio
import logging
from typing import Any

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.http_client import fetch_json
from alphapulse.core.models import DataFreshness, DataSource

logger = logging.getLogger(__name__)

_SEC_BASE = "https://data.sec.gov"


async def lookup_cik(symbol: str, config: AlphaPulseConfig | None = None) -> str | None:
    """Convert a ticker symbol to a CIK number using the SEC API."""
    url = f"{_SEC_BASE}/submissions/CIK{symbol.upper()}.json"
    try:
        data = await fetch_json(url, config)
        return str(data.get("cik"))
    except Exception:
        logger.info(f"Could not look up CIK for {symbol} using submissions API")
        return None


async def get_company_facts(cik: str, config: AlphaPulseConfig | None = None) -> dict[str, Any] | None:
    """Fetch XBRL company facts from SEC EDGAR."""
    padded_cik = cik.zfill(10)
    url = f"{_SEC_BASE}/api/xbrl/companyfacts/CIK{padded_cik}.json"
    try:
        cfg = config or AlphaPulseConfig()
        headers = {"User-Agent": cfg.user_agent}
        data = await fetch_json(url, config)
        return data
    except Exception as e:
        logger.warning(f"Failed to fetch SEC company facts for CIK {cik}: {e}")
        return None


async def get_filing_list(
    cik: str,
    form_types: list[str] | None = None,
    limit: int = 20,
    config: AlphaPulseConfig | None = None,
) -> list[dict[str, Any]]:
    """Fetch recent filings from SEC EDGAR."""
    if form_types is None:
        form_types = ["10-K", "10-Q", "8-K"]
    padded_cik = cik.zfill(10)
    url = f"{_SEC_BASE}/submissions/CIK{padded_cik}.json"
    try:
        data = await fetch_json(url, config)
        filings = data.get("filings", {}).get("recent", {})
        results = []
        form_list = filings.get("form", [])
        date_list = filings.get("filingDate", [])
        acc_list = filings.get("accessionNumber", [])
        doc_list = filings.get("primaryDocument", [])

        for i in range(min(len(form_list), len(date_list), len(acc_list))):
            if len(results) >= limit:
                break
            if form_list[i] in form_types:
                results.append({
                    "form": form_list[i],
                    "filing_date": date_list[i],
                    "accession": acc_list[i],
                    "primary_document": doc_list[i] if i < len(doc_list) else None,
                })
        return results
    except Exception as e:
        logger.warning(f"Failed to fetch filings for CIK {cik}: {e}")
        return []
