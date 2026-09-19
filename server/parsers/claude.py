"""
Claude Ingestion Parser & Extraction Prompt Generator
Extracts Claude memory, preferences, and Anthropic migration prompt outputs into UMS v1.0.0.
"""

from __future__ import annotations
import re
import json
from typing import Dict, Any, List
from server.models import (
    UMSPayload, UMSMetadata, Tier1Identity, Tier2ActiveContext,
    Profile, TechStack, CommunicationStyle, Conventions, PersonalTrivia, ActiveProject
)

def get_claude_extraction_prompt() -> str:
    """Returns the official Anthropic migration extraction prompt."""
    return (
        "I'm moving to another service and need to export my data. "
        "Please provide a comprehensive summary of everything in your memory and context about me: "
        "including my role, technical stack, architecture guidelines, communication preferences, "
        "active projects, and current objectives."
    )

def parse_claude_data(raw_text: str, name_hint: str = "Claude Persona") -> UMSPayload:
    """Parses Claude's memory export or migration response into UMS format."""
    try:
        data = json.loads(raw_text)
        if isinstance(data, dict) and "tier1_identity" in data:
            return UMSPayload.from_dict(data)
    except Exception:
        pass

    payload = UMSPayload()
    payload.metadata.source_provider = "claude"
    payload.metadata.name = name_hint
    payload.metadata.tags = ["claude", "migrated"]

    lines = raw_text.splitlines()
    languages = []
    frameworks = []
    standards = []
    conventions = []
    prohibitions = []
    trivia = []
    tone_items = []
    principles = []
    decisions = []
    blockers = []
    objective = ""

    known_languages = {"typescript", "javascript", "python", "go", "rust", "c++", "c#", "java", "ruby", "swift", "kotlin", "sql", "html", "css"}
    known_frameworks = {"react", "next.js", "nextjs", "vue", "svelte", "tailwind", "fastapi", "django", "express", "node"}

    for line in lines:
        s = line.strip()
        if not s:
            continue
        clean = re.sub(r"^(\*|-|\d+\.|\•)\s*", "", s).strip()
        if not clean:
            continue

        lower = clean.lower()
        if any(w in lower for w in ["objective", "goal", "current focus", "working on"]):
            if ":" in clean:
                objective = clean.split(":", 1)[1].strip()
            else:
                objective = clean
        elif any(w in lower for w in ["never", "do not", "don't", "avoid", "no pleasantries"]):
            prohibitions.append(clean)
        elif any(w in lower for w in ["concise", "direct", "brevity", "tone"]):
            tone_items.append(clean)
        elif any(w in lower for w in ["decided", "decision", "architecture"]):
            decisions.append(clean)
        elif any(w in lower for w in ["blocker", "blocked", "issue"]):
            blockers.append(clean)
        elif any(w in lower for w in ["hobby", "interest", "sport", "favorite"]):
            trivia.append(PersonalTrivia(topic="personal", value=clean, is_work_related=False))
        else:
            # Check for tech stack tokens
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
            if not found_tech:
                standards.append(clean)

    if languages:
        payload.tier1_identity.tech_stack.primary_languages = languages
    if frameworks:
        payload.tier1_identity.tech_stack.frameworks = frameworks
    if tone_items:
        payload.tier1_identity.communication_style.tone = "; ".join(tone_items)
    if prohibitions:
        payload.tier1_identity.communication_style.prohibitions = prohibitions
    if standards:
        payload.tier1_identity.conventions.coding_standards = standards
    if trivia:
        payload.tier1_identity.personal_trivia = trivia

    payload.tier2_active_context.current_objective = objective or "Active Project Execution"
    payload.tier2_active_context.active_projects = [
        ActiveProject(
            name="Active Claude Project",
            status="active",
            decisions_made_today=decisions,
            active_blockers=blockers,
            next_steps=[]
        )
    ]

    return payload
