class AlphaPulseError(Exception):
    """Base exception for all AlphaPulse errors."""


class RateLimitError(AlphaPulseError):
    """Data source rate limit exceeded."""

    def __init__(self, source: str, retry_after_seconds: float | None = None) -> None:
        self.source = source
        self.retry_after_seconds = retry_after_seconds
        msg = f"Rate limit exceeded for {source}"
        if retry_after_seconds:
            msg += f" (retry after {retry_after_seconds:.0f}s)"
        super().__init__(msg)


class DataUnavailableError(AlphaPulseError):
    """Requested data is not available (ticker not found, missing field, etc.)."""

    def __init__(self, symbol: str, detail: str = "") -> None:
        self.symbol = symbol
        msg = f"Data unavailable for '{symbol}'"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class ConfigurationError(AlphaPulseError):
    """Missing or invalid configuration."""


class NetworkError(AlphaPulseError):
    """Network-level failure."""
