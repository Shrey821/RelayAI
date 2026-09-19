"""
UMS Backend Server & REST API
Zero-dependency HTTP server delivering complete REST endpoints and static file serving for the SPA.
"""

from __future__ import annotations
import http.server
import socketserver
import json
import os
import sys
import mimetypes
import urllib.parse
from typing import Dict, Any, Optional

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.models import UMSPayload
from server.vault import UMSVault
from server.parsers import (
    parse_chatgpt_data, get_chatgpt_extraction_prompt,
    parse_claude_data, get_claude_extraction_prompt,
    parse_gemini_data, get_gemini_extraction_prompt,
    parse_raw_text
)
from server.adapters import (
    hydrate_for_claude, get_claude_verification_query,
    hydrate_for_chatgpt, get_chatgpt_verification_query,
    hydrate_for_gemini, get_gemini_verification_query,
    hydrate_for_ide
)
from server.diff_engine import compute_verification_diff
from server.sync_engine import (
    sync_to_anthropic, sync_to_openai, sync_to_filesystem, get_available_credentials
)

CLIENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client"))
vault = UMSVault()

class UMSRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Concise logging
        print(f"[{self.log_date_time_string()}] {format % args}")

    def _set_headers(self, status: int = 200, content_type: str = "application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def _read_json(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def _send_json(self, data: Any, status: int = 200):
        self._set_headers(status, "application/json; charset=utf-8")
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def _send_error(self, message: str, status: int = 400):
        self._send_json({"error": message, "status": status}, status)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # REST API Routes
        if path == "/api/health":
            self._send_json({"status": "healthy", "service": "UMS Engine", "version": "1.0.0"})
            return

        if path == "/api/prompts":
            self._send_json({
                "extraction_prompts": {
                    "chatgpt": get_chatgpt_extraction_prompt(),
                    "claude": get_claude_extraction_prompt(),
                    "gemini": get_gemini_extraction_prompt()
                },
                "verification_queries": {
                    "claude": get_claude_verification_query(),
                    "chatgpt": get_chatgpt_verification_query(),
                    "gemini": get_gemini_verification_query()
                }
            })
            return

        if path == "/api/profiles":
            profiles = vault.list_profiles()
            self._send_json({"profiles": profiles})
            return

        if path.startswith("/api/profiles/"):
            profile_id = path[len("/api/profiles/"):]
            p = vault.get_profile(profile_id)
            if p:
                self._send_json({"profile": p.to_dict()})
            else:
                self._send_error("Profile not found", 404)
            return

        if path == "/api/migrations":
            logs = vault.get_migration_logs()
            self._send_json({"migrations": logs})
            return

        if path == "/api/sync/status":
            self._send_json({"credentials": get_available_credentials()})
            return

        if path == "/api/handoff/demo":
            demo_chat = """User: I need to implement JWT refresh token rotation in Next.js 15 using the App Router and Edge runtime middleware.
Assistant: Great, we can implement this with jsonwebtoken. Here is an initial implementation...
User: Wait, jsonwebtoken crashes with "Module not found: Can't resolve 'crypto'". Next.js Edge middleware doesn't support Node.js native crypto!
Assistant: Ah, you are completely right. We decided to switch to the 'jose' library since it is built purely on Web Crypto standards compatible with the Edge runtime. Let's install jose.
User: Okay, installed jose. I wrote this middleware.ts file:
```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { jwtVerify, SignJWT } from 'jose'

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  try {
    const secret = new TextEncoder().encode(process.env.JWT_SECRET)
    await jwtVerify(token, secret)
    return NextResponse.next()
  } catch (err) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}
```
Assistant: That looks good, but right now if the access token expires, it redirects to /login immediately instead of checking the refresh token cookie!
User: Exactly, how do we catch the access token expiration error and use the refresh token cookie to issue a new access token without triggering an infinite redirect loop?"""
            self._send_json({
                "source": "chatgpt",
                "target": "claude",
                "demo_chat": demo_chat
            })
            return

        if path == "/api/demo-data":
            # Realistic preloaded dataset: ChatGPT memory export + Claude verification answer
            demo_chatgpt_raw = """### 1. IDENTITY & PROFILE
- Name: Alex Vance
- Role: Lead Full-Stack Architect
- Core Principles: Build minimal, resilient systems; prioritize developer ergonomics; clean functional boundaries.

### 2. TECH STACK & TOOLING
- Primary Languages: TypeScript, Python, SQL
- Frameworks: Next.js (App Router), React 19, Tailwind CSS, FastAPI
- Databases: PostgreSQL, SQLite, Redis
- OS: macOS (Apple Silicon), zsh shell

### 3. COMMUNICATION & RESPONSE PREFERENCES
- Tone: Highly direct, concise, senior engineer peer
- Verbosity: Minimalist to concise, skip pleasantries
- Code Preference: Strict TypeScript, idiomatic, fully working without placeholders
- Prohibitions:
  * Never write generic apology templates or robotic pleasantries
  * Never truncate essential code blocks or emit lazy '// rest of code here'
  * Avoid unnecessary conversational filler

### 4. CODING & ARCHITECTURE CONVENTIONS
- Coding Standards: TypeScript strict mode, zero `any` policy, explicit return types
- Architecture: Decoupled service layer, pure domain functions, zero unnecessary dependencies
- Testing: Thorough unit test coverage with clear assertions

### 5. ACTIVE PROJECTS & WORKING CONTEXT
- Current Primary Objective: Architect and ship the Universal Memory Schema (UMS) standard and bridge
- Active Projects:
  * Project: UMS Core Standard (active)
  * Decisions Finalized Today:
    - Finalized 3-tier context architecture (Tier 1: Identity, Tier 2: Active Context, Tier 3: Conversation)
    - Standardized on zero-dependency Python backend with SQLite local vault
  * Active Blockers: None currently, ready for end-to-end verification
  * Next Steps: Implement Claude memory import and verification loop

### 6. PERSONAL & LIFESTYLE NOTES
- Die-hard Arsenal FC supporter
- Enjoys specialty pour-over Ethiopian coffee
- Plays mechanical keyboard modding on weekends"""

            demo_claude_verification = """I have updated my memory with your developer profile and preferences:

- **Identity & Role**: You are Alex Vance, Lead Full-Stack Architect, focusing on minimal, resilient systems and clean architecture.
- **Tech Stack**:
  • Primary languages: TypeScript (strict mode, zero `any`), Python, and SQL.
  • Frameworks: Next.js (App Router), React 19, Tailwind CSS, and FastAPI.
  • Databases: PostgreSQL, SQLite, and Redis.
  • Environment: macOS Apple Silicon with zsh.
- **Communication & Working Style**:
  • Direct, concise senior engineer tone without pleasantries or apology templates.
  • Production-ready, fully written code without truncation or lazy placeholders.
- **Active Context**:
  • Currently working on the Universal Memory Schema (UMS) standard and bridge.
  • Architecture finalized today: 3-tier context architecture and zero-dependency backend.
  • Immediate priority: End-to-end Claude memory import verification.

*Note: In accordance with our professional memory policy, non-work lifestyle notes (such as football and coffee preferences) were not committed to long-term memory.*"""

            self._send_json({
                "source": "chatgpt",
                "target": "claude",
                "demo_chatgpt_raw": demo_chatgpt_raw,
                "demo_claude_verification": demo_claude_verification
            })
            return

        # Static File Serving (from client/ directory)
        clean_path = path.lstrip("/")
        if not clean_path:
            clean_path = "index.html"

        file_path = os.path.abspath(os.path.join(CLIENT_DIR, clean_path))

        # Security check to prevent directory traversal
        if not file_path.startswith(CLIENT_DIR) or not os.path.isfile(file_path):
            file_path = os.path.join(CLIENT_DIR, "index.html")

        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, content_type)
            self.wfile.write(content)
        except Exception as e:
            self._send_error(f"File read error: {str(e)}", 500)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            body = self._read_json()
        except Exception as e:
            self._send_error(f"Malformed JSON body: {str(e)}", 400)
            return

        if path == "/api/parse":
            source = body.get("source", "chatgpt").lower()
            text = body.get("text", "")
            name = body.get("name", "Imported Persona")

            if not text.strip():
                self._send_error("Field 'text' cannot be empty", 400)
                return

            if source == "chatgpt":
                payload = parse_chatgpt_data(text, name)
            elif source == "claude":
                payload = parse_claude_data(text, name)
            elif source == "gemini":
                payload = parse_gemini_data(text, name)
            else:
                payload = parse_raw_text(text, name)

            self._send_json({"payload": payload.to_dict()})
            return

        if path == "/api/hydrate":
            raw_payload = body.get("payload", {})
            target = body.get("target", "claude").lower()
            opts = body.get("options", {})

            inc_t1 = opts.get("include_tier1", True)
            inc_t2 = opts.get("include_tier2", True)
            inc_t3 = opts.get("include_tier3", False)
            filter_non_work = opts.get("filter_non_work", True)

            try:
                payload = UMSPayload.from_dict(raw_payload)
            except Exception as e:
                self._send_error(f"Invalid UMS payload: {str(e)}", 400)
                return

            if target == "claude":
                result = hydrate_for_claude(payload, inc_t1, inc_t2, inc_t3, filter_non_work)
            elif target == "chatgpt":
                result = hydrate_for_chatgpt(payload, inc_t1, inc_t2, inc_t3)
            elif target == "gemini":
                result = hydrate_for_gemini(payload, inc_t1, inc_t2, inc_t3)
            elif target in ("ide", "cursor", "claude_code"):
                result = {"target_provider": target, "files": hydrate_for_ide(payload)}
            else:
                self._send_error(f"Unknown target provider: {target}", 400)
                return

            self._send_json(result)
            return

        if path == "/api/verify":
            raw_payload = body.get("payload", {})
            verification_resp = body.get("verification_response", "")
            target_provider = body.get("target_provider", "claude").lower()
            save_log = body.get("save_log", True)

            if not verification_resp.strip():
                self._send_error("Verification response text cannot be empty", 400)
                return

            try:
                payload = UMSPayload.from_dict(raw_payload)
            except Exception as e:
                self._send_error(f"Invalid UMS payload: {str(e)}", 400)
                return

            diff = compute_verification_diff(payload, verification_resp, target_provider)

            if save_log:
                try:
                    log_id = vault.log_migration(
                        profile_id=payload.metadata.id,
                        source=payload.metadata.source_provider,
                        target=target_provider,
                        diff_result=diff
                    )
                    diff["migration_log_id"] = log_id
                except Exception:
                    pass

            self._send_json(diff)
            return

        if path == "/api/profiles":
            raw_payload = body.get("payload", {})
            desc = body.get("description", "Saved via UI")
            try:
                payload = UMSPayload.from_dict(raw_payload)
                pid = vault.save_profile(payload, desc)
                self._send_json({"id": pid, "status": "saved"})
            except Exception as e:
                self._send_error(f"Could not save profile: {str(e)}", 500)
            return

        if path == "/api/sync/filesystem":
            raw_payload = body.get("payload", {})
            target_dir = body.get("target_dir", ".")
            try:
                payload = UMSPayload.from_dict(raw_payload)
            except Exception as e:
                self._send_error(f"Invalid UMS payload: {str(e)}", 400)
                return
            result = sync_to_filesystem(payload, target_dir)
            self._send_json(result)
            return

        if path == "/api/sync/api":
            raw_payload = body.get("payload", {})
            target = body.get("target", "claude").lower()
            api_key = body.get("api_key")
            model = body.get("model")

            try:
                payload = UMSPayload.from_dict(raw_payload)
            except Exception as e:
                self._send_error(f"Invalid UMS payload: {str(e)}", 400)
                return

            if target == "claude":
                result = sync_to_anthropic(payload, api_key, model or "claude-3-5-sonnet-20241022")
            elif target == "chatgpt":
                result = sync_to_openai(payload, api_key, model or "gpt-4o")
            else:
                self._send_error(f"Target provider '{target}' not supported for direct API sync", 400)
                return

            if result.get("status") == "success" and "diff" in result:
                try:
                    vault.log_migration(
                        profile_id=payload.metadata.id,
                        source=payload.metadata.source_provider,
                        target=target,
                        diff_result=result["diff"]
                    )
                except Exception:
                    pass

            self._send_json(result)
            return

        if path == "/api/handoff/distill":
            raw_chat = body.get("raw_chat", "")
            source = body.get("source", "chatgpt").lower()
            target = body.get("target", "claude").lower()
            mode = body.get("mode", "full").lower()

            if not raw_chat.strip():
                self._send_error("Field 'raw_chat' cannot be empty", 400)
                return

            from server.chat_handoff import distill_chat_thread
            result = distill_chat_thread(raw_chat, source, target, mode=mode)
            self._send_json(result)
            return

        self._send_error(f"Endpoint not found: {path}", 404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/profiles/"):
            pid = path[len("/api/profiles/"):]
            success = vault.delete_profile(pid)
            if success:
                self._send_json({"status": "deleted", "id": pid})
            else:
                self._send_error("Profile not found or already deleted", 404)
            return
        self._send_error(f"Endpoint not found: {path}", 404)

def start_server(port: int = 8000, host: str = "127.0.0.1"):
    server_address = (host, port)
    # Enable address reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, UMSRequestHandler) as httpd:
        print(f"============================================================")
        print(f" UMS Engine & Web UI running at http://{host}:{port}")
        print(f" Universal Memory Schema v1.0.0 Server Ready")
        print(f"============================================================")
        httpd.serve_forever()

if __name__ == "__main__":
    start_server()
