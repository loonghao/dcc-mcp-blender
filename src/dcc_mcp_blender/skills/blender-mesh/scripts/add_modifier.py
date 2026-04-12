"""Add a modifier to a Blender mesh object."""

from __future__ import annotations

from typing import Any, Dict, Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def add_modifier(
    object_name: str,
    modifier_type: str,
    name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> dict:
    """Add a modifier to a mesh object.

    Args:
        object_name: Name of the mesh object.
        modifier_type: Blender modifier type, e.g. SUBSURF, MIRROR, ARRAY,
            SOLIDIFY, BEVEL, BOOLEAN, DECIMATE, etc.
        name: Optional name for the modifier. Defaults to Blender's auto-name.
        properties: Optional dict of modifier property overrides, e.g.
            {"levels": 2} for SUBSURF.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            return skill_error(f"Object not found: {object_name}", f"No object named '{object_name}'.")
        if obj.type != "MESH":
            return skill_error(
                f"{object_name} is not a mesh",
                f"Modifiers can only be added to MESH objects, got {obj.type}.",
            )

        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new(name=name or modifier_type.capitalize(), type=modifier_type.upper())

        if properties:
            for key, value in properties.items():
                if hasattr(mod, key):
                    setattr(mod, key, value)

        return skill_success(
            f"Added {modifier_type} modifier to {object_name}",
            object_name=object_name,
            modifier_name=mod.name,
            modifier_type=mod.type,
            prompt="Modifier added. Use apply_modifier to bake it permanently.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to add modifier to {object_name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`add_modifier`."""
    return add_modifier(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
