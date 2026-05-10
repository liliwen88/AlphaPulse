"""AlphaPulse — AI-powered global market intelligence for US equities, macro trends, and institutional flow analysis."""

__version__ = "0.1.0"

from alphapulse.client import AlphaPulse, AlphaPulseSync
from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.disclaimer import RISK_DISCLAIMER

__all__ = [
    "AlphaPulse",
    "AlphaPulseSync",
    "AlphaPulseConfig",
    "RISK_DISCLAIMER",
    "__version__",
]
