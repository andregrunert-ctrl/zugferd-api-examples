"""
Offizieller Python-Client für die E-Rechnung API (ZUGFeRD 2.2 / Factur-X & XRechnung).
"""

from .client import ZugferdClient
from .models import ValidationResult, BillingStatus
from .leitweg import calculate_leitweg_id, LEITWEG_REGIONS
from .exceptions import (
    ZugferdError,
    AuthenticationError,
    QuotaExceededError,
    ValidationError,
    RateLimitError,
    ApiError,
)

__version__ = "0.2.0"
__all__ = [
    "ZugferdClient",
    "ValidationResult",
    "BillingStatus",
    "calculate_leitweg_id",
    "LEITWEG_REGIONS",
    "ZugferdError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "RateLimitError",
    "ApiError",
]
