class ZugferdError(Exception):
    """Basis-Exception für alle ZUGFeRD API Client Fehler."""
    pass

class AuthenticationError(ZugferdError):
    """Wird geworfen, wenn der API-Key ungültig oder deaktiviert ist (HTTP 401)."""
    pass

class QuotaExceededError(ZugferdError):
    """Wird geworfen, wenn das Dokumenten-Guthaben aufgebraucht ist (HTTP 402)."""
    pass

class ValidationError(ZugferdError):
    """Wird geworfen, wenn die Rechnungsdaten fehlerhaft sind oder Rechenfehler enthalten (HTTP 422)."""
    def __init__(self, message: str, details=None):
        super().__init__(message)
        self.details = details

class RateLimitError(ZugferdError):
    """Wird geworfen, wenn das Anfrage-Limit überschritten wurde (HTTP 429)."""
    pass

class ApiError(ZugferdError):
    """Wird geworfen, wenn die API einen Server- oder Netzwerkfehler meldet (HTTP 5xx)."""
    def __init__(self, message: str, status_code: int = 500, response_text: str = ""):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.response_text = response_text
