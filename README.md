# zugferd-client

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/zugferd-client/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.org/project/zugferd-client/)
[![Live API Health Check](https://github.com/andregrunert-ctrl/zugferd-api-examples/actions/workflows/health-check.yml/badge.svg)](https://github.com/andregrunert-ctrl/zugferd-api-examples/actions/workflows/health-check.yml)
[![Standard](https://img.shields.io/badge/Standard-EN%2016931%20%7C%20ZUGFeRD%202.2-blue)](https://e-rechnung-api.fly.dev)
[![Format](https://img.shields.io/badge/Format-PDF%2FA--3%20%2B%20Factur--X-purple)](https://e-rechnung-api.fly.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Der offizielle, leichtgewichtige Python-Client für die [E-Rechnung API](https://e-rechnung-api.fly.dev). 

Erstelle, verarbeite und validiere rechtskonforme elektronische Rechnungen nach **EN 16931** (ZUGFeRD 2.2 / Factur-X & XRechnung) mit nur 3 Zeilen Python-Code.

---

## 📦 Installation

```bash
pip install zugferd-client
```

*(Erfordert Python >= 3.8 und hat keine schweren C-Bibliotheks-Abhängigkeiten).*

---

## ⚡ Schnellstart

Dank des integrierten öffentlichen Test-Keys kannst du sofort ohne API-Key oder Registrierung loslegen:

```python
from zugferd_client import ZugferdClient

# Initialisierung (ohne Argumente wird automatisch der kostenlose Test-Key genutzt)
client = ZugferdClient()

# 1. ZUGFeRD PDF/A-3 Rechnung generieren
pdf_bytes = client.generate_invoice({
    "invoice_number": "RE-2026-001",
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
            "description": "Software-Entwicklung & Beratung",
            "quantity": 10,
            "unit_price": 120.00,
            "tax_rate_percent": 19
        }
    ]
}, output_path="rechnung.pdf")

print("✅ ZUGFeRD-Rechnung erfolgreich gespeichert!")

# 2. Vorhandene Rechnung auf EN 16931 Konformität validieren
report = client.validate("rechnung.pdf")
print("Ist konform:", report.is_valid)
print("Format:", report.format_detected)
```

---

## 🛠️ Funktionen & Methoden

### 1. Rechnungs-PDF generieren (`generate_invoice`)
Erstellt ein vollständiges, druckfertiges deutsches Rechnungs-PDF (PDF/A-3) mit unsichtbar eingebetteter `factur-x.xml` nach europäischer Norm EN 16931.

```python
pdf_bytes = client.generate_invoice(invoice_data, output_path="meine_rechnung.pdf")
```

### 2. ZUGFeRD in bestehendes Kunden-PDF einbetten (`embed_invoice`)
Hast du bereits ein fertiges PDF-Design (z. B. aus InDesign, WeasyPrint oder ReportLab)? Bette das EN 16931 XML verlustfrei ein:

```python
pdf_bytes = client.embed_invoice(
    pdf_file="vorlage.pdf",
    invoice_data=invoice_data,
    output_path="fertige_zugferd_rechnung.pdf"
)
```

### 3. XRechnung XML generieren (`generate_xrechnung`)
Erstellt eine reine EN 16931 XML-Datei (ohne visuelles PDF) – gesetzlich vorgeschrieben für Bundesbehörden und B2G in Deutschland.

```python
xml_string = client.generate_xrechnung(invoice_data, output_path="xrechnung.xml")
```

### 4. PDF oder XML validieren (`validate`)
Prüft PDF/A-3 Konformität, XMP-Metadaten, strukturelle Pflichtknoten und führt eine offizielle XSD-Schemaprüfung durch.

```python
result = client.validate("eingangsrechnung.pdf")

if result.is_valid:
    print(f"Gültige E-Rechnung ({result.format_detected})")
else:
    print("Fehler gefunden:", result.errors)
```

### 5. Guthaben abfragen (`get_billing_status`)
Fragt das verbleibende Dokumenten-Guthaben deines Keys ab:

```python
status = client.get_billing_status()
print(f"Verbleibende Dokumente: {status.credits_remaining}")
```

---

## 🔑 Eigener API-Key & Produktion

Für produktive Rechnungen ohne Test-Wasserzeichen übergibst du deinen persönlichen Key oder setzt die Umgebungsvariable `ZUGFERD_API_KEY`:

```bash
export ZUGFERD_API_KEY="zg_live_..."
```

```python
client = ZugferdClient(api_key="zg_live_...")
```

---

## 🌐 Nützliche Links

* **Live-Web-Validator:** [https://e-rechnung-api.fly.dev/validator](https://e-rechnung-api.fly.dev/validator) (Kostenlos Dateien im Browser prüfen)
* **Interaktive API-Dokumentation (Swagger):** [https://e-rechnung-api.fly.dev/docs](https://e-rechnung-api.fly.dev/docs)
* **Preise & Tarife:** [https://e-rechnung-api.fly.dev/#pricing](https://e-rechnung-api.fly.dev/#pricing)
* **Tutorials:**
  * [Python ZUGFeRD Guide](https://e-rechnung-api.fly.dev/tutorials/python-zugferd)
  * [Make.com No-Code Guide](https://e-rechnung-api.fly.dev/tutorials/make-zugferd)
  * [n8n Automation Guide](https://e-rechnung-api.fly.dev/tutorials/n8n-e-rechnung)
  * [PHP / Laravel Guide](https://e-rechnung-api.fly.dev/tutorials/php-zugferd)
  * [WooCommerce & Shopify Guide](https://e-rechnung-api.fly.dev/tutorials/woocommerce-e-rechnung)
  * [Power Automate Guide](https://e-rechnung-api.fly.dev/tutorials/power-automate-zugferd)

---

## 📄 Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details.
