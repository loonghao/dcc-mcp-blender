"""Blender MCP server — embeds a Streamable HTTP MCP server inside Blender.

Usage (inside Blender Python console or startup script)::

    import dcc_mcp_blender
    dcc_mcp_blender.start_server()        # default port 8765
    dcc_mcp_blender.stop_server()
"""

from __future__ import annotations

import logging
import os
import pathlib
from typing import List, Optional

from dcc_mcp_core import (
    ActionRegistry,
    McpHttpConfig,
    McpHttpServer,
    scan_and_load,
)

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

_DCC_NAME = "blender"


# ── path collection helper ────────────────────────────────────────────────────


def _collect_skill_paths(extra_paths: Optional[List[str]] = None) -> List[str]:
    """Collect all skill directory paths in priority order.

    Priority (highest → lowest):
    1. Paths passed via *extra_paths*
    2. Built-in skills bundled with this package
    3. ``DCC_MCP_BLENDER_SKILL_PATHS`` env var (colon/semicolon separated)
    4. ``DCC_MCP_SKILL_PATHS`` env var (generic fallback)

    Returns:
        Deduplicated list of existing directory paths as strings.
    """
    candidates: List[str] = list(extra_paths or [])

    # Built-ins
    if _BUILTIN_SKILLS_DIR.is_dir():
        candidates.append(str(_BUILTIN_SKILLS_DIR))

    # Env vars
    for raw in (
        os.environ.get(_ENV_EXTRA_SKILL_PATHS, ""),
        os.environ.get(_ENV_GENERIC_SKILL_PATHS, ""),
    ):
        if not raw:
            continue
        # On Windows, use os.pathsep (';'); on Unix use ':'.
        # Also accept ';' explicitly as a universal separator.
        sep = ";" if ";" in raw else os.pathsep
        for part in raw.split(sep):
            part = part.strip()
            if part:
                candidates.append(part)

    # Deduplicate, only keep existing dirs
    seen: set = set()
    result: List[str] = []
    for p in candidates:
        if p not in seen and pathlib.Path(p).is_dir():
            seen.add(p)
            result.append(p)
    return result


# ── server class ─────────────────────────────────────────────────────────────


class BlenderMcpServer:
    """MCP server embedded inside Blender.

    Wraps :class:`dcc_mcp_core.McpHttpServer` and adds Blender-specific
    skill discovery and lifecycle helpers.

    Attributes:
        port: TCP port to listen on (default :data:`DEFAULT_PORT`).
        extra_skill_paths: Additional skill directories to load on start.
    """

    def __init__(
        self,
        port: int = DEFAULT_PORT,
        extra_skill_paths: Optional[List[str]] = None,
    ) -> None:
        self.port = port
        self._extra_skill_paths: List[str] = extra_skill_paths or []
        self._handle = None  # McpServerHandle when running
        self._server: Optional[McpHttpServer] = None

    # ── skill path collection ──────────────────────────────────────────────

    def _collect_skill_paths(self) -> List[str]:
        return _collect_skill_paths(self._extra_skill_paths)

    # ── lifecycle ──────────────────────────────────────────────────────────

    def start(self) -> "BlenderMcpServer":
        """Start the MCP HTTP server. Idempotent.

        Returns:
            *self* for chaining.
        """
        if self._handle is not None:
            return self

        skill_paths = self._collect_skill_paths()
        logger.debug("BlenderMcpServer: loading skills from %s", skill_paths)

        # Build ActionRegistry + load skills
        registry = ActionRegistry()
        scan_and_load(extra_paths=skill_paths, dcc_name=_DCC_NAME)

        cfg = McpHttpConfig(
            port=self.port,
            server_name=SERVER_NAME,
            server_version=SERVER_VERSION,
        )
        self._server = McpHttpServer(registry, cfg)
        self._handle = self._server.start()

        # Update port in case it was 0 (OS-assigned)
        if hasattr(self._handle, "port"):
            _port = self._handle.port
            self.port = _port() if callable(_port) else _port

        logger.info(
            "BlenderMcpServer started on %s",
            self._handle.mcp_url() if hasattr(self._handle, "mcp_url") else f"port {self.port}",
        )
        return self

    def stop(self) -> None:
        """Stop the running server."""
        if self._handle is not None:
            try:
                self._handle.shutdown()
            except Exception:
                pass
            self._handle = None
        self._server = None
        logger.info("BlenderMcpServer stopped")

    def is_running(self) -> bool:
        """Return True if the server is currently running."""
        return self._handle is not None

    def mcp_url(self) -> Optional[str]:
        """Return the MCP HTTP URL, or None if not running."""
        if self._handle is None:
            return None
        if hasattr(self._handle, "mcp_url"):
            return self._handle.mcp_url()
        return f"http://127.0.0.1:{self.port}/mcp"


# ── module-level singleton helpers ────────────────────────────────────────────

_server_instance: Optional[BlenderMcpServer] = None


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
    global _server_instance  # noqa: PLW0603
    if _server_instance is not None and _server_instance.is_running():
        return _server_instance

    _server_instance = BlenderMcpServer(port=port, extra_skill_paths=extra_skill_paths)
    _server_instance.start()
    return _server_instance


def stop_server() -> None:
    """Stop the running Blender MCP server."""
    global _server_instance  # noqa: PLW0603
    if _server_instance is None:
        return
    _server_instance.stop()
    _server_instance = None


def get_server() -> Optional[BlenderMcpServer]:
    """Return the current server instance, or *None* if not started."""
    return _server_instance
