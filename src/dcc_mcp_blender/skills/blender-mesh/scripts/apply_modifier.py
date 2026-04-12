"""Apply (bake) a modifier permanently to a Blender mesh."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def apply_modifier(object_name: str, modifier_name: str) -> dict:
    """Apply a modifier permanently to a mesh object.

    Args:
        object_name: Name of the mesh object.
        modifier_name: Name of the modifier to apply.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            return skill_error(f"Object not found: {object_name}", f"No object named '{object_name}'.")

        mod = obj.modifiers.get(modifier_name)
        if mod is None:
            return skill_error(
                f"Modifier not found: {modifier_name}",
                f"No modifier named '{modifier_name}' on '{object_name}'.",
            )

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        return skill_success(
            f"Applied modifier {modifier_name} on {object_name}",
            object_name=object_name,
            modifier_name=modifier_name,
            prompt="Modifier applied. The mesh has been updated permanently.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to apply modifier {modifier_name} on {object_name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`apply_modifier`."""
    return apply_modifier(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
