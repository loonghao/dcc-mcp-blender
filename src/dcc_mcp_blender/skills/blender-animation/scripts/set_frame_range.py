"""Set the animation frame range in Blender."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def set_frame_range(start: int, end: int) -> dict:
    """Set the animation frame range.

    Args:
        start: Start frame number.
        end: End frame number.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        if end < start:
            return skill_error("Invalid frame range", f"End frame ({end}) must be >= start frame ({start}).")

        scene = bpy.context.scene
        scene.frame_start = start
        scene.frame_end = end
        return skill_success(
            f"Frame range set: {start} - {end}",
            frame_start=start,
            frame_end=end,
            prompt="Frame range updated.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to set frame range")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`set_frame_range`."""
    return set_frame_range(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
