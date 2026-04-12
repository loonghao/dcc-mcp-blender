"""Delete an object from the Blender scene."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def delete_object(name: str) -> dict:
    """Delete an object from the current scene.

    Args:
        name: Name of the object to delete.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(name)
        if obj is None:
            return skill_error(f"Object not found: {name}", f"No object named '{name}' in the scene.")

        bpy.data.objects.remove(obj, do_unlink=True)
        return skill_success(
            f"Deleted object: {name}",
            object_name=name,
            prompt="Object deleted. Use list_objects to see the updated scene.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to delete object: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`delete_object`."""
    return delete_object(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
