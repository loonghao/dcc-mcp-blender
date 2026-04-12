"""Rotate an object by Euler angles (degrees)."""

from __future__ import annotations

import math
from typing import List

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def rotate_object(name: str, rotation: List[float]) -> dict:
    """Set the Euler rotation of an object.

    Args:
        name: Name of the object to rotate.
        rotation: [rx, ry, rz] rotation in **degrees**.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(name)
        if obj is None:
            return skill_error(f"Object not found: {name}", f"No object named '{name}' in the scene.")

        obj.rotation_euler = [math.radians(r) for r in rotation]
        actual_deg = [math.degrees(r) for r in obj.rotation_euler]
        return skill_success(
            f"Rotated {name}",
            object_name=name,
            rotation_degrees=actual_deg,
            prompt="Object rotated. Use get_object_info to verify the new rotation.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to rotate object: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`rotate_object`."""
    return rotate_object(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
