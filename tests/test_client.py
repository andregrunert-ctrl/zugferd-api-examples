import os
import pytest
from zugferd_client import ZugferdClient, ValidationResult, BillingStatus

SAMPLE_INVOICE = {
    "invoice_number": "SDK-TEST-2026-001",
    "issue_date": "2026-10-09",
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
    assert client.base_url == "https://e-rechnung-api.fly.dev"

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
