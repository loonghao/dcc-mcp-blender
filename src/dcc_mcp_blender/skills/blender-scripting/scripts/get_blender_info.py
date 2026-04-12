"""Get Blender version and Python environment information."""

from __future__ import annotations

import sys

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def get_blender_info() -> dict:
    """Return Blender version and Python environment details.

    Returns:
        ActionResultModel dict with version and environment info.
    """
    try:
        import bpy

        info = {
            "blender_version": ".".join(str(v) for v in bpy.app.version),
            "blender_version_string": bpy.app.version_string,
            "blender_build_date": bpy.app.build_date.decode() if isinstance(bpy.app.build_date, bytes) else str(bpy.app.build_date),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "platform": sys.platform,
            "binary_path": bpy.app.binary_path,
            "is_background": bpy.app.background,
        }
        return skill_success(
            "Blender info retrieved",
            **info,
            prompt="Use execute_python to run custom Blender Python code.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message="Failed to get Blender info")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`get_blender_info`."""
    return get_blender_info(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
