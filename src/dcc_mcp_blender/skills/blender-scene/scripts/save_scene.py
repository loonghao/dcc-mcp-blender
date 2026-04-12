"""Save the current Blender scene."""

from __future__ import annotations

from typing import Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def save_scene(filepath: Optional[str] = None) -> dict:
    """Save the current Blender scene.

    Args:
        filepath: Optional path to save the scene to. If None, saves to the
            current file path. If the scene has never been saved, this is required.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        if filepath:
            bpy.ops.wm.save_as_mainfile(filepath=filepath)
            saved_path = filepath
        else:
            current_path = bpy.data.filepath
            if not current_path:
                return skill_error(
                    "No filepath specified",
                    "The scene has not been saved yet. Please provide a filepath.",
                )
            bpy.ops.wm.save_mainfile()
            saved_path = current_path

        return skill_success(
            f"Scene saved to {saved_path}",
            filepath=saved_path,
            prompt="Scene saved successfully.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to save scene")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`save_scene`."""
    return save_scene(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
