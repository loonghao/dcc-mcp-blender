"""Move an object to a specified location."""

from __future__ import annotations

from typing import List

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def move_object(name: str, location: List[float]) -> dict:
    """Move an object to the specified [x, y, z] location.

    Args:
        name: Name of the object to move.
        location: [x, y, z] coordinates.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(name)
        if obj is None:
            return skill_error(f"Object not found: {name}", f"No object named '{name}' in the scene.")

        obj.location = location
        return skill_success(
            f"Moved {name} to {location}",
            object_name=name,
            location=list(obj.location),
            prompt="Object moved. Use get_object_info to verify the new position.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to move object: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`move_object`."""
    return move_object(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
