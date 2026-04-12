"""Unit tests for blender-mesh skill scripts (bpy mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock

from tests.conftest import load_and_call, make_mock_bpy


def _make_mesh_obj(name="Cube", vertex_count=8, edge_count=12, face_count=6):
    obj = MagicMock()
    obj.name = name
    obj.type = "MESH"
    obj.data = MagicMock()
    obj.data.name = name
    obj.data.vertices = [MagicMock()] * vertex_count
    obj.data.edges = [MagicMock()] * edge_count
    obj.data.polygons = [MagicMock()] * face_count
    obj.data.uv_layers = []
    obj.data.materials = []
    obj.modifiers = MagicMock()
    obj.modifiers.__iter__ = MagicMock(return_value=iter([]))
    return obj


class TestGetMeshInfo:
    def test_returns_counts(self):
        bpy = make_mock_bpy()
        obj = _make_mesh_obj("Cube", 8, 12, 6)
        bpy.data.objects.get.return_value = obj

        result = load_and_call("blender-mesh/scripts/get_mesh_info.py", bpy, object_name="Cube")
        assert result["success"] is True
        ctx = result["context"]
        assert ctx["vertex_count"] == 8
        assert ctx["edge_count"] == 12
        assert ctx["face_count"] == 6

    def test_not_found_returns_error(self):
        bpy = make_mock_bpy()
        bpy.data.objects.get.return_value = None
        result = load_and_call("blender-mesh/scripts/get_mesh_info.py", bpy, object_name="Ghost")
        assert result["success"] is False

    def test_non_mesh_returns_error(self):
        bpy = make_mock_bpy()
        obj = MagicMock()
        obj.type = "LIGHT"
        bpy.data.objects.get.return_value = obj
        result = load_and_call("blender-mesh/scripts/get_mesh_info.py", bpy, object_name="Sun")
        assert result["success"] is False


class TestAddModifier:
    def test_adds_subsurf(self):
        bpy = make_mock_bpy()
        obj = _make_mesh_obj()
        bpy.data.objects.get.return_value = obj
        bpy.context.view_layer.objects.active = None

        mod = MagicMock()
        mod.name = "Subdivision"
        mod.type = "SUBSURF"
        obj.modifiers.new = MagicMock(return_value=mod)

        result = load_and_call(
            "blender-mesh/scripts/add_modifier.py",
            bpy,
            object_name="Cube",
            modifier_type="SUBSURF",
        )
        assert result["success"] is True
        obj.modifiers.new.assert_called_once()

    def test_object_not_found(self):
        bpy = make_mock_bpy()
        bpy.data.objects.get.return_value = None
        result = load_and_call(
            "blender-mesh/scripts/add_modifier.py",
            bpy,
            object_name="Ghost",
            modifier_type="SUBSURF",
        )
        assert result["success"] is False

    def test_non_mesh_returns_error(self):
        bpy = make_mock_bpy()
        obj = MagicMock()
        obj.type = "LIGHT"
        bpy.data.objects.get.return_value = obj
        result = load_and_call(
            "blender-mesh/scripts/add_modifier.py",
            bpy,
            object_name="Sun",
            modifier_type="SUBSURF",
        )
        assert result["success"] is False

    def test_properties_applied(self):
        bpy = make_mock_bpy()
        obj = _make_mesh_obj()
        bpy.data.objects.get.return_value = obj

        mod = MagicMock()
        mod.name = "Subdivision"
        mod.type = "SUBSURF"
        mod.levels = 1
        obj.modifiers.new = MagicMock(return_value=mod)

        load_and_call(
            "blender-mesh/scripts/add_modifier.py",
            bpy,
            object_name="Cube",
            modifier_type="SUBSURF",
            properties={"levels": 3},
        )
        assert mod.levels == 3


class TestApplyModifier:
    def test_applies_modifier(self):
        bpy = make_mock_bpy()
        obj = _make_mesh_obj()
        mod = MagicMock()
        mod.name = "Subdivision"
        bpy.data.objects.get.return_value = obj
        obj.modifiers.get = MagicMock(return_value=mod)
        bpy.context.view_layer.objects.active = None

        result = load_and_call(
            "blender-mesh/scripts/apply_modifier.py",
            bpy,
            object_name="Cube",
            modifier_name="Subdivision",
        )
        assert result["success"] is True
        bpy.ops.object.modifier_apply.assert_called_once_with(modifier="Subdivision")

    def test_modifier_not_found(self):
        bpy = make_mock_bpy()
        obj = _make_mesh_obj()
        bpy.data.objects.get.return_value = obj
        obj.modifiers.get = MagicMock(return_value=None)

        result = load_and_call(
            "blender-mesh/scripts/apply_modifier.py",
            bpy,
            object_name="Cube",
            modifier_name="Ghost",
        )
        assert result["success"] is False


class TestListModifiers:
    def test_returns_modifier_list(self):
        bpy = make_mock_bpy()
        obj = _make_mesh_obj()
        mod1 = MagicMock()
        mod1.name = "Subdivision"
        mod1.type = "SUBSURF"
        mod1.show_viewport = True
        mod1.show_render = True

        obj.modifiers.__iter__ = MagicMock(return_value=iter([mod1]))
        bpy.data.objects.get.return_value = obj

        result = load_and_call("blender-mesh/scripts/list_modifiers.py", bpy, object_name="Cube")
        assert result["success"] is True
        assert result["context"]["count"] == 1
        assert result["context"]["modifiers"][0]["name"] == "Subdivision"

    def test_no_modifiers(self):
        bpy = make_mock_bpy()
        obj = _make_mesh_obj()
        obj.modifiers.__iter__ = MagicMock(return_value=iter([]))
        bpy.data.objects.get.return_value = obj

        result = load_and_call("blender-mesh/scripts/list_modifiers.py", bpy, object_name="Cube")
        assert result["success"] is True
        assert result["context"]["count"] == 0
