from dataclasses import dataclass, field
from typing import List

@dataclass
class ValidationResult:
    """Ergebnis einer E-Rechnungs-Validierung."""
    is_valid: bool
    format_detected: str
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid

@dataclass
class BillingStatus:
    """Status und verbleibendes Dokumenten-Guthaben eines API-Keys."""
    api_key_preview: str
    credits_remaining: int
    is_active: bool
