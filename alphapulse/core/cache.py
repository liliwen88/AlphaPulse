from __future__ import annotations

import functools
import hashlib
import inspect
import json
import time
from collections import OrderedDict
from typing import Any, Callable


class TTLCache:
    """Thread-safe in-memory TTL cache with LRU eviction."""

    def __init__(self, maxsize: int = 512, default_ttl: int = 120) -> None:
        self._maxsize = maxsize
        self._default_ttl = default_ttl
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None
        expires_at, value = self._store[key]
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self._maxsize:
            self._store.popitem(last=False)
        ttl_seconds = ttl if ttl is not None else self._default_ttl
        expires_at = time.monotonic() + ttl_seconds
        self._store[key] = (expires_at, value)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        self._prune_expired()
        return len(self._store)

    def _prune_expired(self) -> None:
        now = time.monotonic()
        expired = [k for k, (exp, _) in self._store.items() if now > exp]
        for k in expired:
            del self._store[k]


_GLOBAL_CACHE = TTLCache()


def _make_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    raw = f"{func.__module__}.{func.__qualname__}:{args}:{sorted(kwargs.items())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def cached(ttl_seconds: int | None = None):
    """Decorator that caches function return values in the global TTL cache."""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = _make_cache_key(func, args, kwargs)
            result = _GLOBAL_CACHE.get(key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            _GLOBAL_CACHE.set(key, result, ttl=ttl_seconds)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = _make_cache_key(func, args, kwargs)
            result = _GLOBAL_CACHE.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            _GLOBAL_CACHE.set(key, result, ttl=ttl_seconds)
            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def get_global_cache() -> TTLCache:
    return _GLOBAL_CACHE
