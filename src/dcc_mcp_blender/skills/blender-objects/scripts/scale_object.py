"""Scale an object."""

from __future__ import annotations

from typing import List, Union

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def scale_object(name: str, scale: Union[float, List[float]]) -> dict:
    """Set the scale of a Blender object.

    Args:
        name: Name of the object to scale.
        scale: Uniform scale factor (float) or [sx, sy, sz] list.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(name)
        if obj is None:
            return skill_error(f"Object not found: {name}", f"No object named '{name}' in the scene.")

        if isinstance(scale, (int, float)):
            obj.scale = [float(scale)] * 3
        else:
            obj.scale = scale

        return skill_success(
            f"Scaled {name}",
            object_name=name,
            scale=list(obj.scale),
            prompt="Object scaled. Use get_object_info to verify the new scale.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to scale object: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`scale_object`."""
    return scale_object(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
