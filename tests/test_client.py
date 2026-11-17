import os
import pytest
from zugferd_client import ZugferdClient, ValidationResult, BillingStatus

os.environ["ZUGFERD_INTERNAL_CI"] = "1"

SAMPLE_INVOICE = {
    "invoice_number": "SDK-TEST-2026-001",
    "issue_date": "2026-10-09",
    "buyer_reference": "04011000-1234512345-06",
    "seller": {
        "name": "Muster GmbH",
        "street": "Hauptstraße 1",
        "city": "Berlin",
        "zip_code": "10115",
        "country": "DE",
        "vat_id": "DE123456789",
        "iban": "DE12345678901234567890"
    },
    "buyer": {
        "name": "Kunden AG",
        "street": "Nebenstraße 2",
        "city": "München",
        "zip_code": "80331",
        "country": "DE"
    },
    "line_items": [
        {
            "description": "SDK Integration Testing",
            "quantity": 1,
            "unit_price": 49.00,
            "tax_rate_percent": 19
        }
    ]
}

def test_client_init():
    client = ZugferdClient()
    assert client.api_key == "zg_test_ouroboros_001"
    assert client.base_url == "https://e-rechnung-cloud.de"

def test_generate_invoice_and_validate():
    client = ZugferdClient()
    
    # 1. Generate PDF
    pdf_bytes = client.generate_invoice(SAMPLE_INVOICE)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
    
    # 2. Validate PDF
    result = client.validate(pdf_bytes, filename="rechnung.pdf")
    assert isinstance(result, ValidationResult)
    assert result.is_valid is True
    assert "PDF" in result.format_detected
    assert len(result.errors) == 0

def test_validate_invalid_xml():
    client = ZugferdClient()
    invalid_xml = b"<root><invalid>Data</invalid></root>"
    result = client.validate(invalid_xml, filename="bad.xml")
    assert result.is_valid is False
    assert len(result.errors) > 0

def test_generate_xrechnung():
    client = ZugferdClient()
    xml_str = client.generate_xrechnung(SAMPLE_INVOICE)
    assert isinstance(xml_str, str)
    assert "CrossIndustryInvoice" in xml_str

def test_get_billing_status():
    client = ZugferdClient()
    status = client.get_billing_status()
    assert isinstance(status, BillingStatus)
    assert status.api_key_preview.startswith("zg_test_")
    assert status.is_test_tier is True
    assert status.upgrade_url == "https://e-rechnung-cloud.de/#pricing"


def test_free_tier_warning_and_upgrade_links_in_errors(monkeypatch):
    import warnings
    import requests
    from zugferd_client.exceptions import AuthenticationError, QuotaExceededError, RateLimitError

    monkeypatch.delenv("ZUGFERD_INTERNAL_CI", raising=False)
    monkeypatch.delenv("ZUGFERD_API_KEY", raising=False)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        c = ZugferdClient()
    assert any("https://e-rechnung-cloud.de" in str(w.message) for w in caught)

    for code, exc_cls in [(401, AuthenticationError), (402, QuotaExceededError), (429, RateLimitError)]:
        resp = requests.Response()
        resp.status_code = code
        resp._content = b'{"detail":"limit"}'
        with pytest.raises(exc_cls) as exc_info:
            c._handle_response(resp)
        assert "https://e-rechnung-cloud.de/#pricing" in str(exc_info.value)
