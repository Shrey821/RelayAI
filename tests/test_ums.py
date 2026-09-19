"""
Comprehensive Automated Unit Tests for UMS
Tests models, parsers, adapters, diff engine, and vault persistence.
"""

import unittest
import os
import tempfile
import json
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.models import (
    UMSPayload, Tier1Identity, Tier2ActiveContext, Profile, TechStack,
    CommunicationStyle, Conventions, PersonalTrivia, ActiveProject
)
from server.vault import UMSVault
from server.parsers import (
    parse_chatgpt_data, get_chatgpt_extraction_prompt,
    parse_claude_data, get_claude_extraction_prompt,
    parse_gemini_data, parse_raw_text
)
from server.adapters import (
    hydrate_for_claude, hydrate_for_chatgpt, hydrate_for_gemini, hydrate_for_ide,
    get_claude_verification_query, get_chatgpt_verification_query
)
from server.diff_engine import compute_verification_diff

class TestUMSModels(unittest.TestCase):
    def test_payload_roundtrip(self):
        payload = UMSPayload()
        payload.tier1_identity.profile.name = "Test Architect"
        payload.tier1_identity.profile.role = "Staff Systems Engineer"
        payload.tier1_identity.tech_stack.primary_languages = ["TypeScript", "Python"]
        payload.tier1_identity.tech_stack.frameworks = ["Next.js", "FastAPI"]
        payload.tier2_active_context.current_objective = "Launch UMS v1.0"
        
        as_dict = payload.to_dict()
        self.assertEqual(as_dict["version"], "1.0.0")
        self.assertEqual(as_dict["tier1_identity"]["profile"]["name"], "Test Architect")

        restored = UMSPayload.from_dict(as_dict)
        self.assertEqual(restored.tier1_identity.profile.name, "Test Architect")
        self.assertEqual(restored.tier1_identity.tech_stack.primary_languages, ["TypeScript", "Python"])
        self.assertEqual(restored.tier2_active_context.current_objective, "Launch UMS v1.0")

class TestParsers(unittest.TestCase):
    def test_chatgpt_parser(self):
        sample = """
        ### 1. IDENTITY & PROFILE
        - Role: Principal Architect
        - Background: Distributed systems

        ### 2. TECH STACK & TOOLING
        - Languages: TypeScript, Go
        - Frameworks: React, Next.js, Tailwind

        ### 3. COMMUNICATION
        - Tone: Direct and concise
        - Never write generic apology templates

        ### 5. ACTIVE CONTEXT
        - Current Objective: Complete database migration

        ### 6. PERSONAL
        - Enjoys espresso
        """
        payload = parse_chatgpt_data(sample)
        self.assertEqual(payload.tier1_identity.profile.role, "Principal Architect")
        self.assertIn("TypeScript", payload.tier1_identity.tech_stack.primary_languages)
        self.assertIn("Next.js", payload.tier1_identity.tech_stack.frameworks)
        self.assertTrue(any("apology" in p.lower() for p in payload.tier1_identity.communication_style.prohibitions))
        self.assertTrue(len(payload.tier1_identity.personal_trivia) > 0)
        self.assertFalse(payload.tier1_identity.personal_trivia[0].is_work_related)

    def test_claude_parser(self):
        sample = """
        - Objective: Build memory bridge
        - Languages: Python, Rust
        - Never use boilerplate code
        - Decided: Use SQLite for local storage
        """
        payload = parse_claude_data(sample)
        self.assertIn("Python", payload.tier1_identity.tech_stack.primary_languages)
        self.assertEqual(payload.tier2_active_context.current_objective, "Build memory bridge")

class TestAdapters(unittest.TestCase):
    def setUp(self):
        self.payload = UMSPayload()
        self.payload.tier1_identity.profile.role = "Lead Architect"
        self.payload.tier1_identity.tech_stack.primary_languages = ["TypeScript"]
        self.payload.tier1_identity.tech_stack.frameworks = ["Next.js"]
        self.payload.tier1_identity.communication_style.tone = "Concise and direct"
        self.payload.tier1_identity.communication_style.prohibitions = ["Never use filler words"]
        self.payload.tier1_identity.personal_trivia = [
            PersonalTrivia(topic="sports", value="Arsenal fan", is_work_related=False),
            PersonalTrivia(topic="timezone", value="UTC+5:30", is_work_related=True)
        ]
        self.payload.tier2_active_context.current_objective = "Ship cross-LLM bridge"

    def test_claude_adapter_work_filter(self):
        res = hydrate_for_claude(self.payload, filter_non_work=True)
        self.assertEqual(res["target_provider"], "claude")
        self.assertIn("TypeScript", res["import_text"])
        # Non-work trivia should be filtered out
        self.assertNotIn("Arsenal fan", res["import_text"])
        self.assertIn("UTC+5:30", res["import_text"])
        self.assertTrue(len(res["excluded_items"]) > 0)
        self.assertEqual(res["verification_query"], "I updated my memory. What did you learn about me?")

    def test_chatgpt_adapter_custom_instructions(self):
        res = hydrate_for_chatgpt(self.payload)
        self.assertEqual(res["target_provider"], "chatgpt")
        self.assertTrue(len(res["custom_instructions_box_1"]) <= 1500)
        self.assertTrue(len(res["custom_instructions_box_2"]) <= 1500)
        self.assertIn("Never use filler words", res["custom_instructions_box_2"])
        self.assertIn("Ship cross-LLM bridge", res["custom_instructions_box_1"])

    def test_ide_adapter(self):
        res = hydrate_for_ide(self.payload)
        self.assertIn("claude_md", res)
        self.assertIn("cursorrules", res)
        self.assertIn("TypeScript", res["claude_md"])
        self.assertIn("Never use filler words", res["cursorrules"])

class TestDiffEngine(unittest.TestCase):
    def test_verification_diff_calculation(self):
        payload = UMSPayload()
        payload.tier1_identity.tech_stack.primary_languages = ["TypeScript", "Python"]
        payload.tier1_identity.tech_stack.frameworks = ["Next.js"]
        payload.tier1_identity.communication_style.tone = "Concise and direct"
        payload.tier1_identity.personal_trivia = [
            PersonalTrivia(topic="sports", value="Arsenal supporter", is_work_related=False)
        ]
        payload.tier2_active_context.current_objective = "Build Universal Memory Schema"

        claude_response = """
        I have updated my memory:
        - Tech stack: TypeScript, Python, and Next.js.
        - Style: Concise and direct.
        - Objective: Building the Universal Memory Schema standard.
        Note: Lifestyle notes about sports teams were not saved.
        """

        diff = compute_verification_diff(payload, claude_response, target_provider="claude")
        self.assertTrue(diff["retention_score"] >= 80.0)
        self.assertTrue(diff["items_learned"] >= 3)
        self.assertEqual(diff["target_provider"], "claude")

        # Check that Arsenal supporter is detected as filtered
        trivia_entry = next((e for e in diff["diff_entries"] if "Arsenal" in e["item"]), None)
        self.assertIsNotNone(trivia_entry)
        self.assertEqual(trivia_entry["status"], "filtered")

class TestVaultPersistence(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.vault = UMSVault(db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_crud_and_snapshot(self):
        payload = UMSPayload()
        payload.metadata.name = "Vault Test Profile"
        payload.tier1_identity.profile.role = "Security Engineer"

        # Save profile
        pid = self.vault.save_profile(payload, "Initial commit")
        self.assertEqual(pid, payload.metadata.id)

        # Retrieve profile
        retrieved = self.vault.get_profile(pid)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.tier1_identity.profile.role, "Security Engineer")

        # List profiles
        profiles = self.vault.list_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["name"], "Vault Test Profile")

        # Update profile (creates snapshot)
        payload.tier1_identity.profile.role = "Chief Security Architect"
        self.vault.save_profile(payload, "Promoted")
        updated = self.vault.get_profile(pid)
        self.assertEqual(updated.tier1_identity.profile.role, "Chief Security Architect")

        # Log migration
        diff_data = {"retention_score": 95.0, "items_total": 10, "items_learned": 9, "items_adapted": 1, "items_filtered": 0}
        log_id = self.vault.log_migration(pid, "chatgpt", "claude", diff_data)
        self.assertTrue(log_id > 0)

        logs = self.vault.get_migration_logs(pid)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["retention_score"], 95.0)

        # Delete profile
        deleted = self.vault.delete_profile(pid)
        self.assertTrue(deleted)
        self.assertIsNone(self.vault.get_profile(pid))

class TestCLI(unittest.TestCase):
    def test_cli_prompt(self):
        import subprocess
        res = subprocess.run([sys.executable, "cli.py", "prompt", "--provider", "claude"],
                             capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        self.assertEqual(res.returncode, 0)
        self.assertIn("Claude Extraction Prompt", res.stdout)
        self.assertIn("What did you learn about me?", res.stdout)

    def test_cli_parse_and_hydrate(self):
        import subprocess
        sample = "Role: Staff Engineer\nLanguages: TypeScript, Go\nObjective: Launch Bridge"
        parse_proc = subprocess.run([sys.executable, "cli.py", "parse", "--source", "chatgpt"],
                                    input=sample, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        self.assertEqual(parse_proc.returncode, 0)
        data = json.loads(parse_proc.stdout)
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(data["tier1_identity"]["profile"]["role"], "Staff Engineer")

        # Save to temp file and hydrate
        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as f:
            f.write(parse_proc.stdout)
            temp_path = f.name

        try:
            hydrate_proc = subprocess.run([sys.executable, "cli.py", "hydrate", "--target", "claude", "-f", temp_path],
                                          capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
            self.assertEqual(hydrate_proc.returncode, 0)
            self.assertIn("CLAUDE MEMORY IMPORT TEXT", hydrate_proc.stdout)
            self.assertIn("Staff Engineer", hydrate_proc.stdout)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
