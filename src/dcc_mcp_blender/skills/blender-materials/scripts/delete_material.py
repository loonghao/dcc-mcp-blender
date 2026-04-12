"""Delete a material from Blender."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def delete_material(name: str) -> dict:
    """Delete a material by name.

    Args:
        name: Name of the material to delete.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        mat = bpy.data.materials.get(name)
        if mat is None:
            return skill_error(f"Material not found: {name}", f"No material named '{name}'.")

        bpy.data.materials.remove(mat)
        return skill_success(
            f"Deleted material: {name}",
            material_name=name,
            prompt="Material deleted. Use list_materials to verify.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to delete material: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`delete_material`."""
    return delete_material(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
