"""Create a new light object in Blender."""

from __future__ import annotations

from typing import List, Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success

VALID_LIGHT_TYPES = {"POINT", "SUN", "AREA", "SPOT"}


def create_light(
    light_type: str = "POINT",
    name: Optional[str] = None,
    location: Optional[List[float]] = None,
    energy: float = 1000.0,
    color: Optional[List[float]] = None,
) -> dict:
    """Create a new light in the scene.

    Args:
        light_type: Type of light: POINT, SUN, AREA, or SPOT.
        name: Optional name for the light object.
        location: [x, y, z] position. Defaults to [0, 0, 3].
        energy: Light energy/intensity in watts.
        color: [R, G, B] light color (0-1). Default: white.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        light_type = light_type.upper()
        if light_type not in VALID_LIGHT_TYPES:
            return skill_error(
                f"Invalid light type: {light_type}",
                f"Valid types: {', '.join(sorted(VALID_LIGHT_TYPES))}",
            )

        loc = location or [0.0, 0.0, 3.0]
        light_data = bpy.data.lights.new(name=name or f"{light_type.capitalize()}Light", type=light_type)
        light_data.energy = energy
        if color:
            light_data.color = color[:3]

        obj = bpy.data.objects.new(name=name or light_data.name, object_data=light_data)
        obj.location = loc
        bpy.context.scene.collection.objects.link(obj)

        return skill_success(
            f"Created {light_type} light: {obj.name}",
            object_name=obj.name,
            light_type=light_type,
            energy=energy,
            location=loc,
            prompt="Light created. Use set_light_properties to adjust intensity or color.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to create {light_type} light")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`create_light`."""
    return create_light(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
