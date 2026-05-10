from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.errors import NetworkError

_DEFAULT_CONFIG = AlphaPulseConfig()


def get_async_client(config: AlphaPulseConfig | None = None) -> httpx.AsyncClient:
    cfg = config or _DEFAULT_CONFIG
    return httpx.AsyncClient(
        timeout=httpx.Timeout(cfg.request_timeout_seconds),
        headers={"User-Agent": cfg.user_agent},
        http2=True,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
    )


@asynccontextmanager
async def async_client_context(
    config: AlphaPulseConfig | None = None,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    client = get_async_client(config)
    try:
        yield client
    finally:
        await client.aclose()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    reraise=True,
)
async def fetch_json(url: str, config: AlphaPulseConfig | None = None) -> dict:
    async with async_client_context(config) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    reraise=True,
)
async def fetch_text(url: str, config: AlphaPulseConfig | None = None) -> str:
    async with async_client_context(config) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
