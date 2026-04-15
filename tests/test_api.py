"""Tests for dcc_mcp_blender.api re-exports."""

from __future__ import annotations


def test_skill_success_importable():
    from dcc_mcp_blender.api import skill_success

    result = skill_success("all good", foo="bar")
    assert result["success"] is True
    assert result["message"] == "all good"
    assert result["context"]["foo"] == "bar"


def test_skill_error_importable():
    from dcc_mcp_blender.api import skill_error

    result = skill_error("oops", "something failed")
    assert result["success"] is False
    assert "oops" in result["message"]


def test_skill_exception_importable():
    from dcc_mcp_blender.api import skill_exception

    try:
        raise ValueError("test exc")
    except ValueError as e:
        result = skill_exception(e, message="wrapped")
    assert result["success"] is False
    assert "wrapped" in result["message"] or "test exc" in str(result)


def test_skill_entry_importable():
    from dcc_mcp_blender.api import skill_entry

    assert callable(skill_entry)


def test_all_exports_in_package():
    """Top-level package should expose all key API symbols."""
    import dcc_mcp_blender

    for name in [
        "skill_success",
        "skill_error",
        "skill_exception",
        "skill_entry",
        # server
        "BlenderMcpServer",
        "start_server",
        "stop_server",
        "get_server",
        # capabilities
        "blender_capabilities",
        "blender_capabilities_dict",
    ]:
        assert hasattr(dcc_mcp_blender, name), f"Missing export: {name}"


def test_blender_capabilities_importable():
    """blender_capabilities() returns a DccCapabilities with expected fields."""
    from dcc_mcp_blender.capabilities import blender_capabilities

    caps = blender_capabilities()
    assert caps.scene_manager is True
    assert caps.transform is True
    assert caps.hierarchy is True
    assert caps.render_capture is True
    assert caps.has_embedded_python is True


def test_blender_capabilities_dict():
    """blender_capabilities_dict() returns a serialisable dict."""
    from dcc_mcp_blender.capabilities import blender_capabilities_dict

    d = blender_capabilities_dict()
    assert isinstance(d, dict)
    assert d["scene_manager"] is True
    assert d["has_embedded_python"] is True
    assert isinstance(d["extensions"], dict)
    assert d["extensions"]["geometry_nodes"] is True
