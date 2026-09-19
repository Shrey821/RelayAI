"""
Claude Hydration Adapter
Formats UMS into Claude's native 'Settings -> Memory -> Start import' format,
with intelligent work-focus filtering and official verification query generation.
"""

from __future__ import annotations
from typing import Dict, Any
from server.models import UMSPayload

def get_claude_verification_query() -> str:
    """Official Anthropic documented verification query."""
    return "I updated my memory. What did you learn about me?"

def hydrate_for_claude(
    payload: UMSPayload,
    include_tier1: bool = True,
    include_tier2: bool = True,
    include_tier3: bool = False,
    filter_non_work: bool = True
) -> Dict[str, Any]:
    """
    Hydrates UMS into Claude's native Memory Import text.
    Returns:
      - import_text: Formatted string ready to paste into Claude Settings -> Memory -> Start import.
      - verification_query: The official Anthropic verification prompt.
      - token_estimate: Approximate token count.
      - excluded_items: Items filtered out (e.g. non-work trivia).
    """
    sections = []
    excluded = []

    if include_tier1:
        t1 = payload.tier1_identity
        lines = ["# DEVELOPER PROFILE & CORE PREFERENCES"]

        # Profile & Role
        if t1.profile.role or t1.profile.name:
            lines.append(f"- **Role**: {t1.profile.role} ({t1.profile.name})")
        if t1.profile.core_principles:
            lines.append("- **Core Principles**:")
            for p in t1.profile.core_principles:
                lines.append(f"  • {p}")

        # Tech Stack
        ts = t1.tech_stack
        tech_items = []
        if ts.primary_languages:
            tech_items.append(f"Languages: {', '.join(ts.primary_languages)}")
        if ts.frameworks:
            tech_items.append(f"Frameworks: {', '.join(ts.frameworks)}")
        if ts.databases:
            tech_items.append(f"Databases: {', '.join(ts.databases)}")
        if ts.toolchains:
            tech_items.append(f"Tools & Environment: {', '.join(ts.toolchains)}")
        if ts.operating_system:
            tech_items.append(f"OS: {ts.operating_system}")

        if tech_items:
            lines.append("- **Primary Tech Stack**:")
            for ti in tech_items:
                lines.append(f"  • {ti}")

        # Conventions
        cv = t1.conventions
        if cv.coding_standards or cv.architecture_patterns or cv.testing_requirements:
            lines.append("- **Engineering Conventions & Standards**:")
            for s in cv.coding_standards:
                lines.append(f"  • {s}")
            for a in cv.architecture_patterns:
                lines.append(f"  • {a}")
            for t in cv.testing_requirements:
                lines.append(f"  • {t}")

        # Communication Style
        cs = t1.communication_style
        lines.append("- **Communication & Output Guidelines**:")
        lines.append(f"  • Tone: {cs.tone}")
        lines.append(f"  • Verbosity: {cs.verbosity}")
        if cs.code_preference:
            lines.append(f"  • Code Standard: {cs.code_preference}")
        if cs.prohibitions:
            lines.append("  • Strict Prohibitions (NEVER DO):")
            for pr in cs.prohibitions:
                lines.append(f"    - {pr}")

        # Personal Trivia / Lifestyle
        if t1.personal_trivia:
            trivia_work = [tr for tr in t1.personal_trivia if tr.is_work_related]
            trivia_non_work = [tr for tr in t1.personal_trivia if not tr.is_work_related]

            if filter_non_work:
                for tr in trivia_non_work:
                    excluded.append(f"Personal Trivia: {tr.topic} - {tr.value} (filtered by Claude Work-Focus policy)")
                if trivia_work:
                    lines.append("- **Work Habits & Preferences**:")
                    for tr in trivia_work:
                        lines.append(f"  • {tr.topic}: {tr.value}")
            else:
                lines.append("- **Personal Preferences & Background**:")
                for tr in t1.personal_trivia:
                    lines.append(f"  • {tr.topic}: {tr.value}")

        sections.append("\n".join(lines))

    if include_tier2:
        t2 = payload.tier2_active_context
        lines = ["# ACTIVE WORKING CONTEXT & OBJECTIVES"]
        if t2.current_objective:
            lines.append(f"- **Current Primary Objective**: {t2.current_objective}")

        if t2.active_projects:
            lines.append("- **Active Projects**:")
            for proj in t2.active_projects:
                lines.append(f"  • Project: {proj.name} ({proj.status})")
                if proj.decisions_made_today:
                    lines.append("    - Decisions Finalized Today:")
                    for d in proj.decisions_made_today:
                        lines.append(f"      * {d}")
                if proj.active_blockers:
                    lines.append("    - Active Blockers:")
                    for b in proj.active_blockers:
                        lines.append(f"      * {b}")

        if t2.ephemeral_constraints:
            lines.append("- **Temporary Constraints**:")
            for ec in t2.ephemeral_constraints:
                lines.append(f"  • {ec}")

        sections.append("\n".join(lines))

    if include_tier3 and payload.tier3_conversation_transcript.included:
        t3 = payload.tier3_conversation_transcript
        lines = ["# RECENT CONVERSATIONAL CONTEXT"]
        if t3.summary:
            lines.append(f"Summary: {t3.summary}")
        for m in t3.messages[-5:]:
            lines.append(f"[{m.role.upper()}]: {m.content}")
        sections.append("\n".join(lines))

    import_text = "\n\n".join(sections)
    # Estimate tokens (~4 characters per token)
    token_estimate = max(1, len(import_text) // 4)

    return {
        "target_provider": "claude",
        "format": "native_memory_import",
        "import_text": import_text,
        "verification_query": get_claude_verification_query(),
        "token_estimate": token_estimate,
        "character_count": len(import_text),
        "excluded_items": excluded,
        "instructions": "In Claude, navigate to Settings → Memory → click 'Start import' and paste this content. Afterwards, query Claude with the verification prompt to verify retention."
    }
