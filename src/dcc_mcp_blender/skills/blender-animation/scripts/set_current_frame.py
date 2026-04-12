"""Set the current animation frame in Blender."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def set_current_frame(frame: int) -> dict:
    """Set the current animation frame.

    Args:
        frame: Frame number to set as current.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        bpy.context.scene.frame_set(frame)
        return skill_success(
            f"Current frame set to {frame}",
            frame_current=bpy.context.scene.frame_current,
            prompt="Frame set. Use set_keyframe to insert keyframes at this position.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to set current frame to {frame}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`set_current_frame`."""
    return set_current_frame(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
