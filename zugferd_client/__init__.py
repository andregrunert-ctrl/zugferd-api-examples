"""
Offizieller Python-Client für die E-Rechnung API (ZUGFeRD 2.2 / Factur-X & XRechnung).
"""

from .client import ZugferdClient
from .models import ValidationResult, BillingStatus
from .exceptions import (
    ZugferdError,
    AuthenticationError,
    QuotaExceededError,
    ValidationError,
    RateLimitError,
    ApiError,
)

__version__ = "0.1.0"
__all__ = [
    "ZugferdClient",
    "ValidationResult",
    "BillingStatus",
    "ZugferdError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "RateLimitError",
    "ApiError",
]
