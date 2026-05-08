"""Stage-level USD operations."""

from __future__ import annotations

from pxr import Usd, UsdGeom  # type: ignore[import]

from usdagent.schemas import PrimInfo, StageHandle, StageMetadata

# Module-level registry maps path → live Usd.Stage so the agent can hold
# a lightweight StageHandle in its state without serializing the full stage.
_open_stages: dict[str, Usd.Stage] = {}


def _get_stage(handle: StageHandle) -> Usd.Stage:
    if handle.path not in _open_stages:
        raise KeyError(f"Stage not open: {handle.path}. Call open_stage or create_stage first.")
    return _open_stages[handle.path]


def open_stage(path: str) -> StageHandle:
    """Open an existing USD stage file (.usda or .usd) and return a handle."""
    try:
        stage = Usd.Stage.Open(path)
    except Exception as exc:
        raise FileNotFoundError(f"Could not open USD stage: {path}") from exc
    if not stage:
        raise FileNotFoundError(f"Could not open USD stage: {path}")
    _open_stages[path] = stage
    up_axis = UsdGeom.GetStageUpAxis(stage)
    return StageHandle(path=path, up_axis=up_axis)


def create_stage(path: str, up_axis: str = "Y") -> StageHandle:
    """Create a new empty USD stage at path with the given up axis (Y or Z)."""
    stage = Usd.Stage.CreateNew(path)
    UsdGeom.SetStageUpAxis(stage, up_axis)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    stage.GetRootLayer().Save()
    _open_stages[path] = stage
    return StageHandle(path=path, up_axis=up_axis)


def save_stage(handle: StageHandle, path: str | None = None) -> None:
    """Save the stage in place, or export to a new path if provided."""
    stage = _get_stage(handle)
    if path:
        stage.Export(path)
    else:
        stage.GetRootLayer().Save()


def list_prims(handle: StageHandle, root_path: str = "/") -> list[PrimInfo]:
    """List all prims in the stage tree starting from root_path."""
    stage = _get_stage(handle)
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


def get_stage_metadata(handle: StageHandle) -> StageMetadata:
    """Return metadata for the stage: up axis, meters per unit, layer count, prim count."""
    stage = _get_stage(handle)
    all_prims = list(stage.Traverse())
    return StageMetadata(
        path=handle.path,
        up_axis=UsdGeom.GetStageUpAxis(stage),
        meters_per_unit=UsdGeom.GetStageMetersPerUnit(stage),
        layer_count=len(stage.GetLayerStack()),
        prim_count=len(all_prims),
    )
