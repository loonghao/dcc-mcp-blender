"""E2E tests for blender-mesh and blender-collection skills.

Requires a real Blender Python interpreter.

Run::

    blender --background --python -m pytest tests/e2e/test_mesh_e2e.py -- -v
"""

from __future__ import annotations

import pytest

bpy = pytest.importorskip("bpy", reason="bpy not available — run inside Blender Python interpreter")

pytestmark = pytest.mark.e2e

from tests.e2e.conftest import load_skill  # noqa: E402


def _new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


# ── Mesh skills ───────────────────────────────────────────────────────────────


class TestMeshSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_get_mesh_info(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_name = bpy.context.active_object.name
        mod = load_skill("blender-mesh", "get_mesh_info")
        result = mod.get_mesh_info(object_name=cube_name)
        assert result["success"] is True
        ctx = result["context"]
        assert ctx["vertex_count"] == 8
        assert ctx["edge_count"] == 12
        assert ctx["face_count"] == 6

    def test_add_subsurf_modifier(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_name = bpy.context.active_object.name
        mod = load_skill("blender-mesh", "add_modifier")
        result = mod.add_modifier(object_name=cube_name, modifier_type="SUBSURF")
        assert result["success"] is True
        obj = bpy.data.objects[cube_name]
        assert any(m.type == "SUBSURF" for m in obj.modifiers)

    def test_add_bevel_modifier(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_name = bpy.context.active_object.name
        mod = load_skill("blender-mesh", "add_modifier")
        result = mod.add_modifier(object_name=cube_name, modifier_type="BEVEL")
        assert result["success"] is True
        obj = bpy.data.objects[cube_name]
        assert any(m.type == "BEVEL" for m in obj.modifiers)

    def test_add_solidify_modifier(self):
        bpy.ops.mesh.primitive_plane_add()
        plane_name = bpy.context.active_object.name
        mod = load_skill("blender-mesh", "add_modifier")
        result = mod.add_modifier(object_name=plane_name, modifier_type="SOLIDIFY")
        assert result["success"] is True
        obj = bpy.data.objects[plane_name]
        assert any(m.type == "SOLIDIFY" for m in obj.modifiers)

    def test_list_modifiers(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_name = bpy.context.active_object.name
        # Add two modifiers
        bpy.data.objects[cube_name].modifiers.new(name="SubSurf", type="SUBSURF")
        bpy.data.objects[cube_name].modifiers.new(name="Bevel", type="BEVEL")
        mod = load_skill("blender-mesh", "list_modifiers")
        result = mod.list_modifiers(object_name=cube_name)
        assert result["success"] is True
        assert result["context"]["count"] == 2

    def test_apply_modifier(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_name = bpy.context.active_object.name
        obj = bpy.data.objects[cube_name]
        obj.modifiers.new(name="SubSurf", type="SUBSURF")
        mod = load_skill("blender-mesh", "apply_modifier")
        result = mod.apply_modifier(object_name=cube_name, modifier_name="SubSurf")
        assert result["success"] is True
        # After applying, the modifier should no longer exist
        assert not any(m.name == "SubSurf" for m in bpy.data.objects[cube_name].modifiers)

    def test_get_mesh_info_nonexistent_object(self):
        mod = load_skill("blender-mesh", "get_mesh_info")
        result = mod.get_mesh_info(object_name="NonExistentObject_XYZ")
        assert result["success"] is False


# ── Collection skills ─────────────────────────────────────────────────────────


class TestCollectionSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_create_collection(self):
        mod = load_skill("blender-collection", "create_collection")
        result = mod.create_collection(name="E2ECollection")
        assert result["success"] is True
        assert "E2ECollection" in bpy.data.collections

    def test_list_collections(self):
        bpy.data.collections.new("ColA")
        bpy.data.collections.new("ColB")
        bpy.context.scene.collection.children.link(bpy.data.collections["ColA"])
        bpy.context.scene.collection.children.link(bpy.data.collections["ColB"])
        mod = load_skill("blender-collection", "list_collections")
        result = mod.list_collections()
        assert result["success"] is True
        names = [c["name"] for c in result["context"]["collections"]]
        assert "ColA" in names
        assert "ColB" in names

    def test_link_object_to_collection(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_name = bpy.context.active_object.name
        col = bpy.data.collections.new("LinkTestCol")
        bpy.context.scene.collection.children.link(col)
        mod = load_skill("blender-collection", "link_to_collection")
        result = mod.link_to_collection(object_name=cube_name, collection_name="LinkTestCol")
        assert result["success"] is True
        assert cube_name in [o.name for o in bpy.data.collections["LinkTestCol"].objects]
