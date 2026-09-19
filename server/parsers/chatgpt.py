"""
ChatGPT Ingestion Parser & Extraction Prompt Generator
Extracts ChatGPT memories, Custom Instructions, and conversational memory dumps into UMS v1.0.0.
"""

from __future__ import annotations
import re
import json
from typing import Dict, Any, List, Optional
from server.models import (
    UMSPayload, UMSMetadata, Tier1Identity, Tier2ActiveContext,
    Profile, TechStack, CommunicationStyle, Conventions, PersonalTrivia, ActiveProject
)

def get_chatgpt_extraction_prompt() -> str:
    """Returns the official extraction prompt to send to ChatGPT."""
    return (
        "Please extract all long-term memories, user preferences, and active context you have stored about me. "
        "Format your answer clearly with these exact section headings:\n\n"
        "### 1. IDENTITY & PROFILE\n"
        "- My name / handle / role\n"
        "- Core principles & background\n\n"
        "### 2. TECH STACK & TOOLING\n"
        "- Languages, frameworks, libraries, databases, OS\n\n"
        "### 3. COMMUNICATION & RESPONSE PREFERENCES\n"
        "- Tone, verbosity, code formatting, things to avoid (prohibitions)\n\n"
        "### 4. CODING & ARCHITECTURE CONVENTIONS\n"
        "- Architectural patterns, standards, testing requirements\n\n"
        "### 5. ACTIVE PROJECTS & WORKING CONTEXT\n"
        "- Current primary objective, active project names, recent decisions, current blockers\n\n"
        "### 6. PERSONAL & LIFESTYLE NOTES\n"
        "- Hobbies, personal interests, non-work preferences"
    )

def parse_chatgpt_data(raw_text: str, name_hint: str = "ChatGPT Persona") -> UMSPayload:
    """Parses raw text (memory dump, custom instructions, or prompt output) into UMSPayload."""
    # Check if raw_text is valid JSON
    try:
        data = json.loads(raw_text)
        if isinstance(data, dict) and "tier1_identity" in data:
            return UMSPayload.from_dict(data)
        from server.chat_handoff import unpack_json_chat_export
        unpacked = unpack_json_chat_export(raw_text)
        if unpacked != raw_text:
            raw_text = unpacked
    except Exception:
        pass

    payload = UMSPayload()
    payload.metadata.source_provider = "chatgpt"
    payload.metadata.name = name_hint
    payload.metadata.tags = ["chatgpt", "migrated"]

    lines = raw_text.splitlines()
    current_section = "general"

    languages = []
    frameworks = []
    databases = []
    toolchains = []
    standards = []
    patterns = []
    tests = []
    prohibitions = []
    decisions_today = []
    blockers = []
    trivia = []
    tone_items = []
    principles = []
    projects = []
    current_proj_name = "Active Workspace"
    objective = ""

    known_languages = {"typescript", "javascript", "python", "go", "golang", "rust", "c++", "c#", "java", "ruby", "swift", "kotlin", "sql", "html", "css"}
    known_frameworks = {"react", "next.js", "nextjs", "vue", "angular", "svelte", "tailwind", "fastapi", "django", "flask", "express", "node", "nestjs", "pytorch", "tensorflow"}
    known_databases = {"postgres", "postgresql", "mysql", "sqlite", "mongodb", "redis", "supabase", "prisma", "dynamodb"}

    for line in lines:
        s = line.strip()
        if not s:
            continue

        # Check if line is a bullet item vs section header
        is_bullet = bool(re.match(r"^(\*|-|\d+\.|\•)\s*", s))

        # Section headers (only if not a bullet item)
        if not is_bullet and (s.startswith("#") or s.isupper() or ":" in s or any(s.lower().startswith(x) for x in ["section", "category", "part"])):
            lower = s.lower()
            if any(h in lower for h in ["identity", "profile", "about me"]):
                current_section = "profile"
                continue
            elif any(h in lower for h in ["tech stack", "tooling", "technologies", "tech"]):
                current_section = "tech_stack"
                continue
            elif any(h in lower for h in ["communication", "response style", "how to respond", "tone"]):
                current_section = "communication"
                continue
            elif any(h in lower for h in ["conventions", "architecture", "coding standard"]):
                current_section = "conventions"
                continue
            elif any(h in lower for h in ["active project", "current task", "working context", "objective"]):
                current_section = "active_context"
                continue
            elif any(h in lower for h in ["personal", "lifestyle", "hobbies", "interests"]):
                current_section = "personal"
                continue

        # Clean bullet marker
        clean = re.sub(r"^(\*|-|\d+\.|\•)\s*", "", s).strip()
        if not clean:
            continue

        # Parse bullet into categories based on section or content heuristics
        if current_section == "profile":
            if "role:" in clean.lower() or "title:" in clean.lower():
                payload.tier1_identity.profile.role = clean.split(":", 1)[1].strip()
            elif "name:" in clean.lower():
                payload.tier1_identity.profile.name = clean.split(":", 1)[1].strip()
            else:
                principles.append(clean)

        elif current_section == "tech_stack":
            # Heuristic token extraction
            words = re.findall(r"[\w\.\+#]+", clean)
            for w in words:
                wl = w.lower()
                if wl in known_languages and w not in languages:
                    languages.append(w)
                elif wl in known_frameworks and w not in frameworks:
                    frameworks.append(w)
                elif wl in known_databases and w not in databases:
                    databases.append(w)
            toolchains.append(clean)

        elif current_section == "communication":
            if any(p in clean.lower() for p in ["never", "do not", "don't", "avoid", "no generic", "no filler"]):
                prohibitions.append(clean)
            else:
                tone_items.append(clean)

        elif current_section == "conventions":
            if any(t in clean.lower() for t in ["test", "unit", "tdd", "coverage"]):
                tests.append(clean)
            elif any(a in clean.lower() for a in ["pattern", "architecture", "clean code", "dry", "solid"]):
                patterns.append(clean)
            else:
                standards.append(clean)

        elif current_section == "active_context":
            if any(o in clean.lower() for o in ["objective", "goal", "current focus", "working on"]):
                objective = clean
            elif any(d in clean.lower() for d in ["decided", "decision", "finalized"]):
                decisions_today.append(clean)
            elif any(b in clean.lower() for b in ["blocker", "blocked", "issue", "obstacle"]):
                blockers.append(clean)
            else:
                decisions_today.append(clean)

        elif current_section == "personal":
            is_work = any(w in clean.lower() for w in ["work", "company", "startup", "product", "client"])
            trivia.append(PersonalTrivia(topic="personal_preference", value=clean, is_work_related=is_work))

        else:
            # General fallback heuristic matching
            lower_clean = clean.lower()
            if "role:" in lower_clean or "title:" in lower_clean:
                payload.tier1_identity.profile.role = clean.split(":", 1)[1].strip()
            elif "name:" in lower_clean:
                payload.tier1_identity.profile.name = clean.split(":", 1)[1].strip()
            elif any(w in lower_clean for w in ["never", "don't", "avoid"]):
                prohibitions.append(clean)
            elif any(w in lower_clean for w in ["concise", "direct", "brevity", "tone", "apology"]):
                tone_items.append(clean)
            elif any(w in lower_clean for w in ["objective", "goal", "working on"]):
                if ":" in clean:
                    objective = clean.split(":", 1)[1].strip()
                else:
                    objective = clean
            elif any(w in lower_clean for w in ["sport", "football", "music", "hobby", "hobbies", "fan"]):
                trivia.append(PersonalTrivia(topic="lifestyle", value=clean, is_work_related=False))
            else:
                # Check for tech stack keywords
                words = re.findall(r"[\w\.\+#]+", clean)
                found_tech = False
                for w in words:
                    wl = w.lower()
                    if wl in known_languages and w not in languages:
                        languages.append(w)
                        found_tech = True
                    elif wl in known_frameworks and w not in frameworks:
                        frameworks.append(w)
                        found_tech = True
                    elif wl in known_databases and w not in databases:
                        databases.append(w)
                        found_tech = True
                if not found_tech:
                    standards.append(clean)

    # Populate final payload
    if principles:
        payload.tier1_identity.profile.core_principles = principles

    if languages:
        payload.tier1_identity.tech_stack.primary_languages = languages
    if frameworks:
        payload.tier1_identity.tech_stack.frameworks = frameworks
    if databases:
        payload.tier1_identity.tech_stack.databases = databases
    if toolchains:
        payload.tier1_identity.tech_stack.toolchains = toolchains

    if tone_items:
        payload.tier1_identity.communication_style.tone = "; ".join(tone_items[:3])
    if prohibitions:
        payload.tier1_identity.communication_style.prohibitions = prohibitions

    if standards:
        payload.tier1_identity.conventions.coding_standards = standards
    if patterns:
        payload.tier1_identity.conventions.architecture_patterns = patterns
    if tests:
        payload.tier1_identity.conventions.testing_requirements = tests

    if trivia:
        payload.tier1_identity.personal_trivia = trivia

    if objective:
        payload.tier2_active_context.current_objective = objective
    else:
        payload.tier2_active_context.current_objective = "Build and ship active project milestones"

    payload.tier2_active_context.active_projects = [
        ActiveProject(
            name=current_proj_name,
            status="active",
            current_phase="implementation",
            decisions_made_today=decisions_today,
            active_blockers=blockers,
            next_steps=["Verify cross-provider memory retention"]
        )
    ]

    return payload
