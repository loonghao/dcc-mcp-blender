"""Link an object to a Blender collection."""

from __future__ import annotations

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def link_to_collection(object_name: str, collection_name: str) -> dict:
    """Link an object to a collection.

    Args:
        object_name: Name of the object to link.
        collection_name: Name of the target collection.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            return skill_error(f"Object not found: {object_name}", f"No object named '{object_name}'.")

        col = bpy.data.collections.get(collection_name)
        if col is None:
            return skill_error(f"Collection not found: {collection_name}", f"No collection named '{collection_name}'.")

        if obj.name not in col.objects:
            col.objects.link(obj)

        return skill_success(
            f"Linked {object_name} to {collection_name}",
            object_name=object_name,
            collection_name=collection_name,
            prompt="Object linked to collection.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to link {object_name} to {collection_name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`link_to_collection`."""
    return link_to_collection(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
