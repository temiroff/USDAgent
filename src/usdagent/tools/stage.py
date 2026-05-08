"""Stage-level USD operations."""

from __future__ import annotations

from pxr import Usd, UsdGeom  # type: ignore[import]

from usdagent.schemas import PrimInfo, StageMetadata

# Registry: stage_path → live Usd.Stage object.
_open_stages: dict[str, Usd.Stage] = {}


def get_stage(stage_path: str) -> Usd.Stage:
    """Internal helper — look up an open stage, auto-opening or creating it if needed."""
    if stage_path not in _open_stages:
        import os
        if os.path.exists(stage_path):
            open_stage(stage_path)
        else:
            create_stage(stage_path)
    return _open_stages[stage_path]


def open_stage(stage_path: str) -> str:
    """Open an existing USD stage file (.usda/.usd). Returns the stage path on success."""
    try:
        stage = Usd.Stage.Open(stage_path)
    except Exception as exc:
        raise FileNotFoundError(f"Could not open USD stage: {stage_path}") from exc
    if not stage:
        raise FileNotFoundError(f"Could not open USD stage: {stage_path}")
    _open_stages[stage_path] = stage
    return stage_path


def create_stage(stage_path: str, up_axis: str = "Y") -> str:
    """Create a new empty USD stage at stage_path with the given up axis (Y or Z). Returns the stage path."""
    stage = Usd.Stage.CreateNew(stage_path)
    UsdGeom.SetStageUpAxis(stage, up_axis)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    stage.GetRootLayer().Save()
    _open_stages[stage_path] = stage
    return stage_path


def save_stage(stage_path: str, export_path: str | None = None) -> None:
    """Save the stage in place, or export to export_path if provided."""
    stage = get_stage(stage_path)
    if export_path:
        stage.Export(export_path)
    else:
        stage.GetRootLayer().Save()


def list_prims(stage_path: str, root_path: str = "/") -> list[PrimInfo]:
    """List all prims in the stage tree starting from root_path."""
    stage = get_stage(stage_path)
    root = stage.GetPrimAtPath(root_path)
    if not root.IsValid():
        return []
    results: list[PrimInfo] = []
    for prim in Usd.PrimRange(root):
        results.append(
            PrimInfo(
                path=str(prim.GetPath()),
                type_name=prim.GetTypeName(),
                is_active=prim.IsActive(),
                children=[str(c.GetPath()) for c in prim.GetChildren()],
            )
        )
    return results


def get_stage_metadata(stage_path: str) -> StageMetadata:
    """Return metadata for the stage: up axis, meters per unit, layer count, prim count."""
    stage = get_stage(stage_path)
    all_prims = list(stage.Traverse())
    return StageMetadata(
        path=stage_path,
        up_axis=UsdGeom.GetStageUpAxis(stage),
        meters_per_unit=UsdGeom.GetStageMetersPerUnit(stage),
        layer_count=len(stage.GetLayerStack()),
        prim_count=len(all_prims),
    )
