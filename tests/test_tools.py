"""Unit tests for USD tool layer — no LLM calls."""

from __future__ import annotations

from pathlib import Path

import pytest

from usdagent.tools.stage import create_stage, list_prims, open_stage, save_stage, get_stage_metadata


FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestStage:
    def test_create_stage(self, tmp_path: Path) -> None:
        path = str(tmp_path / "test.usda")
        result = create_stage(path)
        assert result == path

    def test_open_stage(self) -> None:
        path = str(FIXTURE_DIR / "simple_scene.usda")
        result = open_stage(path)
        assert result == path

    def test_open_nonexistent_stage_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            open_stage("/nonexistent/path/scene.usda")

    def test_list_prims(self) -> None:
        path = str(FIXTURE_DIR / "simple_scene.usda")
        open_stage(path)
        prims = list_prims(path)
        paths = [p.path for p in prims]
        assert "/World" in paths
        assert "/World/Floor" in paths

    def test_get_stage_metadata(self) -> None:
        path = str(FIXTURE_DIR / "simple_scene.usda")
        open_stage(path)
        meta = get_stage_metadata(path)
        assert meta.up_axis == "Y"
        assert meta.meters_per_unit == 1.0
        assert meta.prim_count > 0

    def test_save_stage(self, tmp_path: Path) -> None:
        src = str(FIXTURE_DIR / "simple_scene.usda")
        dest = str(tmp_path / "copy.usda")
        open_stage(src)
        save_stage(src, dest)
        assert Path(dest).exists()


class TestPrims:
    def test_create_prim(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        path = str(tmp_path / "prims.usda")
        create_stage(path)
        info = create_prim(path, "/World", "Xform")
        assert info.path == "/World"
        assert info.type_name == "Xform"

    def test_get_prim(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim, get_prim
        path = str(tmp_path / "get.usda")
        create_stage(path)
        create_prim(path, "/World", "Xform")
        info = get_prim(path, "/World")
        assert info.path == "/World"

    def test_delete_prim(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim, delete_prim, get_prim
        path = str(tmp_path / "del.usda")
        create_stage(path)
        create_prim(path, "/World", "Xform")
        create_prim(path, "/World/Child", "Xform")
        delete_prim(path, "/World/Child")
        with pytest.raises(ValueError):
            get_prim(path, "/World/Child")

    def test_delete_nonexistent_prim_raises(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import delete_prim
        path = str(tmp_path / "del2.usda")
        create_stage(path)
        with pytest.raises(ValueError):
            delete_prim(path, "/DoesNotExist")


class TestTransforms:
    def test_set_translate(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        from usdagent.tools.transforms import set_translate, get_world_transform
        path = str(tmp_path / "xform.usda")
        create_stage(path)
        create_prim(path, "/World", "Xform")
        set_translate(path, "/World", (1.0, 2.0, 3.0))
        mat = get_world_transform(path, "/World")
        assert len(mat.values) == 4

    def test_set_rotate(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        from usdagent.tools.transforms import set_rotate
        path = str(tmp_path / "rot.usda")
        create_stage(path)
        create_prim(path, "/World", "Xform")
        set_rotate(path, "/World", (0.0, 45.0, 0.0))

    def test_set_scale(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        from usdagent.tools.transforms import set_scale
        path = str(tmp_path / "scale.usda")
        create_stage(path)
        create_prim(path, "/World", "Xform")
        set_scale(path, "/World", (2.0, 2.0, 2.0))


class TestMaterials:
    def test_create_material(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        from usdagent.tools.materials import create_material
        path = str(tmp_path / "mat.usda")
        create_stage(path)
        create_prim(path, "/World", "Xform")
        create_prim(path, "/World/Looks", "Scope")
        mat = create_material(path, "/World/Looks/Concrete")
        assert mat.path == "/World/Looks/Concrete"
        assert mat.shader_type == "UsdPreviewSurface"

    def test_bind_material(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        from usdagent.tools.materials import create_material, bind_material
        path = str(tmp_path / "bind.usda")
        create_stage(path)
        create_prim(path, "/World", "Xform")
        create_prim(path, "/World/Looks", "Scope")
        create_prim(path, "/World/Floor", "Mesh")
        create_material(path, "/World/Looks/Concrete")
        bind_material(path, "/World/Floor", "/World/Looks/Concrete")


class TestValidation:
    def test_valid_stage(self) -> None:
        from usdagent.tools.validate import validate_stage
        path = str(FIXTURE_DIR / "simple_scene.usda")
        open_stage(path)
        report = validate_stage(path)
        assert isinstance(report.is_valid, bool)

    def test_check_layer_stack(self) -> None:
        from usdagent.tools.validate import check_layer_stack
        path = str(FIXTURE_DIR / "simple_scene.usda")
        open_stage(path)
        issues = check_layer_stack(path)
        assert isinstance(issues, list)


class TestPythonExec:
    def test_basic_exec(self, tmp_path: Path) -> None:
        from usdagent.tools.python_exec import run_usd_python
        path = str(tmp_path / "exec.usda")
        create_stage(path)
        result = run_usd_python(path, "print('hello')")
        assert result.success
        assert "hello" in result.stdout

    def test_timeout(self, tmp_path: Path) -> None:
        from usdagent.tools.python_exec import run_usd_python
        path = str(tmp_path / "timeout.usda")
        create_stage(path)
        result = run_usd_python(path, "import time; time.sleep(60)", timeout_s=1)
        assert not result.success
        assert "timed out" in result.stderr
