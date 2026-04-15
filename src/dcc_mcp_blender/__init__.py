"""dcc-mcp-blender — Blender MCP server package.

Quick start::

    import dcc_mcp_blender

    # Start the server (auto-gateway: first Blender wins port 8765)
    server = dcc_mcp_blender.start_server()

    # Progressive loading
    server.discover_skills()                # scan SKILL.md, register metadata
    server.load_skill("blender-scene")      # lazy-import skill scripts on demand
    server.unload_skill("blender-scene")    # free memory when no longer needed

    dcc_mcp_blender.stop_server()
"""

from __future__ import annotations

from dcc_mcp_blender.__version__ import __version__
from dcc_mcp_blender.api import (
    skill_entry,
    skill_error,
    skill_exception,
    skill_success,
)
from dcc_mcp_blender.capabilities import blender_capabilities, blender_capabilities_dict
from dcc_mcp_blender.server import (
    BlenderMcpServer,
    get_server,
    start_server,
    stop_server,
)

__all__ = [
    "__version__",
    # server lifecycle
    "BlenderMcpServer",
    "start_server",
    "stop_server",
    "get_server",
    # capabilities
    "blender_capabilities",
    "blender_capabilities_dict",
    # skill helpers
    "skill_entry",
    "skill_error",
    "skill_exception",
    "skill_success",
]
