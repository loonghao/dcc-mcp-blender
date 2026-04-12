"""Unit tests for blender-render skill scripts (bpy mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from tests.conftest import load_and_call, make_mock_bpy


class TestGetRenderInfo:
    def test_returns_engine_and_resolution(self):
        bpy = make_mock_bpy()
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.context.scene.camera = None

        result = load_and_call("blender-render/scripts/get_render_info.py", bpy)
        assert result["success"] is True
        ctx = result["context"]
        assert ctx["engine"] == "CYCLES"
        assert ctx["resolution_x"] == 1920
        assert ctx["resolution_y"] == 1080

    def test_returns_cycles_samples(self):
        bpy = make_mock_bpy()
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.cycles = MagicMock()
        bpy.context.scene.cycles.samples = 128
        bpy.context.scene.cycles.device = "GPU"

        result = load_and_call("blender-render/scripts/get_render_info.py", bpy)
        assert result["success"] is True
        assert result["context"]["cycles_samples"] == 128


class TestSetRenderSettings:
    def test_set_engine(self):
        bpy = make_mock_bpy()
        result = load_and_call(
            "blender-render/scripts/set_render_settings.py", bpy, engine="CYCLES"
        )
        assert result["success"] is True
        assert bpy.context.scene.render.engine == "CYCLES"

    def test_set_resolution(self):
        bpy = make_mock_bpy()
        result = load_and_call(
            "blender-render/scripts/set_render_settings.py",
            bpy,
            resolution_x=2560,
            resolution_y=1440,
        )
        assert result["success"] is True
        assert bpy.context.scene.render.resolution_x == 2560
        assert bpy.context.scene.render.resolution_y == 1440

    def test_invalid_engine_returns_error(self):
        bpy = make_mock_bpy()
        result = load_and_call(
            "blender-render/scripts/set_render_settings.py", bpy, engine="INVALID_ENGINE"
        )
        assert result["success"] is False

    def test_set_output_path(self):
        bpy = make_mock_bpy()
        result = load_and_call(
            "blender-render/scripts/set_render_settings.py", bpy, output_path="/tmp/render/"
        )
        assert result["success"] is True
        assert bpy.context.scene.render.filepath == "/tmp/render/"

    def test_set_samples_cycles(self):
        bpy = make_mock_bpy()
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.cycles = MagicMock()
        result = load_and_call(
            "blender-render/scripts/set_render_settings.py", bpy, samples=256
        )
        assert result["success"] is True
        assert bpy.context.scene.cycles.samples == 256


class TestRenderScene:
    def test_render_calls_bpy_ops(self):
        bpy = make_mock_bpy()
        bpy.context.scene.render.filepath = "/tmp/output.png"

        result = load_and_call("blender-render/scripts/render_scene.py", bpy)
        assert result["success"] is True
        bpy.ops.render.render.assert_called_once()

    def test_render_with_output_path(self):
        bpy = make_mock_bpy()
        bpy.context.scene.render.filepath = ""

        result = load_and_call(
            "blender-render/scripts/render_scene.py", bpy, output_path="/custom/output.png"
        )
        assert result["success"] is True
        assert bpy.context.scene.render.filepath == "/custom/output.png"
