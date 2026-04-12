"""Render the current Blender scene."""

from __future__ import annotations

from typing import Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def render_scene(
    output_path: Optional[str] = None,
    write_still: bool = True,
) -> dict:
    """Render the current scene.

    Args:
        output_path: File path for the rendered image. If None, uses the
            scene's current output path setting.
        write_still: If True, write the rendered image to disk.

    Returns:
        ActionResultModel dict with the output path.
    """
    try:
        import bpy

        scene = bpy.context.scene

        if output_path:
            scene.render.filepath = output_path

        bpy.ops.render.render(write_still=write_still)
        return skill_success(
            "Scene rendered",
            output_path=scene.render.filepath,
            write_still=write_still,
            prompt="Render complete. The image has been saved to the output path.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to render scene")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`render_scene`."""
    return render_scene(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
