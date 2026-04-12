"""Blender DCC capabilities declaration."""

from __future__ import annotations

from dcc_mcp_core.models import DccCapabilities

_BLENDER_CAPS = DccCapabilities(
    dcc_name="blender",
    supported_features=[
        "scene_manager",
        "transform",
        "hierarchy",
        "selection",
        "render_capture",
        "snapshot",
        "undo_redo",
        "file_operations",
        "has_embedded_python",
        "progress_reporting",
        "scene_info",
        "modifier_stack",
        "node_editor",
        "geometry_nodes",
        "shader_nodes",
        "particle_system",
        "physics_simulation",
        "animation_system",
        "collection_management",
    ],
)

BLENDER_CAPABILITIES_DICT: dict = _BLENDER_CAPS.model_dump()


def blender_capabilities() -> DccCapabilities:
    """Return the capabilities descriptor for Blender.

    Returns:
        DccCapabilities instance describing all supported Blender features.
    """
    return _BLENDER_CAPS
