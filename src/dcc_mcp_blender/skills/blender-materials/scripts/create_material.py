"""Create a new Principled BSDF material in Blender."""

from __future__ import annotations

from typing import List, Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def create_material(
    name: str,
    color: Optional[List[float]] = None,
    metallic: float = 0.0,
    roughness: float = 0.5,
    use_nodes: bool = True,
) -> dict:
    """Create a new material with Principled BSDF shader.

    Args:
        name: Name for the new material.
        color: [R, G, B] or [R, G, B, A] base color (0-1 range). Default: white.
        metallic: Metallic value (0.0 - 1.0).
        roughness: Roughness value (0.0 - 1.0).
        use_nodes: Whether to use the node-based shader system.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = use_nodes

        if use_nodes:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                if color:
                    rgba = list(color) if len(color) == 4 else list(color) + [1.0]
                    bsdf.inputs["Base Color"].default_value = rgba
                bsdf.inputs["Metallic"].default_value = metallic
                bsdf.inputs["Roughness"].default_value = roughness

        return skill_success(
            f"Created material: {name}",
            material_name=mat.name,
            use_nodes=use_nodes,
            prompt="Use assign_material to assign this material to an object.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to create material: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`create_material`."""
    return create_material(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
