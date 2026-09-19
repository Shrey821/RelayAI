# Universal Memory Schema (UMS) Specification

**Version:** 1.0.0  
**Status:** Living Standard / Production  
**License:** Apache 2.0 / Open Standard  

---

## 1. Abstract
When users transition between major AI models (such as ChatGPT, Claude, and Gemini), their most critical loss is **accumulated personalization, engineering memory, and active working context**. Previous solutions attempted either raw transcript dumping (which quickly inflates context windows with noisy, transient banter) or reverse-engineering private backend APIs (which violates provider Terms of Service and regularly breaks).

The **Universal Memory Schema (UMS)** defines an open, vendor-neutral intermediate representation (IR) and protocol for AI memory extraction, transformation, hydration, and closed-loop verification using officially documented provider interfaces.

---

## 2. The 3-Tier Context Architecture

UMS decomposes AI context into three distinct, decoupled tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: AI Identity & Long-Term Memory                                      │
│ • User Profile & Role (e.g., Senior Systems Architect)                      │
│ • Tech Stack (Languages, Frameworks, Toolchains, Databases)                 │
│ • Conventions (Coding standards, architectural patterns, test rules)        │
│ • Communication Style (Tone, verbosity, strict prohibitions)                │
│ • Personal Trivia & Lifestyle (Explicitly tagged: work vs non-work)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Active Working Context                                              │
│ • Current Primary Objective (e.g., Ship UMS Core Engine v1)                 │
│ • Active Projects & State (Decisions made today, active blockers, next steps│
│ • Ephemeral Constraints (e.g., "Do not alter the auth schema this session") │
├─────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Conversation Transcript (Optional / Ephemeral)                      │
│ • Raw turn-by-turn chat history                                             │
│ • Excluded by default during cross-provider migration to prevent token bloat │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The End-to-End Migration Lifecycle

A compliant UMS migration adheres to a 5-step closed loop:

1. **Extraction (Source AI)**:
   - Guided by official provider prompts.
   - For ChatGPT: Documented memory queries (*"What do you remember about me?"*) and Custom Instructions export.
   - For Claude: Anthropic's official migration export prompt.
2. **Normalization & Ingestion**:
   - The raw provider text is parsed and categorized into the 3-Tier UMS schema.
3. **Selective Pruning & Privacy Controls**:
   - The user selects which tiers and fields to retain.
   - Work vs. Personal filtering prevents irrelevant trivia from polluting target models that prioritize professional work (e.g., Claude's memory pipeline).
4. **Target Hydration**:
   - Formats the UMS payload specifically for the target platform:
     - **Anthropic Claude**: Formatted for `Settings → Memory → Start import` with work-focused structuring.
     - **OpenAI ChatGPT**: Formatted for the dual 1,500-char Custom Instructions fields + conversational memory injection.
     - **Google Gemini**: Formatted for Gemini Gems & Advanced System Instructions.
     - **Developer Toolchains**: Formatted for `CLAUDE.md`, `.cursorrules`, `.windsurfrules`, and `AGENTS.md`.
5. **Closed-Loop Verification & Semantic Diff**:
   - The user (or automated agent) submits the target provider's official verification prompt:
     - Claude: `"I updated my memory. What did you learn about me?"`
     - ChatGPT: `"What do you currently remember about me?"`
   - The UMS Verification Engine evaluates the response against the source UMS payload and produces a structured diff:
     - 🟢 **Learned / Retained**: Confirmed stored in target memory.
     - 🟡 **Consolidated / Adapted**: Conceptually retained under altered wording.
     - 🔴 **Filtered / Skipped**: Excluded (e.g. non-work personal trivia filtered out by Claude).

---

## 4. Provider Compatibility Matrix

| Provider | Ingestion Source | Target Format | Official Verification Query |
| :--- | :--- | :--- | :--- |
| **Claude (Anthropic)** | Migration Prompt Output | `Settings → Memory → Start import` text | `"I updated my memory. What did you learn about me?"` |
| **ChatGPT (OpenAI)** | Memory list & Custom Instructions | Custom Instructions (Dual 1500-char) & Memory Injection | `"What do you remember about me?"` |
| **Gemini (Google)** | Saved Info & Gems | Gems / System Instructions | `"What preferences do you have saved about me?"` |
| **Cursor / IDEs** | Workspace rules | `.cursorrules` / `CLAUDE.md` / `AGENTS.md` | In-editor prompt validation |

---

## 5. Security & Privacy Guarantees

1. **Local Vault Ownership**: All memory profiles are stored in an open SQLite database (`ums_vault.db`) or plaintext JSON on the user's device. No cloud transmission occurs without explicit user consent.
2. **Granular Exclusion**: Users can toggle off personal trivia, active tasks, or transcripts before hydration.
3. **Zero Secret Leakage**: API keys, credentials, and sensitive environment variables are sanitized during parsing.
