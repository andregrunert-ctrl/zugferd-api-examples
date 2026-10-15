import requests
import os

API_URL = "https://e-rechnung-cloud.de/v1/invoice/validate"

if not os.path.exists("invoice_test.pdf"):
    print("ERROR: 'invoice_test.pdf' nicht gefunden. Bitte führe zuerst generate_invoice.py aus.")
    exit(1)

print("Sende PDF zur Validierung an die Live-API...")

with open("invoice_test.pdf", "rb") as f:
    response = requests.post(
        API_URL,
        headers={"X-API-Key": "zg_test_ouroboros_001"},
        files={"file": ("invoice_test.pdf", f, "application/pdf")}
    )

if response.status_code == 200:
    result = response.json()
    if result.get("is_valid"):
        print(f"SUCCESS: Validierung erfolgreich! Das PDF ist eine korrekte ZUGFeRD-Rechnung (Profil: {result.get('profile')}).")
    else:
        print("ERROR: Validierung fehlgeschlagen:")
        for err in result.get("errors", []):
            print(f"  - {err}")
else:
    print(f"ERROR: Server-Fehler: {response.text}")
