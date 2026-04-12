"""Set the base color of a Blender material."""

from __future__ import annotations

from typing import List

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def set_material_color(material_name: str, color: List[float]) -> dict:
    """Set the base color of a Principled BSDF material.

    Args:
        material_name: Name of the material to modify.
        color: [R, G, B] or [R, G, B, A] color values (0.0 - 1.0).

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        mat = bpy.data.materials.get(material_name)
        if mat is None:
            return skill_error(f"Material not found: {material_name}", f"No material named '{material_name}'.")

        if not mat.use_nodes:
            return skill_error(
                f"Material {material_name} does not use nodes",
                "Enable use_nodes on the material first.",
            )

        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            return skill_error(
                f"No Principled BSDF node in {material_name}",
                "This skill only supports Principled BSDF materials.",
            )

        rgba = list(color) if len(color) == 4 else list(color) + [1.0]
        bsdf.inputs["Base Color"].default_value = rgba
        return skill_success(
            f"Set color on {material_name}",
            material_name=material_name,
            color=rgba,
            prompt="Color updated. Use render_scene to see the result.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to set color on {material_name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`set_material_color`."""
    return set_material_color(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
