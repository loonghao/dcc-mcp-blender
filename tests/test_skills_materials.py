"""Unit tests for blender-materials skill scripts (bpy mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from tests.conftest import load_and_call, make_mock_bpy


def _make_material(name="Material", use_nodes=True):
    mat = MagicMock()
    mat.name = name
    mat.use_nodes = use_nodes
    mat.users = 1
    # Mock Principled BSDF node
    bsdf = MagicMock()
    bsdf.inputs = {
        "Base Color": MagicMock(default_value=[1.0, 1.0, 1.0, 1.0]),
        "Metallic": MagicMock(default_value=0.0),
        "Roughness": MagicMock(default_value=0.5),
    }
    mat.node_tree.nodes.get = MagicMock(return_value=bsdf)
    return mat


class TestCreateMaterial:
    def test_creates_material(self):
        bpy = make_mock_bpy()
        mat = _make_material("RedMat")
        bpy.data.materials.new.return_value = mat

        result = load_and_call("blender-materials/scripts/create_material.py", bpy, name="RedMat")
        assert result["success"] is True
        bpy.data.materials.new.assert_called_once_with(name="RedMat")

    def test_sets_color_when_provided(self):
        bpy = make_mock_bpy()
        mat = _make_material("GreenMat")
        bpy.data.materials.new.return_value = mat

        result = load_and_call(
            "blender-materials/scripts/create_material.py",
            bpy,
            name="GreenMat",
            color=[0.0, 1.0, 0.0],
        )
        assert result["success"] is True

    def test_metallic_roughness_applied(self):
        bpy = make_mock_bpy()
        mat = _make_material()
        bpy.data.materials.new.return_value = mat

        result = load_and_call(
            "blender-materials/scripts/create_material.py",
            bpy,
            name="MetalMat",
            metallic=1.0,
            roughness=0.1,
        )
        assert result["success"] is True


class TestAssignMaterial:
    def test_assigns_to_mesh(self):
        bpy = make_mock_bpy()
        mat = _make_material("MyMat")
        obj = MagicMock()
        obj.name = "Cube"
        obj.type = "MESH"
        obj.material_slots = [MagicMock()]

        bpy.data.objects.get.return_value = obj
        bpy.data.materials.get.return_value = mat

        result = load_and_call(
            "blender-materials/scripts/assign_material.py",
            bpy,
            object_name="Cube",
            material_name="MyMat",
        )
        assert result["success"] is True

    def test_object_not_found(self):
        bpy = make_mock_bpy()
        bpy.data.objects.get.return_value = None
        bpy.data.materials.get.return_value = MagicMock()

        result = load_and_call(
            "blender-materials/scripts/assign_material.py",
            bpy,
            object_name="Ghost",
            material_name="Mat",
        )
        assert result["success"] is False

    def test_material_not_found(self):
        bpy = make_mock_bpy()
        obj = MagicMock()
        obj.type = "MESH"
        bpy.data.objects.get.return_value = obj
        bpy.data.materials.get.return_value = None

        result = load_and_call(
            "blender-materials/scripts/assign_material.py",
            bpy,
            object_name="Cube",
            material_name="GhostMat",
        )
        assert result["success"] is False

    def test_non_mesh_returns_error(self):
        bpy = make_mock_bpy()
        obj = MagicMock()
        obj.name = "Camera"
        obj.type = "CAMERA"
        bpy.data.objects.get.return_value = obj
        bpy.data.materials.get.return_value = MagicMock()

        result = load_and_call(
            "blender-materials/scripts/assign_material.py",
            bpy,
            object_name="Camera",
            material_name="Mat",
        )
        assert result["success"] is False


class TestSetMaterialColor:
    def test_sets_rgb_color(self):
        bpy = make_mock_bpy()
        mat = _make_material("ColorMat")
        bpy.data.materials.get.return_value = mat

        result = load_and_call(
            "blender-materials/scripts/set_material_color.py",
            bpy,
            material_name="ColorMat",
            color=[1.0, 0.0, 0.0],
        )
        assert result["success"] is True

    def test_material_not_found(self):
        bpy = make_mock_bpy()
        bpy.data.materials.get.return_value = None

        result = load_and_call(
            "blender-materials/scripts/set_material_color.py",
            bpy,
            material_name="Ghost",
            color=[1.0, 0.0, 0.0],
        )
        assert result["success"] is False

    def test_no_nodes_returns_error(self):
        bpy = make_mock_bpy()
        mat = _make_material(use_nodes=False)
        bpy.data.materials.get.return_value = mat

        result = load_and_call(
            "blender-materials/scripts/set_material_color.py",
            bpy,
            material_name="NoNodeMat",
            color=[1.0, 0.0, 0.0],
        )
        assert result["success"] is False


class TestListMaterials:
    def test_empty_returns_zero(self):
        bpy = make_mock_bpy(data_attrs={"materials": []})
        result = load_and_call("blender-materials/scripts/list_materials.py", bpy)
        assert result["success"] is True
        assert result["context"]["count"] == 0

    def test_lists_all_materials(self):
        mat1 = _make_material("Mat1")
        mat2 = _make_material("Mat2")
        bpy = make_mock_bpy(data_attrs={"materials": [mat1, mat2]})
        result = load_and_call("blender-materials/scripts/list_materials.py", bpy)
        assert result["success"] is True
        assert result["context"]["count"] == 2


class TestDeleteMaterial:
    def test_deletes_existing(self):
        bpy = make_mock_bpy()
        mat = _make_material("ToDelete")
        bpy.data.materials.get.return_value = mat

        result = load_and_call(
            "blender-materials/scripts/delete_material.py", bpy, name="ToDelete"
        )
        assert result["success"] is True
        bpy.data.materials.remove.assert_called_once_with(mat)

    def test_delete_nonexistent_returns_error(self):
        bpy = make_mock_bpy()
        bpy.data.materials.get.return_value = None

        result = load_and_call("blender-materials/scripts/delete_material.py", bpy, name="Ghost")
        assert result["success"] is False
