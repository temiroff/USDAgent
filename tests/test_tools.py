"""Unit tests for USD tool layer — no LLM calls."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from usdagent.schemas import BoundingBox, Vec3f
from usdagent.tools.stage import create_stage, list_prims, open_stage, save_stage, get_stage_metadata


FIXTURE_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Stage
# ---------------------------------------------------------------------------

class TestStage:
    def test_create_stage(self, tmp_path: Path) -> None:
        path = str(tmp_path / "test.usda")
        handle = create_stage(path)
        assert handle.path == path
        assert handle.up_axis == "Y"

    def test_open_stage(self) -> None:
        handle = open_stage(str(FIXTURE_DIR / "simple_scene.usda"))
        assert "simple_scene" in handle.path

    def test_open_nonexistent_stage_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            open_stage("/nonexistent/path/scene.usda")

    def test_list_prims(self) -> None:
        handle = open_stage(str(FIXTURE_DIR / "simple_scene.usda"))
        prims = list_prims(handle)
        paths = [p.path for p in prims]
        assert "/World" in paths
        assert "/World/Floor" in paths

    def test_get_stage_metadata(self) -> None:
        handle = open_stage(str(FIXTURE_DIR / "simple_scene.usda"))
        meta = get_stage_metadata(handle)
        assert meta.up_axis == "Y"
        assert meta.meters_per_unit == 1.0
        assert meta.prim_count > 0

    def test_save_stage(self, tmp_path: Path) -> None:
        src = str(FIXTURE_DIR / "simple_scene.usda")
        dest = str(tmp_path / "copy.usda")
        handle = open_stage(src)
        save_stage(handle, dest)
        assert Path(dest).exists()


# ---------------------------------------------------------------------------
# Prims
# ---------------------------------------------------------------------------

class TestPrims:
    def test_create_prim(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        handle = create_stage(str(tmp_path / "prims.usda"))
        info = create_prim(handle, "/World", "Xform")
        assert info.path == "/World"
        assert info.type_name == "Xform"

    def test_get_prim(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim, get_prim
        handle = create_stage(str(tmp_path / "get.usda"))
        create_prim(handle, "/World", "Xform")
        info = get_prim(handle, "/World")
        assert info.path == "/World"

    def test_delete_prim(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim, delete_prim, get_prim
        handle = create_stage(str(tmp_path / "del.usda"))
        create_prim(handle, "/World", "Xform")
        create_prim(handle, "/World/Child", "Xform")
        delete_prim(handle, "/World/Child")
        with pytest.raises(ValueError):
            get_prim(handle, "/World/Child")

    def test_delete_nonexistent_prim_raises(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import delete_prim
        handle = create_stage(str(tmp_path / "del2.usda"))
        with pytest.raises(ValueError):
            delete_prim(handle, "/DoesNotExist")


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

class TestTransforms:
    def setup_stage(self, tmp_path: Path, name: str = "xform.usda"):
        from usdagent.tools.prims import create_prim
        handle = create_stage(str(tmp_path / name))
        create_prim(handle, "/World", "Xform")
        return handle

    def test_set_translate(self, tmp_path: Path) -> None:
        from usdagent.tools.transforms import set_translate, get_world_transform
        handle = self.setup_stage(tmp_path)
        set_translate(handle, "/World", (1.0, 2.0, 3.0))
        mat = get_world_transform(handle, "/World")
        assert len(mat.values) == 4

    def test_set_rotate(self, tmp_path: Path) -> None:
        from usdagent.tools.transforms import set_rotate
        handle = self.setup_stage(tmp_path, "rot.usda")
        set_rotate(handle, "/World", (0.0, 45.0, 0.0))

    def test_set_scale(self, tmp_path: Path) -> None:
        from usdagent.tools.transforms import set_scale
        handle = self.setup_stage(tmp_path, "scale.usda")
        set_scale(handle, "/World", (2.0, 2.0, 2.0))


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

class TestMaterials:
    def test_create_material(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        from usdagent.tools.materials import create_material
        handle = create_stage(str(tmp_path / "mat.usda"))
        create_prim(handle, "/World", "Xform")
        create_prim(handle, "/World/Looks", "Scope")
        mat = create_material(handle, "/World/Looks/Concrete")
        assert mat.path == "/World/Looks/Concrete"
        assert mat.shader_type == "UsdPreviewSurface"

    def test_bind_material(self, tmp_path: Path) -> None:
        from usdagent.tools.prims import create_prim
        from usdagent.tools.materials import create_material, bind_material
        handle = create_stage(str(tmp_path / "bind.usda"))
        create_prim(handle, "/World", "Xform")
        create_prim(handle, "/World/Looks", "Scope")
        create_prim(handle, "/World/Floor", "Mesh")
        create_material(handle, "/World/Looks/Concrete")
        bind_material(handle, "/World/Floor", "/World/Looks/Concrete")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_valid_stage(self) -> None:
        from usdagent.tools.validate import validate_stage
        handle = open_stage(str(FIXTURE_DIR / "simple_scene.usda"))
        report = validate_stage(handle)
        assert isinstance(report.is_valid, bool)

    def test_check_layer_stack(self) -> None:
        from usdagent.tools.validate import check_layer_stack
        handle = open_stage(str(FIXTURE_DIR / "simple_scene.usda"))
        issues = check_layer_stack(handle)
        assert isinstance(issues, list)


# ---------------------------------------------------------------------------
# Python exec
# ---------------------------------------------------------------------------

class TestPythonExec:
    def test_basic_exec(self, tmp_path: Path) -> None:
        from usdagent.tools.python_exec import run_usd_python
        handle = create_stage(str(tmp_path / "exec.usda"))
        result = run_usd_python(handle, "print('hello')")
        assert result.success
        assert "hello" in result.stdout

    def test_timeout(self, tmp_path: Path) -> None:
        from usdagent.tools.python_exec import run_usd_python
        handle = create_stage(str(tmp_path / "timeout.usda"))
        result = run_usd_python(handle, "import time; time.sleep(60)", timeout_s=1)
        assert not result.success
        assert "timed out" in result.stderr
