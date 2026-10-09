import io
import json
import os
from typing import Union, Optional, BinaryIO, Dict, Any
import requests

from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    ValidationError,
    RateLimitError,
    ApiError,
)
from .models import ValidationResult, BillingStatus

DEFAULT_BASE_URL = "https://e-rechnung-api.fly.dev"
DEFAULT_TEST_KEY = "zg_test_ouroboros_001"

class ZugferdClient:
    """
    Offizieller Python-Client für die E-Rechnung API.
    Unterstützt ZUGFeRD 2.2 / Factur-X (PDF/A-3) und XRechnung nach EN 16931.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30
    ):
        """
        Initialisiert den ZUGFeRD Client.
        
        :param api_key: Dein persönlicher API-Key. Standardmäßig wird der öffentliche
                        Test-Key verwendet, falls kein Key übergeben oder per
                        Umgebungsvariable ZUGFERD_API_KEY gesetzt ist.
        :param base_url: Die Basis-URL der API (Standard: https://e-rechnung-api.fly.dev).
        :param timeout: Timeout in Sekunden für HTTP-Anfragen (Standard: 30s).
        """
        self.api_key = api_key or os.getenv("ZUGFERD_API_KEY", DEFAULT_TEST_KEY)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    def _headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "User-Agent": "zugferd-client-python/0.1.0",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _handle_response(self, response: requests.Response) -> requests.Response:
        if response.status_code == 200:
            return response
        elif response.status_code == 401:
            raise AuthenticationError("API-Key ist ungültig oder fehlt.")
        elif response.status_code == 402:
            raise QuotaExceededError("Dokumenten-Guthaben ist aufgebraucht.")
        elif response.status_code == 422:
            try:
                err_data = response.json()
                detail = err_data.get("detail", response.text)
            except Exception:
                detail = response.text
            raise ValidationError(f"Ungültige Rechnungsdaten: {detail}", details=detail)
        elif response.status_code == 429:
            raise RateLimitError("Anfragelimit überschritten (Rate Limit).")
        else:
            raise ApiError(response.text, status_code=response.status_code, response_text=response.text)

    def generate_invoice(
        self,
        invoice_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generiert ein vollständiges ZUGFeRD 2.2 / Factur-X PDF/A-3 Dokument aus JSON-Daten.
        
        :param invoice_data: Dictionary mit Rechnungsdaten (gemäß EN 16931 Schema).
        :param output_path: Optionaler Dateipfad, an dem das PDF gespeichert werden soll.
        :return: Die rohen PDF-Bytes.
        """
        url = f"{self.base_url}/v1/invoice/generate"
        headers = self._headers({"Content-Type": "application/json"})
        response = self._session.post(
            url,
            headers=headers,
            json=invoice_data,
            timeout=self.timeout
        )
        self._handle_response(response)
        pdf_bytes = response.content

        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def embed_invoice(
        self,
        pdf_file: Union[str, bytes, BinaryIO],
        invoice_data: Union[Dict[str, Any], str],
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Bettet ZUGFeRD-XML in ein bestehendes Kunden-PDF ein und konvertiert es zu PDF/A-3.
        
        :param pdf_file: Dateipfad (str), Bytes oder dateiähnliches Objekt des Ausgangs-PDFs.
        :param invoice_data: Rechnungsdaten als Dict oder JSON-String.
        :param output_path: Optionaler Dateipfad, an dem das fertige PDF gespeichert werden soll.
        :return: Die rohen PDF-Bytes.
        """
        url = f"{self.base_url}/v1/invoice/embed"
        headers = self._headers()

        json_str = json.dumps(invoice_data) if isinstance(invoice_data, dict) else str(invoice_data)
        data = {"invoice_data": json_str}

        if isinstance(pdf_file, str):
            with open(pdf_file, "rb") as f:
                file_bytes = f.read()
            filename = os.path.basename(pdf_file)
        elif isinstance(pdf_file, bytes):
            file_bytes = pdf_file
            filename = "document.pdf"
        elif hasattr(pdf_file, "read"):
            file_bytes = pdf_file.read()
            filename = getattr(pdf_file, "name", "document.pdf")
        else:
            raise ValueError("Ungültiger Dateityp für pdf_file. Erwartet: Pfad, Bytes oder File-Objekt.")

        files = {"file": (filename, file_bytes, "application/pdf")}
        response = self._session.post(
            url,
            headers=headers,
            data=data,
            files=files,
            timeout=self.timeout
        )
        self._handle_response(response)
        pdf_bytes = response.content

        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes

    def generate_xrechnung(
        self,
        invoice_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Erstellt eine reine EN 16931 XML-Datei (XRechnung) ohne PDF.
        
        :param invoice_data: Dictionary mit Rechnungsdaten.
        :param output_path: Optionaler Dateipfad, an dem das XML gespeichert werden soll.
        :return: Das XML als UTF-8 String.
        """
        url = f"{self.base_url}/v1/invoice/xrechnung"
        headers = self._headers({"Content-Type": "application/json"})
        response = self._session.post(
            url,
            headers=headers,
            json=invoice_data,
            timeout=self.timeout
        )
        self._handle_response(response)
        xml_text = response.text

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_text)

        return xml_text

    def validate(
        self,
        file: Union[str, bytes, BinaryIO],
        filename: Optional[str] = None
    ) -> ValidationResult:
        """
        Validiert ein ZUGFeRD-PDF oder XML-Dokument auf Konformität mit der EN 16931 Norm.
        
        :param file: Dateipfad (str), Bytes oder dateiähnliches Objekt (.pdf oder .xml).
        :param filename: Optionaler Dateiname zur Formaterkennung, falls file als Bytes übergeben wird.
        :return: ValidationResult Instanz.
        """
        url = f"{self.base_url}/v1/invoice/validate"
        headers = self._headers()

        if isinstance(file, str):
            with open(file, "rb") as f:
                content = f.read()
            upload_name = filename or os.path.basename(file)
        elif isinstance(file, bytes):
            content = file
            upload_name = filename or "invoice.pdf"
        elif hasattr(file, "read"):
            content = file.read()
            upload_name = filename or getattr(file, "name", "invoice.pdf")
        else:
            raise ValueError("Ungültiger Dateityp für file. Erwartet: Pfad, Bytes oder File-Objekt.")

        content_type = "application/pdf" if upload_name.lower().endswith(".pdf") else "application/xml"
        files = {"file": (upload_name, content, content_type)}

        response = self._session.post(
            url,
            headers=headers,
            files=files,
            timeout=self.timeout
        )
        self._handle_response(response)
        data = response.json()

        return ValidationResult(
            is_valid=data.get("is_valid", False),
            format_detected=data.get("format_detected", "Unknown"),
            errors=data.get("errors", [])
        )

    def get_billing_status(self) -> BillingStatus:
        """
        Gibt das verbleibende Dokumenten-Guthaben und den Status des API-Keys zurück.
        """
        url = f"{self.base_url}/v1/invoice/billing/status"
        headers = self._headers()
        response = self._session.get(url, headers=headers, timeout=self.timeout)
        self._handle_response(response)
        data = response.json()

        return BillingStatus(
            api_key_preview=data.get("api_key_preview", ""),
            credits_remaining=data.get("credits_remaining", 0),
            is_active=data.get("is_active", False)
        )
