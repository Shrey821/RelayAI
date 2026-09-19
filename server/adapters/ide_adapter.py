"""
Developer IDE Adapter
Formats UMS into developer-centric rule files: CLAUDE.md, .cursorrules, .windsurfrules, AGENTS.md.
"""

from __future__ import annotations
from typing import Dict, Any
from server.models import UMSPayload

def hydrate_for_ide(payload: UMSPayload) -> Dict[str, str]:
    t1 = payload.tier1_identity
    t2 = payload.tier2_active_context

    # 1. CLAUDE.md
    claude_md_lines = [
        f"# Claude Code Configuration for {t1.profile.name or 'Project'}",
        "",
        "## Developer Profile",
        f"- Role: {t1.profile.role}",
        f"- Preferred Tone: {t1.communication_style.tone}",
        f"- Verbosity: {t1.communication_style.verbosity}",
        "",
        "## Tech Stack & Runtime",
        f"- Languages: {', '.join(t1.tech_stack.primary_languages)}",
        f"- Frameworks: {', '.join(t1.tech_stack.frameworks)}",
        f"- Databases: {', '.join(t1.tech_stack.databases)}",
        f"- OS: {t1.tech_stack.operating_system}",
        "",
        "## Coding Conventions & Architecture",
    ]
    for s in t1.conventions.coding_standards:
        claude_md_lines.append(f"- {s}")
    for a in t1.conventions.architecture_patterns:
        claude_md_lines.append(f"- {a}")
    for t in t1.conventions.testing_requirements:
        claude_md_lines.append(f"- {t}")

    claude_md_lines.extend([
        "",
        "## Strict Prohibitions",
    ])
    for pr in t1.communication_style.prohibitions:
        claude_md_lines.append(f"- {pr}")

    if t2.current_objective:
        claude_md_lines.extend([
            "",
            "## Current Active Objective",
            f"- {t2.current_objective}"
        ])

    claude_md = "\n".join(claude_md_lines)

    # 2. .cursorrules
    cursorrules_lines = [
        "# Cursor Rules & Context Instructions",
        f"You are assisting a {t1.profile.role}.",
        "",
        "### Guidelines:",
        f"- Code Preference: {t1.communication_style.code_preference}",
        f"- Tone: {t1.communication_style.tone}",
        "",
        "### Tech Stack:",
        f"- Languages: {', '.join(t1.tech_stack.primary_languages)}",
        f"- Frameworks: {', '.join(t1.tech_stack.frameworks)}",
        f"- Databases: {', '.join(t1.tech_stack.databases)}",
        "",
        "### Constraints:",
    ]
    for pr in t1.communication_style.prohibitions:
        cursorrules_lines.append(f"- NEVER: {pr}")
    for s in t1.conventions.coding_standards:
        cursorrules_lines.append(f"- DO: {s}")

    cursorrules = "\n".join(cursorrules_lines)

    # 3. AGENTS.md
    agents_md = f"""# Agent Instructions (AGENTS.md)

## Persona
- Identity: {t1.profile.name} ({t1.profile.role})
- Communication: {t1.communication_style.tone}

## Technology Baseline
- Primary: {', '.join(t1.tech_stack.primary_languages)}
- Frameworks: {', '.join(t1.tech_stack.frameworks)}

## Active Objective
- {t2.current_objective}
"""

    return {
        "claude_md": claude_md,
        "cursorrules": cursorrules,
        "windsurfrules": cursorrules,
        "agents_md": agents_md
    }
