"""dcc-mcp-blender — Blender MCP server package.

Quick start::

    import dcc_mcp_blender
    dcc_mcp_blender.start_server()   # listens on http://127.0.0.1:8765/mcp
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
from dcc_mcp_blender.server import (
    BlenderMcpServer,
    get_server,
    start_server,
    stop_server,
)

__all__ = [
    "__version__",
    # server
    "BlenderMcpServer",
    "start_server",
    "stop_server",
    "get_server",
    # skill helpers
    "skill_entry",
    "skill_error",
    "skill_exception",
    "skill_success",
]
