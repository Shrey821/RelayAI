#!/usr/bin/env python3
"""
Universal Memory Schema (UMS) - Command Line Interface
Headless cross-LLM memory extraction, hydration, and verification tool.
"""

import sys
import os
import argparse
import json

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from server.models import UMSPayload
from server.vault import UMSVault
from server.parsers import (
    parse_chatgpt_data, get_chatgpt_extraction_prompt,
    parse_claude_data, get_claude_extraction_prompt,
    parse_gemini_data, get_gemini_extraction_prompt,
    parse_raw_text
)
from server.adapters import (
    hydrate_for_claude, hydrate_for_chatgpt, hydrate_for_gemini, hydrate_for_ide,
    get_claude_verification_query, get_chatgpt_verification_query, get_gemini_verification_query
)
from server.diff_engine import compute_verification_diff

def main():
    parser = argparse.ArgumentParser(description="Universal Memory Schema (UMS) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: parse
    parse_cmd = subparsers.add_parser("parse", help="Parse raw memory dump into UMS JSON")
    parse_cmd.add_argument("--source", choices=["chatgpt", "claude", "gemini", "raw"], default="chatgpt", help="Source LLM provider")
    parse_cmd.add_argument("--file", "-f", help="Input file path (or reads stdin if omitted)")
    parse_cmd.add_argument("--name", default="CLI Persona", help="Profile name")

    # Command: hydrate
    hydrate_cmd = subparsers.add_parser("hydrate", help="Hydrate UMS JSON into target provider format")
    hydrate_cmd.add_argument("--target", choices=["claude", "chatgpt", "gemini", "ide"], default="claude", help="Target LLM provider")
    hydrate_cmd.add_argument("--file", "-f", required=True, help="Path to UMS JSON file")
    hydrate_cmd.add_argument("--no-work-filter", action="store_true", help="Disable Claude work-focus filter")

    # Command: verify
    verify_cmd = subparsers.add_parser("verify", help="Verify retention score against target model answer")
    verify_cmd.add_argument("--source-file", "-s", required=True, help="Original UMS JSON file")
    verify_cmd.add_argument("--response-file", "-r", required=True, help="Text file containing target AI's verification answer")
    verify_cmd.add_argument("--target", choices=["claude", "chatgpt", "gemini"], default="claude", help="Target provider verified")

    # Command: prompt
    prompt_cmd = subparsers.add_parser("prompt", help="Get official provider extraction and verification prompts")
    prompt_cmd.add_argument("--provider", choices=["chatgpt", "claude", "gemini"], default="chatgpt")

    # Command: vault
    vault_cmd = subparsers.add_parser("vault", help="Manage local SQLite memory vault")
    vault_cmd.add_argument("action", choices=["list", "show", "delete"], help="Vault action")
    vault_cmd.add_argument("--id", help="Profile ID for show/delete")

    # Command: sync
    sync_cmd = subparsers.add_parser("sync", help="Actively synchronize memory to target LLM or write IDE files directly")
    sync_cmd.add_argument("--target", choices=["claude", "chatgpt", "ide"], default="ide", help="Sync target")
    sync_cmd.add_argument("--file", "-f", required=True, help="Path to UMS JSON file")
    sync_cmd.add_argument("--path", "-p", default=".", help="Target project directory path for IDE sync")
    sync_cmd.add_argument("--api-key", help="API Key for Claude or OpenAI sync")
    sync_cmd.add_argument("--model", help="Target model name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "parse":
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = sys.stdin.read()

        if args.source == "chatgpt":
            payload = parse_chatgpt_data(content, args.name)
        elif args.source == "claude":
            payload = parse_claude_data(content, args.name)
        elif args.source == "gemini":
            payload = parse_gemini_data(content, args.name)
        else:
            payload = parse_raw_text(content, args.name)

        print(json.dumps(payload.to_dict(), indent=2))

    elif args.command == "hydrate":
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        payload = UMSPayload.from_dict(data)

        if args.target == "claude":
            res = hydrate_for_claude(payload, filter_non_work=not args.no_work_filter)
            print("================== CLAUDE MEMORY IMPORT TEXT ==================")
            print(res["import_text"])
            print("\n================== VERIFICATION PROMPT ========================")
            print(res["verification_query"])
        elif args.target == "chatgpt":
            res = hydrate_for_chatgpt(payload)
            print("=== BOX 1: WHAT CHATGPT SHOULD KNOW ABOUT YOU ===")
            print(res["custom_instructions_box_1"])
            print("\n=== BOX 2: HOW CHATGPT SHOULD RESPOND ===")
            print(res["custom_instructions_box_2"])
            print("\n=== MEMORY INJECTION PROMPT ===")
            print(res["memory_injection_prompt"])
        elif args.target == "gemini":
            res = hydrate_for_gemini(payload)
            print("=== GEMINI SYSTEM INSTRUCTION ===")
            print(res["system_instruction"])
        elif args.target == "ide":
            res = hydrate_for_ide(payload)
            print("=== CLAUDE.md ===")
            print(res["claude_md"])
            print("\n=== .cursorrules ===")
            print(res["cursorrules"])

    elif args.command == "verify":
        with open(args.source_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        payload = UMSPayload.from_dict(data)

        with open(args.response_file, "r", encoding="utf-8") as f:
            resp_text = f.read()

        diff = compute_verification_diff(payload, resp_text, args.target)

        print(f"\n=======================================================")
        print(f" UMS RETENTION AUDIT: {diff['retention_score']}% RETENTION")
        print(f" Total Items: {diff['items_total']} | Learned: {diff['items_learned']} | Adapted: {diff['items_adapted']} | Filtered: {diff['items_filtered']}")
        print(f"=======================================================\n")

        for entry in diff["diff_entries"]:
            status_icon = "🟢" if entry["status"] == "learned" else ("🟡" if entry["status"] == "adapted" else "🔴")
            print(f"{status_icon} [{entry['status'].upper():<8}] {entry['item']} ({entry['reason']})")

        if diff["suggestions"]:
            print("\n--- Suggestions ---")
            for s in diff["suggestions"]:
                print(f"• {s}")

    elif args.command == "prompt":
        if args.provider == "chatgpt":
            print("--- ChatGPT Extraction Prompt ---")
            print(get_chatgpt_extraction_prompt())
            print("\n--- ChatGPT Verification Query ---")
            print(get_chatgpt_verification_query())
        elif args.provider == "claude":
            print("--- Claude Extraction Prompt ---")
            print(get_claude_extraction_prompt())
            print("\n--- Claude Verification Query ---")
            print(get_claude_verification_query())
        elif args.provider == "gemini":
            print("--- Gemini Extraction Prompt ---")
            print(get_gemini_extraction_prompt())
            print("\n--- Gemini Verification Query ---")
            print(get_gemini_verification_query())

    elif args.command == "vault":
        vault = UMSVault()
        if args.action == "list":
            profiles = vault.list_profiles()
            if not profiles:
                print("Vault is empty.")
            for p in profiles:
                print(f"ID: {p['id']} | Name: {p['name']:<25} | Source: {p['source_provider']:<10} | Updated: {p['updated_at']}")
        elif args.action == "show":
            if not args.id:
                print("Error: --id required")
                sys.exit(1)
            p = vault.get_profile(args.id)
            if p:
                print(json.dumps(p.to_dict(), indent=2))
            else:
                print("Profile not found.")
        elif args.action == "delete":
            if not args.id:
                print("Error: --id required")
                sys.exit(1)
            if vault.delete_profile(args.id):
                print(f"Deleted profile {args.id}")
            else:
                print("Profile not found.")

    elif args.command == "sync":
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        payload = UMSPayload.from_dict(data)

        if args.target == "ide":
            from server.sync_engine import sync_to_filesystem
            res = sync_to_filesystem(payload, args.path)
            print(f"✓ {res['message']}")
            for wf in res["written_files"]:
                print(f"  • {wf['file']} -> {wf['path']} ({wf['bytes']} bytes)")
        elif args.target == "claude":
            from server.sync_engine import sync_to_anthropic
            print(f"Connecting to Anthropic API...")
            res = sync_to_anthropic(payload, api_key=args.api_key, model=args.model or "claude-3-5-sonnet-20241022")
            if res.get("status") == "success":
                print(f"✓ {res['message']}")
                diff = res["diff"]
                print(f"Retention Score: {diff['retention_score']}% (Learned: {diff['items_learned']}, Filtered: {diff['items_filtered']})")
            else:
                print(f"✕ Sync Error: {res.get('message')}")
        elif args.target == "chatgpt":
            from server.sync_engine import sync_to_openai
            print(f"Connecting to OpenAI API...")
            res = sync_to_openai(payload, api_key=args.api_key, model=args.model or "gpt-4o")
            if res.get("status") == "success":
                print(f"✓ {res['message']}")
                diff = res["diff"]
                print(f"Retention Score: {diff['retention_score']}% (Learned: {diff['items_learned']}, Filtered: {diff['items_filtered']})")
            else:
                print(f"✕ Sync Error: {res.get('message')}")

if __name__ == "__main__":
    main()
