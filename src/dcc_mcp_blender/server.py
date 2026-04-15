"""Blender MCP server — embeds a Streamable HTTP MCP server inside Blender.

Uses ``dcc_mcp_core.create_skill_manager()`` to wire up the skill catalog,
progressive loading, and the built-in auto-gateway (first-wins port competition
for multi-instance setups).

Usage (inside Blender Python console or startup script)::

    import dcc_mcp_blender

    # Start with default port (auto-gateway: first instance wins 8765)
    server = dcc_mcp_blender.start_server()

    # Progressive loading — discover skills without loading them immediately
    n = server.discover_skills()        # scan paths, register tool metadata
    server.load_skill("blender-scene")  # lazy-load a specific skill on demand

    dcc_mcp_blender.stop_server()
"""

from __future__ import annotations

import logging
import os
import pathlib
from typing import Any, Dict, List, Optional

from dcc_mcp_core import (
    McpHttpConfig,
    McpHttpServer,
    create_skill_manager,
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
        # On Windows use ';'; on Unix use ':'. Also accept ';' as universal separator.
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

    Wraps :class:`dcc_mcp_core.McpHttpServer` (created via
    :func:`dcc_mcp_core.create_skill_manager`) and adds Blender-specific skill
    discovery, progressive loading, and lifecycle helpers.

    Multi-instance / gateway
    ------------------------
    dcc-mcp-core ≥ 0.12.20 implements an **auto-gateway** with first-wins port
    competition: the first Blender process to bind the well-known port (8765)
    becomes the gateway; subsequent instances start on ephemeral ports and
    register themselves automatically.  No extra configuration is required —
    just call :meth:`start` from each Blender instance.

    Progressive loading
    -------------------
    Skills can be discovered (metadata only, no Python import) and loaded
    on demand::

        server.discover_skills()             # fast: scan SKILL.md files
        server.load_skill("blender-scene")   # lazy: import scripts only now
        server.unload_skill("blender-scene") # unload to free memory

    Attributes:
        port: TCP port the server is listening on (updated after :meth:`start`).
        extra_skill_paths: Extra skill directories beyond built-ins.
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
        """Start the MCP HTTP server.  Idempotent — returns *self* if already running.

        Uses :func:`dcc_mcp_core.create_skill_manager` which automatically:
        * Creates an ``ActionRegistry`` and ``ActionDispatcher``.
        * Discovers skills from all configured skill paths.
        * Wires up the ``SkillCatalog`` for progressive loading.

        Returns:
            *self* for chaining.
        """
        if self._handle is not None:
            return self

        skill_paths = self._collect_skill_paths()
        logger.debug("BlenderMcpServer: skill paths = %s", skill_paths)

        cfg = McpHttpConfig(
            port=self.port,
            server_name=SERVER_NAME,
            server_version=SERVER_VERSION,
        )

        # create_skill_manager handles ActionRegistry + SkillCatalog setup and
        # discovers skills from env vars + extra_paths in one call.
        self._server = create_skill_manager(
            app_name=_DCC_NAME,
            config=cfg,
            extra_paths=skill_paths,
            dcc_name=_DCC_NAME,
        )

        self._handle = self._server.start()

        # Update port — ServerHandle.port is a property in dcc-mcp-core ≥ 0.12.20
        self.port = self._handle.port

        logger.info("BlenderMcpServer started on %s", self._handle.mcp_url())
        return self

    def stop(self) -> None:
        """Gracefully stop the running server."""
        if self._handle is not None:
            try:
                self._handle.shutdown()
            except Exception:
                pass
            self._handle = None
        self._server = None
        logger.info("BlenderMcpServer stopped")

    def is_running(self) -> bool:
        """Return ``True`` if the server is currently running."""
        return self._handle is not None

    def mcp_url(self) -> Optional[str]:
        """Return the MCP HTTP URL, or ``None`` if not running."""
        if self._handle is None:
            return None
        return self._handle.mcp_url()

    # ── progressive skill loading ──────────────────────────────────────────

    def discover_skills(
        self,
        extra_paths: Optional[List[str]] = None,
    ) -> int:
        """Scan skill directories and register tool metadata without importing scripts.

        This is the *discover* phase of progressive loading — only SKILL.md
        metadata is parsed; no Python skill scripts are imported yet.  Call
        :meth:`load_skill` to import a specific skill on demand.

        Args:
            extra_paths: Additional directories to scan beyond the configured paths.

        Returns:
            Number of newly discovered skills (0 if server is not running).
        """
        if self._server is None:
            logger.warning("discover_skills called before server was started")
            return 0
        paths = self._collect_skill_paths()
        if extra_paths:
            paths = list(extra_paths) + paths
        count = self._server.discover(extra_paths=paths, dcc_name=_DCC_NAME)
        logger.debug("BlenderMcpServer: discovered %d new skill(s)", count)
        return count

    def load_skill(self, skill_name: str) -> List[str]:
        """Load a skill by name — imports scripts and registers tools.

        Part of the progressive loading API: call :meth:`discover_skills` first
        to register metadata, then call this to import a specific skill only
        when it is actually needed.

        Args:
            skill_name: Skill name as declared in ``SKILL.md`` (e.g. ``"blender-scene"``).

        Returns:
            List of action names that were registered.

        Raises:
            RuntimeError: If the server is not running.
            ValueError: If the skill is not found.
        """
        if self._server is None:
            raise RuntimeError("Server is not running — call start() first")
        actions = self._server.load_skill(skill_name)
        logger.debug("BlenderMcpServer: loaded skill %r → actions: %s", skill_name, actions)
        return actions

    def unload_skill(self, skill_name: str) -> int:
        """Unload a skill, removing its tools from the registry.

        Args:
            skill_name: Skill name to unload.

        Returns:
            Number of actions removed.

        Raises:
            RuntimeError: If the server is not running.
            ValueError: If the skill is not loaded.
        """
        if self._server is None:
            raise RuntimeError("Server is not running — call start() first")
        count = self._server.unload_skill(skill_name)
        logger.debug("BlenderMcpServer: unloaded skill %r (%d action(s) removed)", skill_name, count)
        return count

    def list_skills(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all discovered skills with their load status.

        Args:
            status: Optional filter — ``"loaded"`` or ``"unloaded"``.

        Returns:
            List of dicts with skill status information, or ``[]`` if not running.
        """
        if self._server is None:
            return []
        return list(self._server.list_skills(status=status))  # type: ignore[arg-type]

    def find_skills(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dcc: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for skills matching the given criteria.

        Args:
            query: Free-text query matched against skill name/description.
            tags: Required tags (skill must have all).
            dcc: DCC filter (defaults to ``"blender"``).

        Returns:
            List of matching skill metadata dicts, or ``[]`` if not running.
        """
        if self._server is None:
            return []
        # The Rust binding requires a Sequence for tags; pass [] instead of None
        return list(self._server.find_skills(query=query, tags=tags or [], dcc=dcc or _DCC_NAME))  # type: ignore[arg-type]

    def is_skill_loaded(self, skill_name: str) -> bool:
        """Return ``True`` if the named skill is currently loaded."""
        if self._server is None:
            return False
        return self._server.is_loaded(skill_name)

    def loaded_skill_count(self) -> int:
        """Return the number of currently loaded skills."""
        if self._server is None:
            return 0
        return self._server.loaded_count()


# ── module-level singleton helpers ────────────────────────────────────────────

_server_instance: Optional[BlenderMcpServer] = None


def start_server(
    port: int = DEFAULT_PORT,
    extra_skill_paths: Optional[List[str]] = None,
) -> BlenderMcpServer:
    """Start the Blender MCP server (creates a process-level singleton).

    The first call creates and starts the server.  Subsequent calls return the
    existing instance without restarting it.

    Multi-instance support (gateway mode)
    --------------------------------------
    dcc-mcp-core ≥ 0.12.20 implements first-wins port competition: if port 8765
    is already taken by another Blender process, this instance starts on a
    random port and registers with the gateway automatically.

    Args:
        port: Preferred TCP port (default 8765; use 0 for a random port).
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
    """Return the current server instance, or ``None`` if not started."""
    return _server_instance
