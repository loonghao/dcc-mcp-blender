"""Blender DCC capabilities declaration."""

from __future__ import annotations

from dcc_mcp_core import DccCapabilities

# Blender supports all four cross-DCC protocol traits and has embedded Python.
# Additional Blender-specific capabilities are listed in the ``extensions`` dict.
_BLENDER_CAPS = DccCapabilities(
    scene_manager=True,
    transform=True,
    hierarchy=True,
    render_capture=True,
    selection=True,
    snapshot=True,
    undo_redo=True,
    file_operations=True,
    has_embedded_python=True,
    progress_reporting=True,
    scene_info=True,
    extensions={
        "modifier_stack": True,
        "node_editor": True,
        "geometry_nodes": True,
        "shader_nodes": True,
        "particle_system": True,
        "physics_simulation": True,
        "animation_system": True,
        "collection_management": True,
    },
)


def blender_capabilities() -> DccCapabilities:
    """Return the capabilities descriptor for Blender.

    Returns:
        DccCapabilities instance describing all supported Blender features.
    """
    return _BLENDER_CAPS


def blender_capabilities_dict() -> dict:
    """Return the Blender capabilities as a plain Python dict.

    Returns:
        dict with capability fields suitable for JSON serialisation.
    """
    caps = _BLENDER_CAPS
    return {
        "scene_manager": caps.scene_manager,
        "transform": caps.transform,
        "hierarchy": caps.hierarchy,
        "render_capture": caps.render_capture,
        "selection": caps.selection,
        "snapshot": caps.snapshot,
        "undo_redo": caps.undo_redo,
        "file_operations": caps.file_operations,
        "has_embedded_python": caps.has_embedded_python,
        "progress_reporting": caps.progress_reporting,
        "scene_info": caps.scene_info,
        "extensions": caps.extensions,
    }
