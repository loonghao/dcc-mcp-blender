"""Set the active render camera in Blender."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def set_active_camera(name: str) -> dict:
    """Set the active render camera for the scene.

    Args:
        name: Name of the camera object to set as active.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(name)
        if obj is None:
            return skill_error(f"Object not found: {name}", f"No object named '{name}'.")
        if obj.type != "CAMERA":
            return skill_error(f"{name} is not a camera", f"Object type is {obj.type}, expected CAMERA.")

        bpy.context.scene.camera = obj
        return skill_success(
            f"Active camera set to: {name}",
            camera_name=name,
            prompt="Active camera updated. Use render_scene to render from this camera.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to set active camera: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`set_active_camera`."""
    return set_active_camera(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
