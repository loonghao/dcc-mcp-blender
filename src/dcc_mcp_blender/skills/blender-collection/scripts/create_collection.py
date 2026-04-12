"""Create a new collection in Blender."""

from __future__ import annotations

from typing import Optional

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success


def create_collection(name: str, parent_collection: Optional[str] = None) -> dict:
    """Create a new collection and link it to the scene.

    Args:
        name: Name for the new collection.
        parent_collection: Optional name of the parent collection. If None,
            links to the scene's root collection.

    Returns:
        ActionResultModel dict.
    """
    try:
        import bpy

        col = bpy.data.collections.new(name=name)

        if parent_collection:
            parent = bpy.data.collections.get(parent_collection)
            if parent is None:
                return skill_error(
                    f"Parent collection not found: {parent_collection}",
                    f"No collection named '{parent_collection}'.",
                )
            parent.children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)

        return skill_success(
            f"Created collection: {col.name}",
            collection_name=col.name,
            parent=parent_collection,
            prompt="Collection created. Use link_to_collection to add objects to it.",
        )
    except ImportError:
        return skill_error("Blender not available", "bpy could not be imported")
    except Exception as exc:
        return skill_exception(exc, message=f"Failed to create collection: {name}")


@skill_entry
def main(**kwargs) -> dict:
    """Entry point; delegates to :func:`create_collection`."""
    return create_collection(**kwargs)


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)
