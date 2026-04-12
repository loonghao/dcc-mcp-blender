"""Return a hierarchical description of the current Blender scene."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def get_scene_info() -> dict:
    """Return scene hierarchy and statistics.

    Returns:
        ActionResultModel dict with scene structure information.
    """
    try:
        import bpy

        scene = bpy.context.scene

        # Build collection hierarchy
        def _collection_info(col) -> dict:
            return {
                "name": col.name,
                "objects": [o.name for o in col.objects],
                "children": [_collection_info(c) for c in col.children],
            }

        collections = _collection_info(scene.collection)

        info = {
            "scene_name": scene.name,
            "frame_current": scene.frame_current,
            "frame_range": [scene.frame_start, scene.frame_end],
            "fps": scene.render.fps,
            "active_camera": scene.camera.name if scene.camera else None,
            "total_objects": len(scene.objects),
            "objects_by_type": {},
            "collections": collections,
        }

        # Count by type
        for obj in scene.objects:
            info["objects_by_type"][obj.type] = info["objects_by_type"].get(obj.type, 0) + 1

        return skill_success(
            "Scene info retrieved",
            **info,
            prompt="Use list_objects to see all objects or blender-objects skill to manipulate them.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to get scene info")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`get_scene_info`."""
    return get_scene_info(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
