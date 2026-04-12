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

    for name in ["skill_success", "skill_error", "skill_exception", "skill_entry"]:
        assert hasattr(dcc_mcp_blender, name), f"Missing: {name}"
