"""Tests for BlenderMcpServer and module-level helpers."""

from __future__ import annotations

import tempfile
from unittest.mock import patch

# ── helpers ───────────────────────────────────────────────────────────────────


def _builtin_skills_dir() -> str:
    from pathlib import Path

    return str(Path(__file__).parent.parent / "src" / "dcc_mcp_blender" / "skills")


# ── BlenderMcpServer unit tests ───────────────────────────────────────────────


class TestBlenderMcpServerBasic:
    def test_instantiation(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer(port=0)
        assert server is not None

    def test_default_port(self):
        from dcc_mcp_blender.server import DEFAULT_PORT, BlenderMcpServer

        server = BlenderMcpServer()
        assert server.port == DEFAULT_PORT

    def test_custom_port(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer(port=19999)
        assert server.port == 19999

    def test_extra_skill_paths_stored(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer(extra_skill_paths=["/tmp/extra"])
        assert "/tmp/extra" in server._extra_skill_paths

    def test_not_running_initially(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer()
        assert not server.is_running()

    def test_mcp_url_none_when_not_running(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer()
        assert server.mcp_url() is None


class TestSkillPathCollection:
    """_collect_skill_paths respects all path sources."""

    def test_builtin_always_included(self):
        from dcc_mcp_blender.server import _BUILTIN_SKILLS_DIR, BlenderMcpServer

        server = BlenderMcpServer()
        paths = server._collect_skill_paths()
        assert str(_BUILTIN_SKILLS_DIR) in paths

    def test_extra_paths_take_priority(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        with tempfile.TemporaryDirectory() as tmp:
            server = BlenderMcpServer(extra_skill_paths=[tmp])
            paths = server._collect_skill_paths()
            assert paths[0] == tmp

    def test_env_var_blender_skill_paths(self):
        from dcc_mcp_blender.server import _ENV_EXTRA_SKILL_PATHS, BlenderMcpServer

        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict("os.environ", {_ENV_EXTRA_SKILL_PATHS: tmp}):
                server = BlenderMcpServer()
                paths = server._collect_skill_paths()
                assert tmp in paths

    def test_env_var_generic_skill_paths(self):
        from dcc_mcp_blender.server import _ENV_GENERIC_SKILL_PATHS, BlenderMcpServer

        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict("os.environ", {_ENV_GENERIC_SKILL_PATHS: tmp}):
                server = BlenderMcpServer()
                paths = server._collect_skill_paths()
                assert tmp in paths

    def test_blender_env_before_generic_env(self):
        from dcc_mcp_blender.server import (
            _ENV_EXTRA_SKILL_PATHS,
            _ENV_GENERIC_SKILL_PATHS,
            BlenderMcpServer,
        )

        with tempfile.TemporaryDirectory() as app_tmp, tempfile.TemporaryDirectory() as global_tmp:
            with patch.dict(
                "os.environ",
                {
                    _ENV_EXTRA_SKILL_PATHS: app_tmp,
                    _ENV_GENERIC_SKILL_PATHS: global_tmp,
                },
            ):
                server = BlenderMcpServer()
                paths = server._collect_skill_paths()
                assert app_tmp in paths
                assert global_tmp in paths
                assert paths.index(app_tmp) < paths.index(global_tmp)

    def test_nonexistent_paths_excluded(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer(extra_skill_paths=["/nonexistent/path/xyz"])
        paths = server._collect_skill_paths()
        assert "/nonexistent/path/xyz" not in paths

    def test_no_duplicates(self):
        from dcc_mcp_blender.server import _BUILTIN_SKILLS_DIR, BlenderMcpServer

        builtin = str(_BUILTIN_SKILLS_DIR)
        server = BlenderMcpServer(extra_skill_paths=[builtin])
        paths = server._collect_skill_paths()
        assert paths.count(builtin) == 1


class TestServerLifecycle:
    """Start/stop lifecycle tests using a real McpHttpServer."""

    def test_start_and_stop(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer(port=0)
        server.start()
        assert server.is_running()
        url = server.mcp_url()
        assert url is not None
        assert "http://127.0.0.1:" in url
        server.stop()
        assert not server.is_running()

    def test_start_idempotent(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer(port=0)
        server.start()
        port_before = server.port
        server.start()  # second call should be no-op
        assert server.port == port_before
        server.stop()

    def test_stop_noop_when_not_running(self):
        from dcc_mcp_blender.server import BlenderMcpServer

        server = BlenderMcpServer(port=0)
        server.stop()  # should not raise


class TestModuleSingleton:
    """Module-level start_server / stop_server singleton pattern."""

    def setup_method(self):
        # ensure clean state
        from dcc_mcp_blender import server as srv_mod

        srv_mod._server_instance = None

    def teardown_method(self):
        from dcc_mcp_blender import server as srv_mod

        if srv_mod._server_instance is not None:
            srv_mod.stop_server()

    def test_start_stop(self):
        from dcc_mcp_blender.server import get_server, start_server, stop_server

        server = start_server(port=0)
        assert server is not None
        assert get_server() is server
        stop_server()
        assert get_server() is None

    def test_start_idempotent(self):
        from dcc_mcp_blender.server import start_server, stop_server

        s1 = start_server(port=0)
        s2 = start_server(port=0)
        assert s1 is s2
        stop_server()

    def test_get_server_none_when_not_running(self):
        from dcc_mcp_blender.server import get_server

        assert get_server() is None

    def test_stop_noop_when_not_running(self):
        from dcc_mcp_blender.server import stop_server

        stop_server()  # should not raise
        stop_server()  # should not raise
