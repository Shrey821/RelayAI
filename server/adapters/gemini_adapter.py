"""
Gemini Hydration Adapter
Formats UMS into Google Gemini System Instructions and Gems configuration.
"""

from __future__ import annotations
from typing import Dict, Any
from server.models import UMSPayload

def get_gemini_verification_query() -> str:
    return "What preferences, background, and instructions do you have saved about me?"

def hydrate_for_gemini(
    payload: UMSPayload,
    include_tier1: bool = True,
    include_tier2: bool = True,
    include_tier3: bool = False
) -> Dict[str, Any]:
    t1 = payload.tier1_identity
    t2 = payload.tier2_active_context

    lines = ["# GEMINI SYSTEM INSTRUCTIONS & PERSONA PROFILE\n"]
    if include_tier1:
        lines.append(f"User: {t1.profile.name} - {t1.profile.role}")
        if t1.profile.core_principles:
            lines.append("Core Principles:\n" + "\n".join(f"- {p}" for p in t1.profile.core_principles))
        
        techs = t1.tech_stack.primary_languages + t1.tech_stack.frameworks + t1.tech_stack.databases
        if techs:
            lines.append(f"Tech Stack: {', '.join(techs)}")

        lines.append(f"Tone: {t1.communication_style.tone}")
        lines.append(f"Verbosity: {t1.communication_style.verbosity}")
        if t1.communication_style.prohibitions:
            lines.append("Strict Avoidances:\n" + "\n".join(f"- {pr}" for pr in t1.communication_style.prohibitions))

    if include_tier2:
        if t2.current_objective:
            lines.append(f"\nCurrent Objective: {t2.current_objective}")
        for p in t2.active_projects:
            lines.append(f"Active Project: {p.name}")
            if p.decisions_made_today:
                lines.append("Decisions: " + ", ".join(p.decisions_made_today))

    system_instruction = "\n".join(lines)
    return {
        "target_provider": "gemini",
        "system_instruction": system_instruction,
        "verification_query": get_gemini_verification_query(),
        "token_estimate": max(1, len(system_instruction) // 4),
        "instructions": "In Google Gemini, create a custom Gem or paste into System Instructions."
    }
