"""Open a Blender scene file from disk."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def open_scene(filepath: str) -> dict:
    """Open a Blender .blend file from disk.

    Args:
        filepath: Absolute path to the .blend file to open.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        bpy.ops.wm.open_mainfile(filepath=filepath)
        return skill_success(
            f"Opened scene: {filepath}",
            filepath=filepath,
            scene_name=bpy.context.scene.name,
            prompt="Scene opened. Use list_objects to see the scene contents.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to open scene: {filepath}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`open_scene`."""
    return open_scene(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
