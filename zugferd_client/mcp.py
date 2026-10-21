"""
Model Context Protocol (MCP) Server für ZUGFeRD 2.2, Factur-X & XRechnung (EN 16931).
Ermöglicht KI-Assistenten (Claude Desktop, Cursor, Antigravity, Cline) den direkten
Zugriff auf E-Rechnungs-Validierung, Leitweg-ID-Prüfung und PDF/XML-Generierung.
"""

import sys
import os
import json
import base64
import traceback
from typing import Dict, Any, Optional

from .client import ZugferdClient
from .leitweg import calculate_leitweg_id

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "zugferd-client"
SERVER_VERSION = "0.2.0"

TOOLS = [
    {
        "name": "calculate_leitweg_id",
        "description": "Prüft eine bestehende deutsche Leitweg-ID (BT-10) oder berechnet die 2-stellige Prüfziffer nach ISO/IEC 7064 MOD 97-10 und decodiert das Bundesland.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "leitweg_id": {
                    "type": "string",
                    "description": "Die zu prüfende oder zu berechnende Leitweg-ID (z. B. '04011000-1234512345-06' oder '04011000-1234512345')."
                }
            },
            "required": ["leitweg_id"]
        }
    },
    {
        "name": "validate_invoice",
        "description": "Validiert ein ZUGFeRD 2.2 / Factur-X PDF oder eine XRechnung XML nach DIN EN 16931 zu 100 % flüchtig im RAM (DSGVO-konform, kein Speichern auf Festplatte).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Optional: Absoluter oder relativer Dateipfad zur zu prüfenden PDF- oder XML-Datei auf dem System."
                },
                "file_base64": {
                    "type": "string",
                    "description": "Optional: Base64-kodierter Inhalt der PDF- oder XML-Datei."
                },
                "xml_content": {
                    "type": "string",
                    "description": "Optional: Reiner XML-Text einer XRechnung oder ZUGFeRD-Rechnung."
                },
                "filename": {
                    "type": "string",
                    "description": "Optionaler Dateiname (z. B. 'rechnung.pdf' oder 'xrechnung.xml'), falls file_base64 übergeben wird."
                }
            }
        }
    },
    {
        "name": "generate_zugferd_invoice",
        "description": "Generiert ein rechtskonformes ZUGFeRD 2.2 / Factur-X PDF/A-3 Dokument mit eingebettetem XML nach EN 16931 aus JSON-Daten.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "invoice_data": {
                    "type": "object",
                    "description": "Rechnungsdaten mit invoice_number, issue_date, currency, seller (name, street, zip_code, city, country, vat_id, iban), buyer, line_items."
                },
                "output_path": {
                    "type": "string",
                    "description": "Optional: Dateipfad, an dem das fertige PDF gespeichert werden soll (z. B. 'rechnung.pdf')."
                }
            },
            "required": ["invoice_data"]
        }
    },
    {
        "name": "generate_xrechnung",
        "description": "Generiert eine behördenkonforme XRechnung (reines UN/CEFACT CII XML) mit Leitweg-ID (BT-10) für deutsche Behörden (B2G).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "invoice_data": {
                    "type": "object",
                    "description": "Rechnungsdaten mit buyer_reference (Leitweg-ID), seller, buyer, line_items etc."
                },
                "output_path": {
                    "type": "string",
                    "description": "Optional: Dateipfad, an dem das XML gespeichert werden soll."
                }
            },
            "required": ["invoice_data"]
        }
    },
    {
        "name": "check_billing_status",
        "description": "Fragt das verbleibende Dokumenten-Guthaben und den Status des konfigurierten oder übergebenen API-Keys ab.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "Optionaler API-Key; standardmäßig wird der konfigurierte Key oder der öffentliche Test-Key zg_test_ouroboros_001 verwendet."
                }
            }
        }
    }
]


class MCPServer:
    def __init__(self, client: Optional[ZugferdClient] = None):
        self.client = client or ZugferdClient()

    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Notifications (kein id-Feld)
        if msg_id is None:
            return None

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    }
                }
            }

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS
                }
            }

        elif method == "resources/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"resources": []}}

        elif method == "prompts/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"prompts": []}}

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return self._call_tool(msg_id, tool_name, arguments)

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    def _call_tool(self, msg_id: Any, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if tool_name == "calculate_leitweg_id":
                raw_id = args.get("leitweg_id", "")
                res = calculate_leitweg_id(raw_id)
                return self._success(msg_id, json.dumps(res, ensure_ascii=False, indent=2))

            elif tool_name == "validate_invoice":
                file_path = args.get("file_path")
                file_base64 = args.get("file_base64")
                xml_content = args.get("xml_content")
                filename = args.get("filename")

                if file_path:
                    if not os.path.exists(file_path):
                        return self._error(msg_id, f"Datei existiert nicht: {file_path}")
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    fname = os.path.basename(file_path)
                elif file_base64:
                    file_bytes = base64.b64decode(file_base64)
                    fname = filename or "invoice.pdf"
                elif xml_content:
                    file_bytes = xml_content.encode("utf-8")
                    fname = "invoice.xml"
                else:
                    return self._error(msg_id, "Weder file_path, file_base64 noch xml_content übergeben.")

                val = self.client.validate(file_bytes, filename=fname)
                res_data = {
                    "is_valid": val.is_valid,
                    "format_detected": val.format_detected,
                    "errors": val.errors,
                    "norm": "DIN EN 16931"
                }
                return self._success(msg_id, json.dumps(res_data, ensure_ascii=False, indent=2))

            elif tool_name == "generate_zugferd_invoice":
                invoice_data = args.get("invoice_data")
                if not invoice_data:
                    return self._error(msg_id, "invoice_data ist erforderlich.")
                output_path = args.get("output_path")
                pdf_bytes = self.client.generate_invoice(invoice_data, output_path=output_path)
                msg = f"ZUGFeRD 2.2 / Factur-X PDF/A-3 erfolgreich erzeugt ({len(pdf_bytes)} Bytes)."
                if output_path:
                    msg += f" Gespeichert unter: {os.path.abspath(output_path)}"
                return self._success(msg_id, msg)

            elif tool_name == "generate_xrechnung":
                invoice_data = args.get("invoice_data")
                if not invoice_data:
                    return self._error(msg_id, "invoice_data ist erforderlich.")
                output_path = args.get("output_path")
                xml_text = self.client.generate_xrechnung(invoice_data, output_path=output_path)
                msg = f"XRechnung (CII XML) erfolgreich erzeugt ({len(xml_text)} Zeichen)."
                if output_path:
                    msg += f" Gespeichert unter: {os.path.abspath(output_path)}"
                return self._success(msg_id, xml_text if not output_path else msg)

            elif tool_name == "check_billing_status":
                api_key = args.get("api_key")
                client = ZugferdClient(api_key=api_key) if api_key else self.client
                status = client.get_billing_status()
                res_data = {
                    "api_key_preview": status.api_key_preview,
                    "credits_remaining": status.credits_remaining,
                    "is_active": status.is_active
                }
                return self._success(msg_id, json.dumps(res_data, ensure_ascii=False, indent=2))

            else:
                return self._error(msg_id, f"Unbekanntes Tool: {tool_name}")

        except Exception as e:
            return self._error(msg_id, f"Fehler bei Ausführung von {tool_name}: {str(e)}\n{traceback.format_exc()}")

    def _success(self, msg_id: Any, text: str) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ],
                "isError": False
            }
        }

    def _error(self, msg_id: Any, text: str) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ],
                "isError": True
            }
        }


def run_stdio_server():
    """Startet den MCP JSON-RPC stdio Server."""
    server = MCPServer()
    sys.stderr.write(f"[{SERVER_NAME} v{SERVER_VERSION}] MCP Server gestartet (stdio)...\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            sys.stderr.write(f"JSON Parse Error: {e}\n")
            sys.stderr.flush()
            continue

        resp = server.handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(f"{SERVER_NAME} v{SERVER_VERSION} - Model Context Protocol (MCP) Server")
        print("\nVerwendung:")
        print("  zugferd-mcp                 Startet den Server im stdio-Modus (für Claude Desktop / Cursor)")
        print("  python -m zugferd_client.mcp")
        print("\nKonfiguration für Claude Desktop (claude_desktop_config.json):")
        print('  "mcpServers": {')
        print('    "zugferd": {')
        print('      "command": "zugferd-mcp",')
        print('      "env": { "ZUGFERD_API_KEY": "zg_test_ouroboros_001" }')
        print('    }')
        print('  }')
        sys.exit(0)

    run_stdio_server()


if __name__ == "__main__":
    main()
