"""List all modifiers on a Blender object."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def list_modifiers(object_name: str) -> dict:
    """List all modifiers on a mesh object.

    Args:
        object_name: Name of the object to inspect.

    Returns:
        ActionResultModel dict with modifiers list.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            return skill_error(f"Object not found: {object_name}", f"No object named '{object_name}'.")

        modifiers = [
            {
                "name": mod.name,
                "type": mod.type,
                "show_viewport": mod.show_viewport,
                "show_render": mod.show_render,
            }
            for mod in obj.modifiers
        ]
        return skill_success(
            f"Found {len(modifiers)} modifiers on {object_name}",
            object_name=object_name,
            modifiers=modifiers,
            count=len(modifiers),
            prompt="Use add_modifier or apply_modifier to manage modifiers.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to list modifiers on {object_name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`list_modifiers`."""
    return list_modifiers(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
