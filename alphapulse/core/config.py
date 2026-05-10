from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AlphaPulseConfig:
    """Configuration for AlphaPulse SDK, loaded from env vars prefixed with ALPHAPULSE_."""

    cache_ttl_seconds: int = 120
    fundamentals_ttl_seconds: int = 21600
    macro_ttl_seconds: int = 3600
    max_retries: int = 3
    request_timeout_seconds: float = 30.0
    fred_api_key: str | None = None
    user_agent: str = "AlphaPulse/0.1.0"
    cache_backend: Literal["memory", "disk"] = "memory"
    log_level: str = "WARNING"

    def __post_init__(self) -> None:
        self._load_from_env()

    def _load_from_env(self) -> None:
        for field_name in self.__dataclass_fields__:
            env_key = f"ALPHAPULSE_{field_name.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                target_type = type(getattr(self, field_name))
                if target_type is bool:
                    setattr(self, field_name, env_val.lower() in ("1", "true", "yes"))
                elif target_type is int:
                    setattr(self, field_name, int(env_val))
                elif target_type is float:
                    setattr(self, field_name, float(env_val))
                else:
                    setattr(self, field_name, env_val)
