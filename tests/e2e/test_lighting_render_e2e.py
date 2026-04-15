"""E2E tests for blender-lighting and blender-render skills.

Requires a real Blender Python interpreter.

Run::

    blender --background --python -m pytest tests/e2e/test_lighting_render_e2e.py -- -v
"""

from __future__ import annotations

import pytest

bpy = pytest.importorskip("bpy", reason="bpy not available — run inside Blender Python interpreter")

pytestmark = pytest.mark.e2e

from tests.e2e.conftest import load_skill  # noqa: E402


def _new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


# ── blender-lighting ──────────────────────────────────────────────────────────


class TestLightingSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_create_point_light(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="POINT", name="E2EPoint")
        assert result["success"] is True
        assert "E2EPoint" in bpy.data.objects
        assert bpy.data.objects["E2EPoint"].type == "LIGHT"
        assert bpy.data.objects["E2EPoint"].data.type == "POINT"

    def test_create_sun_light(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="SUN", name="E2ESun")
        assert result["success"] is True
        assert bpy.data.objects["E2ESun"].data.type == "SUN"

    def test_create_spot_light(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="SPOT", name="E2ESpot")
        assert result["success"] is True
        assert bpy.data.objects["E2ESpot"].data.type == "SPOT"

    def test_create_area_light(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="AREA", name="E2EArea")
        assert result["success"] is True
        assert bpy.data.objects["E2EArea"].data.type == "AREA"

    def test_create_light_with_energy(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="POINT", name="BrightLight", energy=2000.0)
        assert result["success"] is True
        assert abs(bpy.data.objects["BrightLight"].data.energy - 2000.0) < 1.0

    def test_create_light_at_location(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="POINT", name="LocLight", location=[1.0, 2.0, 5.0])
        assert result["success"] is True
        loc = bpy.data.objects["LocLight"].location
        assert abs(loc.x - 1.0) < 1e-4
        assert abs(loc.z - 5.0) < 1e-4

    def test_create_light_invalid_type(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="LASER", name="BadLight")
        assert result["success"] is False

    def test_set_light_energy(self):
        bpy.ops.object.light_add(type="POINT")
        light_name = bpy.context.active_object.name
        mod = load_skill("blender-lighting", "set_light_properties")
        result = mod.set_light_properties(name=light_name, energy=500.0)
        assert result["success"] is True
        assert abs(bpy.data.objects[light_name].data.energy - 500.0) < 1.0

    def test_set_light_color(self):
        bpy.ops.object.light_add(type="POINT")
        light_name = bpy.context.active_object.name
        mod = load_skill("blender-lighting", "set_light_properties")
        result = mod.set_light_properties(name=light_name, color=[1.0, 0.0, 0.0])
        assert result["success"] is True
        color = bpy.data.objects[light_name].data.color
        assert abs(color[0] - 1.0) < 1e-4
        assert abs(color[1] - 0.0) < 1e-4

    def test_set_light_not_found(self):
        mod = load_skill("blender-lighting", "set_light_properties")
        result = mod.set_light_properties(name="NoSuchLight_XYZ", energy=100.0)
        assert result["success"] is False

    def test_list_lights(self):
        bpy.ops.object.light_add(type="POINT")
        bpy.ops.object.light_add(type="SUN")
        mod = load_skill("blender-lighting", "list_lights")
        result = mod.list_lights()
        assert result["success"] is True
        assert result["context"]["count"] >= 2
        for light in result["context"]["lights"]:
            assert light["type"] == "LIGHT"

    def test_list_lights_empty_scene(self):
        mod = load_skill("blender-lighting", "list_lights")
        result = mod.list_lights()
        assert result["success"] is True
        assert result["context"]["count"] == 0


# ── blender-render ────────────────────────────────────────────────────────────


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
        assert "resolution_y" in ctx

    def test_set_render_resolution(self):
        mod = load_skill("blender-render", "set_render_settings")
        result = mod.set_render_settings(resolution_x=1280, resolution_y=720)
        assert result["success"] is True
        scene = bpy.context.scene
        assert scene.render.resolution_x == 1280
        assert scene.render.resolution_y == 720

    def test_set_render_engine_cycles(self):
        mod = load_skill("blender-render", "set_render_settings")
        result = mod.set_render_settings(engine="CYCLES")
        assert result["success"] is True
        assert bpy.context.scene.render.engine == "CYCLES"

    def test_set_render_engine_eevee(self):
        mod = load_skill("blender-render", "set_render_settings")
        result = mod.set_render_settings(engine="BLENDER_EEVEE")
        assert result["success"] is True
        assert bpy.context.scene.render.engine == "BLENDER_EEVEE"

    def test_set_render_engine_invalid(self):
        mod = load_skill("blender-render", "set_render_settings")
        result = mod.set_render_settings(engine="INVALID_ENGINE_XYZ")
        assert result["success"] is False

    def test_set_output_path(self, tmp_path):
        mod = load_skill("blender-render", "set_render_settings")
        out = str(tmp_path / "render_")
        result = mod.set_render_settings(output_path=out)
        assert result["success"] is True
        assert bpy.context.scene.render.filepath == out

    def test_set_cycles_samples(self):
        bpy.context.scene.render.engine = "CYCLES"
        mod = load_skill("blender-render", "set_render_settings")
        result = mod.set_render_settings(samples=64)
        assert result["success"] is True
        assert bpy.context.scene.cycles.samples == 64

    def test_render_scene_to_file(self, tmp_path):
        """Render a minimal scene (workbench, 64×64) to verify render_scene runs."""
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.camera_add()
        bpy.context.scene.camera = bpy.context.active_object
        scene = bpy.context.scene
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.render.resolution_x = 64
        scene.render.resolution_y = 64
        scene.render.resolution_percentage = 100

        out_path = str(tmp_path / "e2e_render.png")
        mod = load_skill("blender-render", "render_scene")
        result = mod.render_scene(output_path=out_path, write_still=True)
        assert result["success"] is True
        assert (tmp_path / "e2e_render.png").exists()
