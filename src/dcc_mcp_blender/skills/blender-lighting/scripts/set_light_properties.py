"""Set properties on a Blender light."""

from __future__ import annotations

from typing import List, Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def set_light_properties(
    name: str,
    energy: Optional[float] = None,
    color: Optional[List[float]] = None,
    radius: Optional[float] = None,
) -> dict:
    """Set light properties.

    Args:
        name: Name of the light object.
        energy: Light energy in watts.
        color: [R, G, B] color values (0-1).
        radius: Light radius/size (for POINT and SPOT lights).

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(name)
        if obj is None:
            return skill_error(f"Object not found: {name}", f"No object named '{name}'.")
        if obj.type != "LIGHT":
            return skill_error(f"{name} is not a light", f"Object type is {obj.type}, expected LIGHT.")

        light = obj.data
        if energy is not None:
            light.energy = energy
        if color:
            light.color = color[:3]
        if radius is not None and hasattr(light, "shadow_soft_size"):
            light.shadow_soft_size = radius

        return skill_success(
            f"Light properties updated: {name}",
            object_name=name,
            energy=light.energy,
            color=list(light.color),
            prompt="Light updated. Use render_scene to see the changes.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to set light properties: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`set_light_properties`."""
    return set_light_properties(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
