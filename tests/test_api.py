"""
In-Memory Integration Tests for UMS HTTP REST API Handler
Tests HTTP handler request dispatching without opening external TCP sockets.
Runs cleanly in sandboxed environments.
"""

import unittest
import json
import io
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.app import UMSRequestHandler

class DummyServer:
    server_address = ("127.0.0.1", 8000)

class MockRequest:
    def __init__(self, raw_http_bytes: bytes):
        self.rfile = io.BytesIO(raw_http_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, b):
        self.wfile.write(b)

class TestAPIHandler(unittest.TestCase):
    def _execute_request(self, method: str, path: str, body_dict: dict = None):
        headers = [f"{method} {path} HTTP/1.1", "Host: localhost"]
        body_bytes = b""
        if body_dict is not None:
            body_bytes = json.dumps(body_dict).encode("utf-8")
            headers.append("Content-Type: application/json")
            headers.append(f"Content-Length: {len(body_bytes)}")
        headers.append("\r\n")

        raw_req = "\r\n".join(headers).encode("utf-8") + body_bytes
        mock_req = MockRequest(raw_req)

        # Instantiate handler without binding a socket
        handler = UMSRequestHandler(mock_req, ("127.0.0.1", 12345), DummyServer())
        
        response_bytes = mock_req.wfile.getvalue()
        parts = response_bytes.split(b"\r\n\r\n", 1)
        header_text = parts[0].decode("utf-8")
        body_text = parts[1].decode("utf-8") if len(parts) > 1 else ""

        status_code = int(header_text.split(" ")[1])
        data = None
        if "application/json" in header_text:
            try:
                data = json.loads(body_text)
            except Exception:
                data = body_text
        return status_code, data

    def test_health_endpoint(self):
        status, data = self._execute_request("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["version"], "1.0.0")

    def test_prompts_endpoint(self):
        status, data = self._execute_request("GET", "/api/prompts")
        self.assertEqual(status, 200)
        self.assertIn("chatgpt", data["extraction_prompts"])
        self.assertIn("claude", data["extraction_prompts"])
        self.assertIn("claude", data["verification_queries"])

    def test_demo_data_endpoint(self):
        status, data = self._execute_request("GET", "/api/demo-data")
        self.assertEqual(status, 200)
        self.assertIn("Alex Vance", data["demo_chatgpt_raw"])
        self.assertIn("TypeScript", data["demo_claude_verification"])

    def test_parse_and_hydrate_flow(self):
        # 1. Fetch demo data
        _, demo = self._execute_request("GET", "/api/demo-data")

        # 2. Parse into UMS
        status, parse_res = self._execute_request("POST", "/api/parse", {
            "source": "chatgpt",
            "text": demo["demo_chatgpt_raw"],
            "name": "Integration Persona"
        })
        self.assertEqual(status, 200)
        payload = parse_res["payload"]
        self.assertEqual(payload["version"], "1.0.0")

        # 3. Hydrate for Claude
        status, hydrate_res = self._execute_request("POST", "/api/hydrate", {
            "payload": payload,
            "target": "claude",
            "options": {"filter_non_work": True}
        })
        self.assertEqual(status, 200)
        self.assertEqual(hydrate_res["target_provider"], "claude")
        self.assertIn("TypeScript", hydrate_res["import_text"])
        self.assertTrue(len(hydrate_res["excluded_items"]) > 0)

        # 4. Verify against Claude verification response
        status, verify_res = self._execute_request("POST", "/api/verify", {
            "payload": payload,
            "verification_response": demo["demo_claude_verification"],
            "target_provider": "claude",
            "save_log": True
        })
        self.assertEqual(status, 200)
        self.assertTrue(verify_res["retention_score"] >= 80.0)
        self.assertTrue(verify_res["items_learned"] >= 10)

        # 5. Check migration logs
        status, logs_res = self._execute_request("GET", "/api/migrations")
        self.assertEqual(status, 200)
        self.assertTrue(len(logs_res["migrations"]) > 0)

if __name__ == "__main__":
    unittest.main()
