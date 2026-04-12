"""E2E tests for blender-scripting, blender-animation, blender-lighting, blender-camera skills.

Requires a real Blender Python interpreter.

Run::

    blender --background --python -m pytest tests/e2e/test_scripting_e2e.py -- -v
"""

from __future__ import annotations

import tempfile

import pytest

bpy = pytest.importorskip("bpy", reason="bpy not available — run inside Blender Python interpreter")

pytestmark = pytest.mark.e2e

from tests.e2e.conftest import load_skill  # noqa: E402


def _new_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


class TestScriptingSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_get_blender_info(self):
        mod = load_skill("blender-scripting", "get_blender_info")
        result = mod.get_blender_info()
        assert result["success"] is True
        ctx = result["context"]
        assert "blender_version" in ctx
        assert "python_version" in ctx
        assert ctx["is_background"] is True  # running --background in CI

    def test_execute_python_simple(self):
        mod = load_skill("blender-scripting", "execute_python")
        result = mod.execute_python(code="x = 1 + 1\nresult = x")
        assert result["success"] is True
        assert result["context"]["result"] == "2"

    def test_execute_python_print(self):
        mod = load_skill("blender-scripting", "execute_python")
        result = mod.execute_python(code="print('e2e output')")
        assert result["success"] is True
        assert "e2e output" in result["context"]["stdout"]

    def test_execute_python_bpy_access(self):
        mod = load_skill("blender-scripting", "execute_python")
        result = mod.execute_python(code="import bpy; result = bpy.app.version_string")
        assert result["success"] is True
        assert result["context"]["result"] is not None

    def test_execute_python_create_object(self):
        mod = load_skill("blender-scripting", "execute_python")
        result = mod.execute_python(
            code="import bpy; bpy.ops.mesh.primitive_cube_add(); result = bpy.context.active_object.name"
        )
        assert result["success"] is True
        cube_name = result["context"]["result"]
        assert cube_name in bpy.data.objects

    def test_execute_python_syntax_error(self):
        mod = load_skill("blender-scripting", "execute_python")
        result = mod.execute_python(code="def broken(: pass")
        assert result["success"] is False

    def test_execute_script_file(self):
        mod = load_skill("blender-scripting", "execute_script_file")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import bpy\nresult = bpy.app.version_string\nprint('from file:', result)\n")
            fpath = f.name

        result = mod.execute_script_file(filepath=fpath)
        assert result["success"] is True
        assert "from file:" in result["context"]["stdout"]

    def test_execute_missing_file(self):
        mod = load_skill("blender-scripting", "execute_script_file")
        result = mod.execute_script_file(filepath="/nonexistent/script.py")
        assert result["success"] is False


class TestAnimationSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_get_frame_range(self):
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 250
        mod = load_skill("blender-animation", "get_frame_range")
        result = mod.get_frame_range()
        assert result["success"] is True
        assert result["context"]["frame_start"] == 1
        assert result["context"]["frame_end"] == 250

    def test_set_frame_range(self):
        mod = load_skill("blender-animation", "set_frame_range")
        result = mod.set_frame_range(start=10, end=200)
        assert result["success"] is True
        assert bpy.context.scene.frame_start == 10
        assert bpy.context.scene.frame_end == 200

    def test_set_current_frame(self):
        mod = load_skill("blender-animation", "set_current_frame")
        result = mod.set_current_frame(frame=42)
        assert result["success"] is True
        assert bpy.context.scene.frame_current == 42

    def test_set_keyframe(self):
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        cube_name = bpy.context.active_object.name
        mod = load_skill("blender-animation", "set_keyframe")
        result = mod.set_keyframe(object_name=cube_name, frame=1)
        assert result["success"] is True
        # Verify animation data was created
        obj = bpy.data.objects[cube_name]
        assert obj.animation_data is not None
        assert obj.animation_data.action is not None


class TestLightingSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_create_point_light(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="POINT", name="E2EPoint", energy=1000.0)
        assert result["success"] is True
        assert "E2EPoint" in bpy.data.objects
        assert bpy.data.objects["E2EPoint"].type == "LIGHT"

    def test_create_sun_light(self):
        mod = load_skill("blender-lighting", "create_light")
        result = mod.create_light(light_type="SUN", name="E2ESun")
        assert result["success"] is True
        assert bpy.data.objects["E2ESun"].data.type == "SUN"

    def test_set_light_energy(self):
        bpy.ops.object.light_add(type="POINT", location=(0, 0, 3))
        light_name = bpy.context.active_object.name
        mod = load_skill("blender-lighting", "set_light_properties")
        result = mod.set_light_properties(name=light_name, energy=5000.0)
        assert result["success"] is True
        assert abs(bpy.data.objects[light_name].data.energy - 5000.0) < 1.0

    def test_list_lights(self):
        bpy.ops.object.light_add(type="POINT")
        bpy.ops.object.light_add(type="SUN")
        mod = load_skill("blender-lighting", "list_lights")
        result = mod.list_lights()
        assert result["success"] is True
        assert result["context"]["count"] >= 2


class TestCameraSkillsE2E:
    def setup_method(self):
        _new_scene()

    def test_create_camera(self):
        mod = load_skill("blender-camera", "create_camera")
        result = mod.create_camera(name="E2ECam", lens=50.0)
        assert result["success"] is True
        assert "E2ECam" in bpy.data.objects
        assert bpy.data.objects["E2ECam"].type == "CAMERA"

    def test_set_active_camera(self):
        bpy.ops.object.camera_add()
        cam_name = bpy.context.active_object.name
        mod = load_skill("blender-camera", "set_active_camera")
        result = mod.set_active_camera(name=cam_name)
        assert result["success"] is True
        assert bpy.context.scene.camera.name == cam_name

    def test_set_camera_properties_lens(self):
        bpy.ops.object.camera_add()
        cam_name = bpy.context.active_object.name
        mod = load_skill("blender-camera", "set_camera_properties")
        result = mod.set_camera_properties(name=cam_name, lens=85.0)
        assert result["success"] is True
        assert abs(bpy.data.objects[cam_name].data.lens - 85.0) < 1e-4

    def test_list_cameras(self):
        bpy.ops.object.camera_add()
        bpy.ops.object.camera_add()
        mod = load_skill("blender-camera", "list_cameras")
        result = mod.list_cameras()
        assert result["success"] is True
        assert result["context"]["count"] >= 2
