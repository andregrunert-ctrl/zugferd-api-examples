# ZUGFeRD / XRechnung Client (Python, Node.js &amp; No-Code)

[![Live API Health Check](https://github.com/andregrunert-ctrl/zugferd-api-examples/actions/workflows/health-check.yml/badge.svg)](https://github.com/andregrunert-ctrl/zugferd-api-examples/actions/workflows/health-check.yml)
[![Standard](https://img.shields.io/badge/Standard-EN%2016931%20%7C%20ZUGFeRD%202.2-blue)](https://e-rechnung-api.fly.dev)
[![Format](https://img.shields.io/badge/Format-PDF%2FA--3%20%2B%20Factur--X-purple)](https://e-rechnung-api.fly.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Offizielle Integrations-Beispiele und Vorlagen für die [E-Rechnung API](https://e-rechnung-api.fly.dev). 
Diese API wandelt strukturierte Rechnungsdaten (JSON) in rechtsgültige PDF/A-3-Dateien nach europäischer Norm **EN 16931** um.

## Schnellstart via cURL

Teste die API direkt im Terminal mit unserem öffentlichen Test-Key (`zg_test_ouroboros_001`):

```bash
curl -X POST https://e-rechnung-api.fly.dev/v1/invoice/generate \
  -H "X-API-Key: zg_test_ouroboros_001" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "RE-2024-001",
    "issue_date": "2024-10-09",
    "seller": {
      "name": "Demo Firma GmbH",
      "street": "Musterstraße 1", "city": "Berlin", "zip_code": "10115", "country": "DE",
      "vat_id": "DE123456789", "iban": "DE12345678901234567890"
    },
    "buyer": {
      "name": "Kunde AG",
      "street": "Zielweg 2", "city": "München", "zip_code": "80331", "country": "DE"
    },
    "line_items": [
      {"description": "API Nutzung", "quantity": 1, "unit_price": 100.0, "tax_rate_percent": 19}
    ]
  }' --output test_rechnung.pdf
```

## Python-Beispiel (requests)

Speichere das folgende Skript als `generate_invoice.py` ab und führe es aus:

```python
import requests
import json

API_URL = "https://e-rechnung-api.fly.dev/v1/invoice/generate"
API_KEY = "zg_test_ouroboros_001"

payload = {
    "invoice_number": "RE-2024-002",
    "issue_date": "2024-10-09",
    "seller": {
        "name": "Python Beispiel GmbH",
        "street": "Testweg 1", "city": "Hamburg", "zip_code": "20095", "country": "DE",
        "vat_id": "DE123456789", "iban": "DE12345678901234567890"
    },
    "buyer": {
        "name": "NodeJS Kunde",
        "street": "Kundenweg 5", "city": "Frankfurt", "zip_code": "60311", "country": "DE"
    },
    "line_items": [
        {"description": "Consulting", "quantity": 10, "unit_price": 150.0, "tax_rate_percent": 19}
    ]
}

response = requests.post(
    API_URL,
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json=payload
)

if response.status_code == 200:
    with open("invoice.pdf", "wb") as f:
        f.write(response.content)
    print("✅ PDF erfolgreich generiert und als invoice.pdf gespeichert.")
else:
    print(f"❌ Fehler: {response.text}")
```

## Node.js-Beispiel (fetch)

```javascript
const fs = require('fs');

async function generateInvoice() {
  const response = await fetch("https://e-rechnung-api.fly.dev/v1/invoice/generate", {
    method: "POST",
    headers: {
      "X-API-Key": "zg_test_ouroboros_001",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      invoice_number: "RE-JS-001",
      issue_date: "2024-10-09",
      seller: { name: "JS Corp", street: "Main St", city: "London", zip_code: "123", country: "GB", vat_id: "GB123", iban: "GB123456" },
      buyer: { name: "Kunde", street: "Nebenstr", city: "Berlin", zip_code: "10115", country: "DE" },
      line_items: [{ description: "Lizenz", quantity: 1, unit_price: 99.0, tax_rate_percent: 19 }]
    })
  });

  if (response.ok) {
    const buffer = await response.arrayBuffer();
    fs.writeFileSync('invoice.pdf', Buffer.from(buffer));
    console.log("✅ PDF erfolgreich generiert (invoice.pdf)!");
  } else {
    console.error("❌ Fehler:", await response.text());
  }
}

generateInvoice();
```

## Validierung
Bist du dir unsicher, ob dein generiertes PDF 100% rechtsgültig ist? 
Lade es einfach auf unserem **[kostenlosen Live-Validator](https://e-rechnung-api.fly.dev)** hoch und lass die XML-Struktur prüfen!
