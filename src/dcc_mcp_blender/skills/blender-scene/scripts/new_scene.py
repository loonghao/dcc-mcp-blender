"""Create a new empty Blender scene."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def new_scene() -> dict:
    """Create a new Blender scene by loading the default startup file.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        bpy.ops.wm.read_factory_settings(use_empty=True)
        return skill_success(
            "New scene created",
            prompt="Check the result with list_objects or use related actions to continue.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to create new scene")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`new_scene`."""
    return new_scene(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
