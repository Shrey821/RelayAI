"""
Gemini Ingestion Parser & Extraction Prompt Generator
Extracts Google Gemini saved info, Gems, and memory into UMS v1.0.0.
"""

from __future__ import annotations
import re
import json
from typing import Dict, Any
from server.models import (
    UMSPayload, PersonalTrivia, ActiveProject
)

def get_gemini_extraction_prompt() -> str:
    """Returns extraction prompt for Google Gemini."""
    return (
        "Please display all stored memory, saved information, and system instructions you have for me. "
        "Include my technical skills, preferences, active tasks, and communication style in a structured bulleted list."
    )

def parse_gemini_data(raw_text: str, name_hint: str = "Gemini Persona") -> UMSPayload:
    from server.parsers.chatgpt import parse_chatgpt_data
    payload = parse_chatgpt_data(raw_text, name_hint)
    payload.metadata.source_provider = "gemini"
    payload.metadata.tags = ["gemini", "migrated"]
    return payload
