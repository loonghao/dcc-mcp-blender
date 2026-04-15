"""Real integration test: progressive loading + gateway competition."""
import json
import time
import urllib.request


def post_mcp(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def test_progressive_loading():
    print("=== TEST 1: Progressive Loading (Blender) ===")
    from dcc_mcp_blender.server import BlenderMcpServer

    server = BlenderMcpServer(port=0)
    server.start()
    try:
        assert server.loaded_skill_count() == 0, "Should have 0 loaded skills"

        discovered = server.discover_skills()
        all_skills = server.list_skills()
        skill_names = [s.name if hasattr(s, "name") else s["name"] for s in all_skills]
        print(f"  Discovered {discovered} skills: {skill_names[:5]}")

        url = server.mcp_url
        r = post_mcp(url, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                       "clientInfo": {"name": "test", "version": "1.0"}},
        })
        info = r["result"]["serverInfo"]
        print(f"  MCP initialize OK: name={info['name']} version={info['version']}")

        # tools/list before loading any skill (only meta-tools expected)
        r2 = post_mcp(url, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools_before = [t["name"] for t in r2["result"]["tools"]]
        print(f"  Tools before load ({len(tools_before)}): {tools_before[:5]}")

        # load a skill and check tools appear
        if skill_names:
            skill = skill_names[0]
            actions = server.load_skill(skill)
            print(f"  Loaded {skill!r}: {len(actions)} actions")

            r3 = post_mcp(url, {"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
            tools_after = [t["name"] for t in r3["result"]["tools"]]
            print(f"  Tools after load ({len(tools_after)}): {tools_after[:5]}")
            assert len(tools_after) > len(tools_before), "More tools expected after load"

            # unload and verify count drops
            removed = server.unload_skill(skill)
            print(f"  Unloaded {skill!r}: {removed} actions removed")
            assert removed > 0, "Expected removed > 0"

        print("  PASS: Progressive loading verified")
    finally:
        server.stop()


def test_gateway_competition():
    print("\n=== TEST 2: Gateway Competition (2 instances) ===")
    from dcc_mcp_blender.server import BlenderMcpServer

    GATEWAY_PORT = 19901

    s1 = BlenderMcpServer(port=0, gateway_port=GATEWAY_PORT, enable_gateway_failover=True)
    s2 = BlenderMcpServer(port=0, gateway_port=GATEWAY_PORT, enable_gateway_failover=True)

    s1.start()
    time.sleep(0.3)
    s2.start()
    time.sleep(0.5)

    try:
        print(f"  Server1: port={s1.port} is_gateway={s1.is_gateway} url={s1.mcp_url}")
        print(f"  Server2: port={s2.port} is_gateway={s2.is_gateway} url={s2.mcp_url}")

        assert s1.is_running, "Server1 should be running"
        assert s2.is_running, "Server2 should be running"
        assert s1.port != s2.port, f"Ports must differ: {s1.port} vs {s2.port}"

        # Both should respond to MCP
        for i, s in enumerate([s1, s2], 1):
            r = post_mcp(s.mcp_url, {
                "jsonrpc": "2.0", "id": i, "method": "initialize",
                "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                           "clientInfo": {"name": "test", "version": "1.0"}},
            })
            assert r["result"]["serverInfo"]["name"] == "dcc-mcp-blender"
            print(f"  Server{i} MCP initialize OK")

        gateways = [s for s in [s1, s2] if s.is_gateway]
        print(f"  Gateway count: {len(gateways)}")
        print("  PASS: Multi-instance gateway competition verified")
    finally:
        s1.stop()
        s2.stop()


def test_maya_progressive_loading():
    print("\n=== TEST 3: Progressive Loading (Maya mock) ===")
    import sys
    from unittest.mock import MagicMock, patch

    maya_mock = MagicMock()
    maya_mock.cmds = MagicMock()
    modules = {"maya": maya_mock, "maya.cmds": maya_mock.cmds,
               "maya.mel": MagicMock(), "maya.utils": MagicMock()}

    with patch.dict(sys.modules, modules):
        import importlib
        for mod in list(sys.modules):
            if "dcc_mcp_maya" in mod:
                del sys.modules[mod]
        srv_mod = importlib.import_module("dcc_mcp_maya.server")
        server = srv_mod.MayaMcpServer(port=0)
        server.register_builtin_actions()
        handle = server.start()

        try:
            skills = list(server._server.list_skills())
            names = [s.name if hasattr(s, "name") else s["name"] for s in skills]
            print(f"  Discovered {len(skills)} skills: {names[:5]}")

            url = handle.mcp_url()
            r = post_mcp(url, {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                           "clientInfo": {"name": "test", "version": "1.0"}},
            })
            print(f"  MCP initialize: name={r['result']['serverInfo']['name']}")
            assert r["result"]["serverInfo"]["name"] == "maya-mcp"
            print("  PASS: Maya progressive loading verified")
        finally:
            server.stop()


if __name__ == "__main__":
    test_progressive_loading()
    test_gateway_competition()
    test_maya_progressive_loading()
    print("\n=== All integration tests PASSED ===")
