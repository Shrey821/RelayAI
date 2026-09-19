# Universal Memory Schema (UMS)

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](spec/ums-v1.json)
[![Status](https://img.shields.io/badge/status-production--ready-emerald.svg)](spec/SPECIFICATION.md)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Zero-Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](run.py)

**The portable semantic bridge and open standard for cross-LLM memory migration, identity preservation, and verification across ChatGPT, Claude, Gemini, and developer IDEs.**

---

## 💡 The Core Problem

When developers switch between ChatGPT, Claude, and Gemini, their biggest loss isn't just raw conversation logs—it is **accumulated personalization, engineering preferences, and working context**:
- Your coding standards, strict TypeScript requirements, preferred frameworks, and toolchains.
- Your communication preferences (*"be concise", "skip pleasantries", "never emit lazy placeholders"*).
- The active context of what you are building right now (architecture decisions made today, active blockers).

Existing tools either dump bloated raw chat logs (which waste thousands of tokens on ephemeral banter) or attempt brittle DOM scrapers (which violate Terms of Service and regularly break).

### The UMS Breakthrough
UMS leverages **officially documented provider interfaces and migration prompts**:
1. **Anthropic Claude**: Official migration export prompt + native `Settings → Memory → Start import` ingest pipeline + officially documented verification query (`"I updated my memory. What did you learn about me?"`).
2. **OpenAI ChatGPT**: Documented memory inspection query (`"What do you remember about me?"`) + dual 1,500-char Custom Instructions.
3. **Google Gemini**: Saved Info & Gems system instructions.
4. **Developer IDEs**: Export directly into `CLAUDE.md`, `.cursorrules`, and `AGENTS.md`.

---

## 🏛️ The 3-Tier Context Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: AI Identity & Long-Term Memory (Persistent)                         │
│ • Tech stack (TypeScript strict, Next.js, Tailwind, FastAPI, PostgreSQL)   │
│ • Engineering conventions (testing rules, zero-any policy, clean design)    │
│ • Communication style (concise, senior engineer tone, strict prohibitions)  │
│ • Personal trivia (work-related vs non-work lifestyle notes)                │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Active Working Context (Ephemeral / Sprint-Level)                   │
│ • Current primary objective & milestone                                     │
│ • Active projects, decisions finalized today, active blockers               │
│ • Ephemeral constraints ("Do not alter auth schema during this migration")  │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Conversation Transcript (Optional / Pruned by Default)              │
│ • Raw turn-by-turn chat history (excluded by default to prevent bloat)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart (Zero External Dependencies)

UMS requires **only Python 3.10+**. It uses standard library networking and SQLite persistence—no `npm install`, no `pip install`, and zero dependency conflicts.

### 1. Launch the Full-Stack Web Application

```bash
python3 run.py
```
This automatically starts the local backend server and launches your browser at `http://127.0.0.1:8000`.

### 2. Run the 1-Click Test Drive
1. On the web dashboard, click **"⚡ Load 1-Click Demo"**.
2. Watch the end-to-end flow run in real time:
   - Ingests a real-world ChatGPT memory export.
   - Normalizes into the 3-Tier UMS specification.
   - Formats for Claude's native `Settings → Memory → Start import` pipeline.
   - Applies the Claude **Work-Focus Filter** (omits non-work football and hobby notes).
   - Computes the **Semantic Retention Diff** (🟢 16 Learned, 🟡 1 Adapted, 🔴 4 Filtered).

---

## 🛠️ Command Line Interface (CLI)

UMS comes with a headless CLI for terminal and script workflows:

```bash
# 1. View official provider extraction prompts
python3 cli.py prompt --provider chatgpt
python3 cli.py prompt --provider claude

# 2. Parse a raw memory dump into UMS JSON
python3 cli.py parse --source chatgpt < my_memory_dump.txt > persona.ums.json

# 3. Hydrate UMS JSON for Claude's memory import pipeline
python3 cli.py hydrate --target claude -f persona.ums.json

# 4. Hydrate for ChatGPT Custom Instructions & Memory Injection
python3 cli.py hydrate --target chatgpt -f persona.ums.json

# 5. Hydrate for Developer IDEs (CLAUDE.md & .cursorrules)
python3 cli.py hydrate --target ide -f persona.ums.json

# 6. Verify retention against target model's answer
python3 cli.py verify -s persona.ums.json -r claude_response.txt --target claude

# 7. List personas stored in your local SQLite vault
python3 cli.py vault list
```

---

## 🔍 Closed-Loop Verification & Semantic Diff Engine

After importing memory into Claude or ChatGPT, UMS prompts the target model with its official verification query:

> **Claude Verification Query:** `"I updated my memory. What did you learn about me?"`  
> **ChatGPT Verification Query:** `"What do you remember about me?"`

UMS then calculates a **Semantic Retention Diff**:
- 🟢 **Learned / Retained**: High semantic confidence; item is active in the target model's memory.
- 🟡 **Adapted / Consolidated**: Concept retained under merged or abstracted wording.
- 🔴 **Filtered / Omitted**: Skipped by the model (e.g. Claude's work filter purposely skipping non-work sports trivia).

---

## 📁 Project Structure

```
.
├── run.py                 # One-click web application launcher
├── cli.py                 # Full-featured command line interface
├── ums_vault.db           # Local SQLite database (profiles, snapshots, logs)
├── spec/
│   ├── ums-v1.json        # Official JSON Schema for UMS v1.0.0
│   ├── ums.d.ts           # TypeScript type definitions
│   └── SPECIFICATION.md   # Architectural & protocol specification
├── server/
│   ├── app.py             # Zero-dependency REST API & static server
│   ├── models.py          # UMS data models & serialization
│   ├── vault.py           # SQLite persistence layer
│   ├── diff_engine.py     # Verification & semantic retention engine
│   ├── parsers/           # ChatGPT, Claude, Gemini, and Raw parsers
│   └── adapters/          # Claude, ChatGPT, Gemini, and IDE hydrators
├── client/
│   ├── index.html         # Responsive Single Page Application
│   ├── styles.css         # Modern dark/light design system
│   └── app.js             # Reactive UI state & diff inspector
└── tests/
    ├── test_ums.py        # Core unit tests (parsers, adapters, diff, vault)
    └── test_api.py        # REST API integration tests
```

---

## 🧪 Running Automated Tests

Run the complete test suite:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

All 14 automated tests pass in < 0.2 seconds.

---

## 📄 License
Universal Memory Schema (UMS) is released under the **Apache 2.0 License**.
