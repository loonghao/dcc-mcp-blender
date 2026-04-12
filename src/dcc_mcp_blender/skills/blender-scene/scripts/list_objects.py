"""List all objects in the current Blender scene."""

from __future__ import annotations

from typing import Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def list_objects(object_type: Optional[str] = None) -> dict:
    """List objects in the current Blender scene.

    Args:
        object_type: Optional Blender object type filter, e.g. ``"MESH"``,
            ``"LIGHT"``, ``"CAMERA"``, ``"ARMATURE"``.

    Returns:
        ActionResultModel dict with ``context.objects`` list.
    """
    try:
        import bpy

        objects = bpy.data.objects
        if object_type:
            objects = [o for o in objects if o.type == object_type.upper()]
        else:
            objects = list(objects)

        result = [
            {
                "name": o.name,
                "type": o.type,
                "location": list(o.location),
                "visible": not o.hide_viewport,
            }
            for o in objects
        ]
        return skill_success(
            f"Found {len(result)} objects",
            objects=result,
            count=len(result),
            prompt="Use get_scene_info for a hierarchical view, or manipulate objects with the blender-objects skill.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to list objects")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`list_objects`."""
    return list_objects(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
