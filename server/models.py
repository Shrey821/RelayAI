"""
Universal Memory Schema (UMS) - Data Models
Version 1.0.0
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class PersonalTrivia:
    topic: str
    value: str
    is_work_related: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Profile:
    name: str = "Developer"
    role: str = "Software Engineer"
    bio: str = ""
    core_principles: List[str] = field(default_factory=list)

@dataclass
class TechStack:
    primary_languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    toolchains: List[str] = field(default_factory=list)
    operating_system: str = "macOS"

@dataclass
class CommunicationStyle:
    tone: str = "concise, direct, senior engineer"
    verbosity: str = "concise"  # minimalist, concise, balanced, thorough, verbose
    code_preference: str = "production-ready, idiomatic, no placeholder code"
    prohibitions: List[str] = field(default_factory=list)

@dataclass
class Conventions:
    coding_standards: List[str] = field(default_factory=list)
    architecture_patterns: List[str] = field(default_factory=list)
    testing_requirements: List[str] = field(default_factory=list)

@dataclass
class Tier1Identity:
    profile: Profile = field(default_factory=Profile)
    tech_stack: TechStack = field(default_factory=TechStack)
    communication_style: CommunicationStyle = field(default_factory=CommunicationStyle)
    conventions: Conventions = field(default_factory=Conventions)
    personal_trivia: List[PersonalTrivia] = field(default_factory=list)

@dataclass
class ActiveProject:
    name: str
    status: str = "active"
    current_phase: str = "development"
    decisions_made_today: List[str] = field(default_factory=list)
    active_blockers: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

@dataclass
class Tier2ActiveContext:
    current_objective: str = ""
    active_projects: List[ActiveProject] = field(default_factory=list)
    ephemeral_constraints: List[str] = field(default_factory=list)

@dataclass
class TranscriptMessage:
    role: str
    content: str
    timestamp: str = ""

@dataclass
class Tier3Transcript:
    included: bool = False
    summary: str = ""
    message_count: int = 0
    messages: List[TranscriptMessage] = field(default_factory=list)

@dataclass
class UMSMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Default Persona"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_provider: str = "chatgpt"
    tags: List[str] = field(default_factory=lambda: ["default", "dev"])

@dataclass
class UMSPayload:
    version: str = "1.0.0"
    metadata: UMSMetadata = field(default_factory=UMSMetadata)
    tier1_identity: Tier1Identity = field(default_factory=Tier1Identity)
    tier2_active_context: Tier2ActiveContext = field(default_factory=Tier2ActiveContext)
    tier3_conversation_transcript: Tier3Transcript = field(default_factory=Tier3Transcript)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UMSPayload:
        meta_data = data.get("metadata", {})
        metadata = UMSMetadata(
            id=meta_data.get("id", str(uuid.uuid4())),
            name=meta_data.get("name", "Imported Persona"),
            created_at=meta_data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=meta_data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            source_provider=meta_data.get("source_provider", "generic"),
            tags=meta_data.get("tags", [])
        )

        t1_raw = data.get("tier1_identity", {})
        prof_raw = t1_raw.get("profile", {})
        profile = Profile(
            name=prof_raw.get("name", "Developer"),
            role=prof_raw.get("role", "Software Engineer"),
            bio=prof_raw.get("bio", ""),
            core_principles=prof_raw.get("core_principles", [])
        )

        stack_raw = t1_raw.get("tech_stack", {})
        tech_stack = TechStack(
            primary_languages=stack_raw.get("primary_languages", []),
            frameworks=stack_raw.get("frameworks", []),
            databases=stack_raw.get("databases", []),
            toolchains=stack_raw.get("toolchains", []),
            operating_system=stack_raw.get("operating_system", "macOS")
        )

        comm_raw = t1_raw.get("communication_style", {})
        comm = CommunicationStyle(
            tone=comm_raw.get("tone", "concise"),
            verbosity=comm_raw.get("verbosity", "concise"),
            code_preference=comm_raw.get("code_preference", "production-ready"),
            prohibitions=comm_raw.get("prohibitions", [])
        )

        conv_raw = t1_raw.get("conventions", {})
        conventions = Conventions(
            coding_standards=conv_raw.get("coding_standards", []),
            architecture_patterns=conv_raw.get("architecture_patterns", []),
            testing_requirements=conv_raw.get("testing_requirements", [])
        )

        trivia = []
        for item in t1_raw.get("personal_trivia", []):
            if isinstance(item, dict):
                trivia.append(PersonalTrivia(
                    topic=item.get("topic", "interest"),
                    value=item.get("value", ""),
                    is_work_related=item.get("is_work_related", False)
                ))
            elif isinstance(item, str):
                trivia.append(PersonalTrivia(topic="note", value=item, is_work_related=False))

        tier1 = Tier1Identity(
            profile=profile,
            tech_stack=tech_stack,
            communication_style=comm,
            conventions=conventions,
            personal_trivia=trivia
        )

        t2_raw = data.get("tier2_active_context", {})
        projects = []
        for p in t2_raw.get("active_projects", []):
            projects.append(ActiveProject(
                name=p.get("name", "Current Project"),
                status=p.get("status", "active"),
                current_phase=p.get("current_phase", "in_progress"),
                decisions_made_today=p.get("decisions_made_today", []),
                active_blockers=p.get("active_blockers", []),
                next_steps=p.get("next_steps", [])
            ))

        tier2 = Tier2ActiveContext(
            current_objective=t2_raw.get("current_objective", ""),
            active_projects=projects,
            ephemeral_constraints=t2_raw.get("ephemeral_constraints", [])
        )

        t3_raw = data.get("tier3_conversation_transcript", {})
        messages = [
            TranscriptMessage(
                role=m.get("role", "user"),
                content=m.get("content", ""),
                timestamp=m.get("timestamp", "")
            )
            for m in t3_raw.get("messages", [])
        ]
        tier3 = Tier3Transcript(
            included=t3_raw.get("included", False),
            summary=t3_raw.get("summary", ""),
            message_count=len(messages),
            messages=messages
        )

        return cls(
            version=data.get("version", "1.0.0"),
            metadata=metadata,
            tier1_identity=tier1,
            tier2_active_context=tier2,
            tier3_conversation_transcript=tier3
        )
