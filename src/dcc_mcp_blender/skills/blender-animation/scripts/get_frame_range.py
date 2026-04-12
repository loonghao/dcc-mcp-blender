"""Get the current animation frame range."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def get_frame_range() -> dict:
    """Return the current animation frame range and current frame.

    Returns:
        ActionResultModel dict with frame_start, frame_end, frame_current.
    """
    try:
        import bpy

        scene = bpy.context.scene
        return skill_success(
            "Frame range retrieved",
            frame_start=scene.frame_start,
            frame_end=scene.frame_end,
            frame_current=scene.frame_current,
            fps=scene.render.fps,
            prompt="Use set_frame_range to change the frame range.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to get frame range")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`get_frame_range`."""
    return get_frame_range(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
