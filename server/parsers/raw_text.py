"""
Raw Text / Markdown Parser
Extracts unstructured developer notes, cursorrules, or freeform text into UMS v1.0.0.
"""

from __future__ import annotations
from server.models import UMSPayload
from server.parsers.chatgpt import parse_chatgpt_data

def parse_raw_text(text: str, name_hint: str = "Imported Profile") -> UMSPayload:
    payload = parse_chatgpt_data(text, name_hint)
    payload.metadata.source_provider = "generic"
    payload.metadata.tags = ["raw_text", "custom"]
    return payload
