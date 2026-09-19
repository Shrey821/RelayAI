"""
UMS Verification & Semantic Diff Engine
Evaluates target AI verification responses against source UMS payloads to detect retained, adapted, or filtered memory items.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from server.models import UMSPayload

class DiffEntry:
    def __init__(
        self,
        category: str,
        field: str,
        item: str,
        status: str,  # 'learned', 'adapted', 'filtered'
        reason: str = "",
        confidence: float = 1.0
    ):
        self.category = category
        self.field = field
        self.item = item
        self.status = status
        self.reason = reason
        self.confidence = round(confidence, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "field": self.field,
            "item": self.item,
            "status": self.status,
            "reason": self.reason,
            "confidence": self.confidence
        }

def compute_verification_diff(
    source_payload: UMSPayload,
    verification_response: str,
    target_provider: str = "claude"
) -> Dict[str, Any]:
    """
    Compares the verification response from target AI (e.g. Claude's answer to
    'What did you learn about me?') against the source UMS payload.
    """
    resp_lower = verification_response.lower()
    entries: List[DiffEntry] = []
    suggestions: List[str] = []

    # 1. Evaluate Tech Stack (Tier 1)
    for lang in source_payload.tier1_identity.tech_stack.primary_languages:
        clean = lang.strip().lower()
        if not clean:
            continue
        if clean in resp_lower:
            entries.append(DiffEntry("tier1", "language", lang, "learned", "Explicitly mentioned in target memory", 1.0))
        elif any(part in resp_lower for part in clean.split()):
            entries.append(DiffEntry("tier1", "language", lang, "adapted", "Partially recognized or consolidated", 0.7))
        else:
            entries.append(DiffEntry("tier1", "language", lang, "filtered", "Not found in verification response", 0.9))

    for fw in source_payload.tier1_identity.tech_stack.frameworks:
        clean = fw.strip().lower()
        # Normalization for e.g. next.js vs nextjs
        clean_norm = re.sub(r"[\.\s_-]", "", clean)
        resp_norm = re.sub(r"[\.\s_-]", "", resp_lower)
        if clean in resp_lower or clean_norm in resp_norm:
            entries.append(DiffEntry("tier1", "framework", fw, "learned", "Recognized in target memory", 1.0))
        else:
            entries.append(DiffEntry("tier1", "framework", fw, "filtered", "Omitted by target memory", 0.8))

    for db in source_payload.tier1_identity.tech_stack.databases:
        clean = db.strip().lower()
        if clean in resp_lower:
            entries.append(DiffEntry("tier1", "database", db, "learned", "Retained", 1.0))
        else:
            entries.append(DiffEntry("tier1", "database", db, "filtered", "Not explicitly retained", 0.8))

    # 2. Evaluate Communication Style & Prohibitions (Tier 1)
    tone = source_payload.tier1_identity.communication_style.tone
    if tone:
        tone_words = [w for w in re.split(r"[\s,;]+", tone.lower()) if len(w) > 3]
        matches = [w for w in tone_words if w in resp_lower]
        if len(matches) >= max(1, len(tone_words) // 2):
            entries.append(DiffEntry("tier1", "communication_style", f"Tone: {tone}", "learned", "Style preferences adopted", 0.95))
        elif len(matches) > 0:
            entries.append(DiffEntry("tier1", "communication_style", f"Tone: {tone}", "adapted", "Partially reflected in tone", 0.65))
        else:
            entries.append(DiffEntry("tier1", "communication_style", f"Tone: {tone}", "filtered", "Tone guidelines not mentioned", 0.7))

    for pr in source_payload.tier1_identity.communication_style.prohibitions:
        clean_words = [w for w in re.findall(r"\w+", pr.lower()) if len(w) > 3]
        matched_words = [w for w in clean_words if w in resp_lower]
        if len(matched_words) >= 2 or ("never" in resp_lower and len(matched_words) >= 1):
            entries.append(DiffEntry("tier1", "prohibition", pr, "learned", "Constraint noted by target AI", 0.9))
        else:
            entries.append(DiffEntry("tier1", "prohibition", pr, "filtered", "Negative constraint omitted", 0.75))

    # 3. Evaluate Conventions (Tier 1)
    for std in source_payload.tier1_identity.conventions.coding_standards:
        words = [w for w in re.findall(r"\w+", std.lower()) if len(w) > 3]
        if any(w in resp_lower for w in words):
            entries.append(DiffEntry("tier1", "standard", std, "learned", "Coding convention reflected", 0.85))
        else:
            entries.append(DiffEntry("tier1", "standard", std, "adapted", "Consolidated into general coding profile", 0.5))

    # 4. Evaluate Personal Trivia (Tier 1) - Key Work vs Non-Work check
    for tr in source_payload.tier1_identity.personal_trivia:
        val_clean = tr.value.lower()
        words = [w for w in re.findall(r"\w+", val_clean) if len(w) > 3]
        found = any(w in resp_lower for w in words)
        if found:
            entries.append(DiffEntry("tier1", "personal_trivia", f"{tr.topic}: {tr.value}", "learned", "Retained in memory", 0.9))
        else:
            if not tr.is_work_related and target_provider == "claude":
                entries.append(DiffEntry(
                    "tier1",
                    "personal_trivia",
                    f"{tr.topic}: {tr.value}",
                    "filtered",
                    "Expected: Omitted due to Claude Work-Focus filter",
                    1.0
                ))
            else:
                entries.append(DiffEntry("tier1", "personal_trivia", f"{tr.topic}: {tr.value}", "filtered", "Omitted", 0.8))

    # 5. Evaluate Active Context (Tier 2)
    obj = source_payload.tier2_active_context.current_objective
    if obj:
        words = [w for w in re.findall(r"\w+", obj.lower()) if len(w) > 3]
        match_count = sum(1 for w in words if w in resp_lower)
        if match_count >= max(1, len(words) // 2):
            entries.append(DiffEntry("tier2", "objective", obj, "learned", "Active goal successfully tracked", 0.95))
        elif match_count > 0:
            entries.append(DiffEntry("tier2", "objective", obj, "adapted", "Active objective generalized", 0.7))
        else:
            entries.append(DiffEntry("tier2", "objective", obj, "filtered", "Active goal not captured in long-term memory", 0.6))

    for proj in source_payload.tier2_active_context.active_projects:
        proj_name_clean = proj.name.lower()
        if proj_name_clean in resp_lower:
            entries.append(DiffEntry("tier2", "active_project", proj.name, "learned", f"Project recognized ({proj.status})", 0.95))
        else:
            entries.append(DiffEntry("tier2", "active_project", proj.name, "adapted", "Project context consolidated", 0.6))

    # Compute Statistics
    total = len(entries) or 1
    learned = sum(1 for e in entries if e.status == "learned")
    adapted = sum(1 for e in entries if e.status == "adapted")
    filtered = sum(1 for e in entries if e.status == "filtered")

    score = round(((learned * 1.0 + adapted * 0.5) / total) * 100, 1)

    # Generate Intelligent Suggestions
    if filtered > 0:
        filtered_trivia = [e for e in entries if e.field == "personal_trivia" and e.status == "filtered"]
        if filtered_trivia and target_provider == "claude":
            suggestions.append(
                "Claude intentionally filters out non-work personal trivia (e.g. sports teams, hobbies) "
                "to preserve professional memory capacity. This is expected behavior."
            )
        filtered_prohibitions = [e for e in entries if e.field == "prohibition" and e.status == "filtered"]
        if filtered_prohibitions:
            suggestions.append(
                "Some negative constraints (prohibitions) were not explicitly echoed. "
                "Consider appending them directly to your custom prompt or rules file."
            )

    if score >= 85:
        suggestions.append("Outstanding retention! Your target AI has absorbed the core of your technical identity and active context.")
    elif score >= 65:
        suggestions.append("Good retention. Technical stacks were captured; consider re-affirming active task objectives.")
    else:
        suggestions.append("Low retention detected. We recommend re-running the import using the formatted UMS payload without extraneous transcript text.")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_provider": source_payload.metadata.source_provider,
        "target_provider": target_provider,
        "retention_score": score,
        "items_total": len(entries),
        "items_learned": learned,
        "items_adapted": adapted,
        "items_filtered": filtered,
        "diff_entries": [e.to_dict() for e in entries],
        "suggestions": suggestions
    }
