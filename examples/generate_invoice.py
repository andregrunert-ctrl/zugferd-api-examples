import requests

API_URL = "https://e-rechnung-api.fly.dev/v1/invoice/generate"
API_KEY = "zg_test_ouroboros_001"

payload = {
    "invoice_number": "RE-2024-002",
    "issue_date": "2024-10-09",
    "seller": {
        "name": "Python Beispiel GmbH",
        "street": "Testweg 1",
        "city": "Hamburg",
        "zip_code": "20095",
        "country": "DE",
        "vat_id": "DE123456789",
        "iban": "DE12345678901234567890"
    },
    "buyer": {
        "name": "NodeJS Kunde",
        "street": "Kundenweg 5",
        "city": "Frankfurt",
        "zip_code": "60311",
        "country": "DE"
    },
    "line_items": [
        {"description": "Consulting", "quantity": 10, "unit_price": 150.0, "tax_rate_percent": 19}
    ]
}

print("Sende Request an die Live-API...")
response = requests.post(
    API_URL,
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json=payload
)

if response.status_code == 200:
    with open("invoice_test.pdf", "wb") as f:
        f.write(response.content)
    print("SUCCESS: PDF erfolgreich empfangen und als invoice_test.pdf gespeichert.")
else:
    print(f"ERROR: Fehler: {response.text}")
