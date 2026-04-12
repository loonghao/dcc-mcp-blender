"""Get mesh geometry information from a Blender object."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def get_mesh_info(object_name: str) -> dict:
    """Return vertex, edge, and face counts for a mesh object.

    Args:
        object_name: Name of the mesh object.

    Returns:
        ActionResultModel dict with geometry statistics.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            return skill_error(f"Object not found: {object_name}", f"No object named '{object_name}'.")
        if obj.type != "MESH":
            return skill_error(f"{object_name} is not a mesh", f"Object type is {obj.type}.")

        mesh = obj.data
        info = {
            "object_name": object_name,
            "mesh_name": mesh.name,
            "vertex_count": len(mesh.vertices),
            "edge_count": len(mesh.edges),
            "face_count": len(mesh.polygons),
            "uv_layer_count": len(mesh.uv_layers),
            "vertex_color_count": len(mesh.vertex_colors) if hasattr(mesh, "vertex_colors") else 0,
            "material_count": len(mesh.materials),
        }
        return skill_success(
            f"Mesh info: {object_name}",
            **info,
            prompt="Use add_modifier or blender-objects skills to modify the mesh.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to get mesh info for {object_name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`get_mesh_info`."""
    return get_mesh_info(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
