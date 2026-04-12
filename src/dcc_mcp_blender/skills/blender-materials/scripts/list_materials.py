"""List all materials in the current Blender scene."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def list_materials() -> dict:
    """List all materials in the current scene.

    Returns:
        ActionResultModel dict with material list.
    """
    try:
        import bpy

        materials = [
            {
                "name": mat.name,
                "use_nodes": mat.use_nodes,
                "users": mat.users,
            }
            for mat in bpy.data.materials
        ]
        return skill_success(
            f"Found {len(materials)} materials",
            materials=materials,
            count=len(materials),
            prompt="Use create_material or assign_material to manage materials.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to list materials")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`list_materials`."""
    return list_materials(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
