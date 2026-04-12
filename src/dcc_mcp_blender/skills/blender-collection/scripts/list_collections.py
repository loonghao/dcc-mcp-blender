"""List all collections in the Blender scene."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def list_collections() -> dict:
    """List all collections in the current scene.

    Returns:
        ActionResultModel dict with collections list.
    """
    try:
        import bpy

        def _collect(col, depth=0) -> dict:
            return {
                "name": col.name,
                "object_count": len(col.objects),
                "objects": [o.name for o in col.objects],
                "children": [_collect(c, depth + 1) for c in col.children],
            }

        root = bpy.context.scene.collection
        hierarchy = _collect(root)
        flat = [col.name for col in bpy.data.collections]

        return skill_success(
            f"Found {len(flat)} collections",
            collections=flat,
            hierarchy=hierarchy,
            count=len(flat),
            prompt="Use create_collection or link_to_collection to organize objects.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to list collections")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`list_collections`."""
    return list_collections(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
