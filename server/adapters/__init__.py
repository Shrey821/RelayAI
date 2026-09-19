"""
UMS Target Hydrators & Provider Adapters
Transforms UMS intermediate representations into native provider formats.
"""

from server.adapters.claude_adapter import hydrate_for_claude, get_claude_verification_query
from server.adapters.chatgpt_adapter import hydrate_for_chatgpt, get_chatgpt_verification_query
from server.adapters.gemini_adapter import hydrate_for_gemini, get_gemini_verification_query
from server.adapters.ide_adapter import hydrate_for_ide
