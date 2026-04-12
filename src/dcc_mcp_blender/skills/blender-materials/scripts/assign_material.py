"""Assign a material to a Blender object."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def assign_material(object_name: str, material_name: str, slot_index: int = 0) -> dict:
    """Assign a material to an object's material slot.

    Args:
        object_name: Name of the object to assign the material to.
        material_name: Name of the material to assign.
        slot_index: Material slot index (default 0).

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            return skill_error(f"Object not found: {object_name}", f"No object named '{object_name}'.")

        mat = bpy.data.materials.get(material_name)
        if mat is None:
            return skill_error(f"Material not found: {material_name}", f"No material named '{material_name}'.")

        if obj.type != "MESH":
            return skill_error(
                f"Object {object_name} is not a mesh",
                f"Materials can only be assigned to MESH objects, got {obj.type}.",
            )

        # Ensure enough material slots
        while len(obj.material_slots) <= slot_index:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.material_slot_add()

        obj.material_slots[slot_index].material = mat
        return skill_success(
            f"Assigned {material_name} to {object_name}",
            object_name=object_name,
            material_name=material_name,
            slot_index=slot_index,
            prompt="Material assigned successfully.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to assign material to {object_name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`assign_material`."""
    return assign_material(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
