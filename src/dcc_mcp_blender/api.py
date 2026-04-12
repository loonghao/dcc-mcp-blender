"""High-level API helpers for Blender MCP skill development.

These thin wrappers re-export the most commonly needed pieces from
*dcc-mcp-core* so that skill scripts can import from a single, stable
location::

    from dcc_mcp_blender.api import skill_success, skill_error, skill_exception

"""

from __future__ import annotations

# Re-export core skill helpers so skill scripts can stay DCC-agnostic
from dcc_mcp_core.skill import (
    skill_entry,
    skill_error,
    skill_exception,
    skill_success,
)

__all__ = [
    "skill_entry",
    "skill_error",
    "skill_exception",
    "skill_success",
]
