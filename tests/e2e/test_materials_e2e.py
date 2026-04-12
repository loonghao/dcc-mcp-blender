"""E2E tests for blender-materials and blender-render skills.

Requires a real Blender Python interpreter.

Run::

    blender --background --python -m pytest tests/e2e/test_materials_e2e.py -- -v
"""

from __future__ import annotations

import pytest

bpy = pytest.importorskip("bpy", reason="bpy not available — run inside Blender Python interpreter")

pytestmark = pytest.mark.e2e

from tests.e2e.conftest import load_skill  # noqa: E402


def _new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


class TestMaterialSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_create_material(self):
        mod = load_skill("blender-materials", "create_material")
        result = mod.create_material(name="E2EMat")
        assert result["success"] is True
        assert "E2EMat" in bpy.data.materials

    def test_create_material_with_color(self):
        mod = load_skill("blender-materials", "create_material")
        result = mod.create_material(name="RedMat", color=[1.0, 0.0, 0.0])
        assert result["success"] is True
        mat = bpy.data.materials["RedMat"]
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        color = bsdf.inputs["Base Color"].default_value
        assert abs(color[0] - 1.0) < 1e-4  # R
        assert abs(color[1] - 0.0) < 1e-4  # G

    def test_assign_material_to_mesh(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_name = bpy.context.active_object.name

        create_mod = load_skill("blender-materials", "create_material")
        create_mod.create_material(name="AssignMat")

        assign_mod = load_skill("blender-materials", "assign_material")
        result = assign_mod.assign_material(object_name=cube_name, material_name="AssignMat")
        assert result["success"] is True
        obj = bpy.data.objects[cube_name]
        assert obj.material_slots[0].material.name == "AssignMat"

    def test_set_material_color(self):
        create_mod = load_skill("blender-materials", "create_material")
        create_mod.create_material(name="ColorableMat")

        mod = load_skill("blender-materials", "set_material_color")
        result = mod.set_material_color(material_name="ColorableMat", color=[0.0, 0.0, 1.0])
        assert result["success"] is True

        mat = bpy.data.materials["ColorableMat"]
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        color = bsdf.inputs["Base Color"].default_value
        assert abs(color[2] - 1.0) < 1e-4  # B

    def test_list_materials(self):
        create_mod = load_skill("blender-materials", "create_material")
        create_mod.create_material(name="ListMat1")
        create_mod.create_material(name="ListMat2")

        list_mod = load_skill("blender-materials", "list_materials")
        result = list_mod.list_materials()
        assert result["success"] is True
        names = [m["name"] for m in result["context"]["materials"]]
        assert "ListMat1" in names
        assert "ListMat2" in names

    def test_delete_material(self):
        create_mod = load_skill("blender-materials", "create_material")
        create_mod.create_material(name="DeleteMat")
        assert "DeleteMat" in bpy.data.materials

        delete_mod = load_skill("blender-materials", "delete_material")
        result = delete_mod.delete_material(name="DeleteMat")
        assert result["success"] is True
        assert "DeleteMat" not in bpy.data.materials


class TestRenderSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_get_render_info(self):
        mod = load_skill("blender-render", "get_render_info")
        result = mod.get_render_info()
        assert result["success"] is True
        ctx = result["context"]
        assert "engine" in ctx
        assert "resolution_x" in ctx

    def test_set_render_resolution(self):
        mod = load_skill("blender-render", "set_render_settings")
        result = mod.set_render_settings(resolution_x=1280, resolution_y=720)
        assert result["success"] is True
        assert bpy.context.scene.render.resolution_x == 1280
        assert bpy.context.scene.render.resolution_y == 720

    def test_set_render_engine_cycles(self):
        mod = load_skill("blender-render", "set_render_settings")
        result = mod.set_render_settings(engine="CYCLES")
        assert result["success"] is True
        assert bpy.context.scene.render.engine == "CYCLES"

    def test_set_render_engine_eevee(self):
        mod = load_skill("blender-render", "set_render_settings")
        # EEVEE_NEXT for Blender 4.x
        for engine in ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"]:
            try:
                result = mod.set_render_settings(engine=engine)
                if result["success"]:
                    assert bpy.context.scene.render.engine in {
                        "BLENDER_EEVEE",
                        "BLENDER_EEVEE_NEXT",
                    }
                    break
            except Exception:
                continue

    def test_set_output_path(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            mod = load_skill("blender-render", "set_render_settings")
            result = mod.set_render_settings(output_path=tmp + "/out")
            assert result["success"] is True
            assert bpy.context.scene.render.filepath == tmp + "/out"
