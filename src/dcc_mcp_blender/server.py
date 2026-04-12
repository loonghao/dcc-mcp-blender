"""Blender MCP server — embeds a Streamable HTTP MCP server inside Blender.

Usage (inside Blender Python console or startup script):

    import dcc_mcp_blender
    dcc_mcp_blender.start_server()        # default port 8765
    dcc_mcp_blender.stop_server()
"""

from __future__ import annotations

import logging
import os
import pathlib
from typing import Any, Dict, List, Optional

from dcc_mcp_core.server import DccMcpServer
from dcc_mcp_core.skill_manager import SkillManager

from dcc_mcp_blender.__version__ import __version__

logger = logging.getLogger(__name__)

# ── constants ────────────────────────────────────────────────────────────────

SERVER_NAME = "dcc-mcp-blender"
SERVER_VERSION = __version__
DEFAULT_PORT = 8765

# Built-in skills directory shipped with this package
_BUILTIN_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

# Environment variable for extra skill paths (colon/semicolon separated)
_ENV_EXTRA_SKILL_PATHS = "DCC_MCP_BLENDER_SKILL_PATHS"
_ENV_GENERIC_SKILL_PATHS = "DCC_MCP_SKILL_PATHS"


# ── server class ─────────────────────────────────────────────────────────────


class BlenderMcpServer(DccMcpServer):
    """MCP server embedded inside Blender.

    This class wraps *dcc-mcp-core*'s :class:`DccMcpServer` and adds
    Blender-specific skill discovery and lifecycle helpers.

    Attributes:
        port: TCP port the HTTP server listens on (default 8765).
        extra_skill_paths: Additional skill directories to load on startup.
    """

    def __init__(
        self,
        port: int = DEFAULT_PORT,
        extra_skill_paths: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=SERVER_NAME,
            version=SERVER_VERSION,
            port=port,
            **kwargs,
        )
        self._extra_skill_paths: List[str] = extra_skill_paths or []

    # ── skill discovery ───────────────────────────────────────────────────

    def _collect_skill_paths(self) -> List[str]:
        """Collect all skill directory paths in priority order.

        Priority (highest → lowest):
        1. Paths passed to the constructor via *extra_skill_paths*
        2. Built-in skills bundled with this package
        3. ``DCC_MCP_BLENDER_SKILL_PATHS`` env var (colon/semicolon separated)
        4. ``DCC_MCP_SKILL_PATHS`` env var (generic fallback)

        Returns:
            Deduplicated list of existing directory paths as strings.
        """
        candidates: List[str] = []

        # 1) constructor overrides
        candidates.extend(self._extra_skill_paths)

        # 2) built-ins
        if _BUILTIN_SKILLS_DIR.is_dir():
            candidates.append(str(_BUILTIN_SKILLS_DIR))

        # 3) Blender-specific env var
        for raw in (
            os.environ.get(_ENV_EXTRA_SKILL_PATHS, ""),
            os.environ.get(_ENV_GENERIC_SKILL_PATHS, ""),
        ):
            for part in raw.replace(";", ":").split(":"):
                part = part.strip()
                if part:
                    candidates.append(part)

        # deduplicate while preserving order
        seen: set = set()
        result: List[str] = []
        for p in candidates:
            if p not in seen and pathlib.Path(p).is_dir():
                seen.add(p)
                result.append(p)
        return result

    # ── DccMcpServer overrides ────────────────────────────────────────────

    def build_skill_manager(self) -> SkillManager:
        """Create a :class:`SkillManager` loaded with all discovered skills."""
        paths = self._collect_skill_paths()
        logger.debug("BlenderMcpServer: loading skills from %s", paths)
        manager = SkillManager()
        for path in paths:
            manager.load_skills_from_directory(path)
        return manager

    def get_capabilities(self) -> Dict[str, Any]:
        """Return Blender DCC capabilities."""
        from dcc_mcp_blender.capabilities import BLENDER_CAPABILITIES_DICT

        return BLENDER_CAPABILITIES_DICT


# ── module-level singleton helpers ────────────────────────────────────────────

_server: Optional[BlenderMcpServer] = None


def start_server(
    port: int = DEFAULT_PORT,
    extra_skill_paths: Optional[List[str]] = None,
) -> BlenderMcpServer:
    """Start the Blender MCP server (creates a singleton if not running).

    Args:
        port: TCP port to listen on (default 8765).
        extra_skill_paths: Additional skill directories beyond built-ins.

    Returns:
        The running :class:`BlenderMcpServer` instance.
    """
    global _server  # noqa: PLW0603
    if _server is not None and _server.is_running():
        logger.info("BlenderMcpServer already running on port %d", _server.port)
        return _server

    _server = BlenderMcpServer(port=port, extra_skill_paths=extra_skill_paths)
    _server.start()
    logger.info("BlenderMcpServer started on http://127.0.0.1:%d/mcp", port)
    return _server


def stop_server() -> None:
    """Stop the running Blender MCP server."""
    global _server  # noqa: PLW0603
    if _server is None:
        return
    _server.stop()
    _server = None
    logger.info("BlenderMcpServer stopped")


def get_server() -> Optional[BlenderMcpServer]:
    """Return the current server instance, or *None* if not started."""
    return _server
