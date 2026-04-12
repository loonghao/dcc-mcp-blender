"""List all lights in the current Blender scene."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def list_lights() -> dict:
    """List all light objects in the current scene.

    Returns:
        ActionResultModel dict with lights list.
    """
    try:
        import bpy

        lights = [
            {
                "name": obj.name,
                "light_type": obj.data.type,
                "energy": obj.data.energy,
                "color": list(obj.data.color),
                "location": list(obj.location),
            }
            for obj in bpy.data.objects
            if obj.type == "LIGHT"
        ]
        return skill_success(
            f"Found {len(lights)} lights",
            lights=lights,
            count=len(lights),
            prompt="Use create_light to add more lights or set_light_properties to modify them.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to list lights")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`list_lights`."""
    return list_lights(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
