import json
import pytest
from zugferd_client.mcp import MCPServer, PROTOCOL_VERSION, SERVER_NAME, SERVER_VERSION

@pytest.fixture
def server():
    return MCPServer()

def test_mcp_initialize(server):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "TestClient", "version": "1.0.0"}
        }
    }
    resp = server.handle_request(req)
    assert resp["id"] == 1
    assert resp["result"]["protocolVersion"] == PROTOCOL_VERSION
    assert resp["result"]["serverInfo"]["name"] == SERVER_NAME
    assert "tools" in resp["result"]["capabilities"]

def test_mcp_ping(server):
    req = {"jsonrpc": "2.0", "id": 2, "method": "ping"}
    resp = server.handle_request(req)
    assert resp["id"] == 2
    assert resp["result"] == {}

def test_mcp_notification_no_response(server):
    req = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    resp = server.handle_request(req)
    assert resp is None

def test_mcp_tools_list(server):
    req = {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}}
    resp = server.handle_request(req)
    assert resp["id"] == 3
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "calculate_leitweg_id" in tool_names
    assert "validate_invoice" in tool_names
    assert "generate_zugferd_invoice" in tool_names
    assert "generate_xrechnung" in tool_names
    assert "check_billing_status" in tool_names

def test_mcp_call_calculate_leitweg_id(server):
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "calculate_leitweg_id",
            "arguments": {
                "leitweg_id": "04011000-1234512345-06"
            }
        }
    }
    resp = server.handle_request(req)
    assert resp["id"] == 4
    assert resp["result"]["isError"] is False
    content_text = resp["result"]["content"][0]["text"]
    data = json.loads(content_text)
    assert data["is_valid"] is True
    assert "Bremen" in data["region"]
    assert data["check"] == "06"

def test_mcp_call_check_billing_status(server):
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "check_billing_status",
            "arguments": {}
        }
    }
    resp = server.handle_request(req)
    assert resp["id"] == 5
    assert resp["result"]["isError"] is False
    content_text = resp["result"]["content"][0]["text"]
    data = json.loads(content_text)
    assert data["api_key_preview"].startswith("zg_test_")

def test_mcp_call_validate_invoice_xml(server):
    req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "validate_invoice",
            "arguments": {
                "xml_content": "<invalid>XML</invalid>"
            }
        }
    }
    resp = server.handle_request(req)
    assert resp["id"] == 6
    assert resp["result"]["isError"] is False
    content_text = resp["result"]["content"][0]["text"]
    data = json.loads(content_text)
    assert data["is_valid"] is False
    assert len(data["errors"]) > 0

def test_mcp_unknown_tool(server):
    req = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "non_existent_tool",
            "arguments": {}
        }
    }
    resp = server.handle_request(req)
    assert resp["id"] == 7
    assert resp["result"]["isError"] is True
    assert "Unbekanntes Tool" in resp["result"]["content"][0]["text"]

def test_mcp_unknown_method(server):
    req = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "some_unknown_method",
        "params": {}
    }
    resp = server.handle_request(req)
    assert resp["id"] == 8
    assert "error" in resp
    assert resp["error"]["code"] == -32601
