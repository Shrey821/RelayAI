"""
ChatGPT Hydration Adapter
Formats UMS into ChatGPT's dual 1500-char Custom Instructions,
conversational memory injection, and verification query.
"""

from __future__ import annotations
from typing import Dict, Any
from server.models import UMSPayload

def get_chatgpt_verification_query() -> str:
    """Official OpenAI documented memory inspection prompt."""
    return "What do you remember about me? Please list all stored memories and active context."

def hydrate_for_chatgpt(
    payload: UMSPayload,
    include_tier1: bool = True,
    include_tier2: bool = True,
    include_tier3: bool = False
) -> Dict[str, Any]:
    """
    Hydrates UMS into ChatGPT formats:
    1. Custom Instructions Box 1: What to know about you (max 1500 chars)
    2. Custom Instructions Box 2: How to respond (max 1500 chars)
    3. Memory Injection Prompt: Conversational prompt to add to ChatGPT memory
    """
    t1 = payload.tier1_identity
    t2 = payload.tier2_active_context

    # Box 1: What should ChatGPT know about you?
    box1_lines = []
    if include_tier1:
        if t1.profile.name or t1.profile.role:
            box1_lines.append(f"Role: {t1.profile.role} ({t1.profile.name})")

        ts = t1.tech_stack
        techs = []
        if ts.primary_languages:
            techs.append(f"Languages: {', '.join(ts.primary_languages)}")
        if ts.frameworks:
            techs.append(f"Frameworks: {', '.join(ts.frameworks)}")
        if ts.databases:
            techs.append(f"DBs: {', '.join(ts.databases)}")
        if ts.operating_system:
            techs.append(f"OS: {ts.operating_system}")
        if techs:
            box1_lines.append("Tech Stack: " + " | ".join(techs))

        cv = t1.conventions
        if cv.coding_standards:
            box1_lines.append("Standards: " + "; ".join(cv.coding_standards[:3]))
        if cv.architecture_patterns:
            box1_lines.append("Architecture: " + "; ".join(cv.architecture_patterns[:3]))

        if t1.personal_trivia:
            triv = [f"{tr.topic}: {tr.value}" for tr in t1.personal_trivia[:3]]
            box1_lines.append("Background: " + "; ".join(triv))

    if include_tier2:
        if t2.current_objective:
            box1_lines.append(f"Active Objective: {t2.current_objective}")
        for p in t2.active_projects:
            box1_lines.append(f"Project '{p.name}': {p.status}. Next: {'; '.join(p.next_steps[:2])}")
        if t2.ephemeral_constraints:
            box1_lines.append("Active Constraints: " + "; ".join(t2.ephemeral_constraints))

    box1_text = "\n".join(box1_lines)
    # Ensure <= 1500 chars
    if len(box1_text) > 1500:
        box1_text = box1_text[:1490] + "..."

    # Box 2: How should ChatGPT respond?
    box2_lines = []
    cs = t1.communication_style
    box2_lines.append(f"Tone: {cs.tone}")
    box2_lines.append(f"Verbosity: {cs.verbosity}")
    if cs.code_preference:
        box2_lines.append(f"Code preference: {cs.code_preference}")
    if cs.prohibitions:
        box2_lines.append("Strict rules to avoid:")
        for pr in cs.prohibitions:
            box2_lines.append(f"- {pr}")

    box2_text = "\n".join(box2_lines)
    if len(box2_text) > 1500:
        box2_text = box2_text[:1490] + "..."

    # Conversational memory injection prompt
    injection_lines = [
        "Please remember the following long-term preferences and context for future chats:",
        f"- Role: {t1.profile.role}",
        f"- Languages & Tools: {', '.join(t1.tech_stack.primary_languages + t1.tech_stack.frameworks)}",
        f"- Communication style: {t1.communication_style.tone}, {t1.communication_style.verbosity}",
        f"- Active goal: {t2.current_objective}"
    ]
    if t1.communication_style.prohibitions:
        injection_lines.append(f"- Strictly avoid: {'; '.join(t1.communication_style.prohibitions)}")

    memory_injection_prompt = "\n".join(injection_lines)

    return {
        "target_provider": "chatgpt",
        "custom_instructions_box_1": box1_text,
        "custom_instructions_box_1_chars": len(box1_text),
        "custom_instructions_box_2": box2_text,
        "custom_instructions_box_2_chars": len(box2_text),
        "memory_injection_prompt": memory_injection_prompt,
        "verification_query": get_chatgpt_verification_query(),
        "instructions": "In ChatGPT, go to Settings → Custom Instructions. Paste Box 1 into 'What would you like ChatGPT to know about you' and Box 2 into 'How would you like ChatGPT to respond'. Alternatively, send the Memory Injection Prompt in chat."
    }
