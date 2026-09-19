"""
Tests for UMS Active Target Memory Sync Engine
Verifies direct filesystem synchronization, credential inspection, and sync endpoints.
"""

import unittest
import os
import sys
import tempfile
import json
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.models import UMSPayload
from server.sync_engine import sync_to_filesystem, get_available_credentials
from tests.test_api import TestAPIHandler

class TestSyncEngine(unittest.TestCase):
    def setUp(self):
        self.payload = UMSPayload()
        self.payload.tier1_identity.profile.name = "Sync Architect"
        self.payload.tier1_identity.profile.role = "Principal Systems Engineer"
        self.payload.tier1_identity.tech_stack.primary_languages = ["TypeScript", "Python", "Rust"]
        self.payload.tier1_identity.tech_stack.frameworks = ["Next.js", "FastAPI"]
        self.payload.tier1_identity.communication_style.tone = "Concise and direct"
        self.payload.tier1_identity.communication_style.prohibitions = ["Never emit truncated code"]
        self.payload.tier2_active_context.current_objective = "Active Sync Engine Deployment"

    def test_filesystem_direct_sync(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            res = sync_to_filesystem(self.payload, temp_dir)
            self.assertEqual(res["status"], "success")
            self.assertEqual(len(res["written_files"]), 4)

            claude_md = os.path.join(temp_dir, "CLAUDE.md")
            cursorrules = os.path.join(temp_dir, ".cursorrules")
            windsurfrules = os.path.join(temp_dir, ".windsurfrules")
            agents_md = os.path.join(temp_dir, "AGENTS.md")

            self.assertTrue(os.path.isfile(claude_md))
            self.assertTrue(os.path.isfile(cursorrules))
            self.assertTrue(os.path.isfile(windsurfrules))
            self.assertTrue(os.path.isfile(agents_md))

            with open(claude_md, "r") as f:
                content = f.read()
                self.assertIn("Principal Systems Engineer", content)
                self.assertIn("TypeScript", content)
                self.assertIn("Never emit truncated code", content)

            with open(cursorrules, "r") as f:
                content = f.read()
                self.assertIn("TypeScript", content)
                self.assertIn("Never emit truncated code", content)

    def test_credentials_detection(self):
        creds = get_available_credentials()
        self.assertIn("anthropic", creds)
        self.assertIn("openai", creds)
        self.assertIn("gemini", creds)

    def test_api_sync_filesystem_endpoint(self):
        handler_tester = TestAPIHandler()
        with tempfile.TemporaryDirectory() as temp_dir:
            status, res = handler_tester._execute_request("POST", "/api/sync/filesystem", {
                "payload": self.payload.to_dict(),
                "target_dir": temp_dir
            })
            self.assertEqual(status, 200)
            self.assertEqual(res["status"], "success")
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "CLAUDE.md")))

    def test_api_sync_status_endpoint(self):
        handler_tester = TestAPIHandler()
        status, res = handler_tester._execute_request("GET", "/api/sync/status")
        self.assertEqual(status, 200)
        self.assertIn("credentials", res)

    def test_cli_sync_ide(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
                json.dump(self.payload.to_dict(), f)
                temp_payload_path = f.name

            try:
                proc = subprocess.run([
                    sys.executable, "cli.py", "sync", "--target", "ide",
                    "--file", temp_payload_path, "--path", temp_dir
                ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
                self.assertEqual(proc.returncode, 0)
                self.assertIn("Successfully wrote 4 rule files", proc.stdout)
                self.assertTrue(os.path.isfile(os.path.join(temp_dir, "CLAUDE.md")))
            finally:
                if os.path.exists(temp_payload_path):
                    os.remove(temp_payload_path)

if __name__ == "__main__":
    unittest.main()
