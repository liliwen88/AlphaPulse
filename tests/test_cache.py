"""Tests for the TTLCache."""

import asyncio

import pytest

from alphapulse.core.cache import TTLCache, cached, get_global_cache


class TestTTLCache:
    def test_set_get(self):
        cache = TTLCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_ttl_expiry(self):
        cache = TTLCache(default_ttl=0)
        cache.set("key1", "value1", ttl=-1)
        assert cache.get("key1") is None

    def test_invalidate(self):
        cache = TTLCache()
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        cache = TTLCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert len(cache) == 0

    def test_lru_eviction(self):
        cache = TTLCache(maxsize=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3


class TestCachedDecorator:
    def test_sync_cached(self):
        call_count = 0

        @cached(ttl_seconds=60)
        def expensive(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        assert expensive(5) == 10
        assert call_count == 1
        assert expensive(5) == 10
        assert call_count == 1  # cached
        assert expensive(10) == 20
        assert call_count == 2  # different arg

    @pytest.mark.asyncio
    async def test_async_cached(self):
        call_count = 0

        @cached(ttl_seconds=60)
        async def expensive_async(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result = await expensive_async(5)
        assert result == 10
        assert call_count == 1
        result = await expensive_async(5)
        assert result == 10
        assert call_count == 1  # cached
