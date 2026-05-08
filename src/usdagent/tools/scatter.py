"""Procedural placement — scatter on surface or in volume."""

from __future__ import annotations

import math
import random

from pxr import Gf, Usd, UsdGeom  # type: ignore[import]

from usdagent.schemas import BoundingBox, ScatterResult
from usdagent.tools.stage import get_stage
from usdagent.tools.transforms import set_rotate, set_scale, set_translate

_LARGE = 1e10  # anything larger is considered an invalid/empty BBox


def _safe_bbox(stage: Usd.Stage, prim_path: str) -> tuple[Gf.Vec3d, Gf.Vec3d] | None:
    """Return (min, max) world bounds, or None if the prim has no geometry."""
    from pxr import Usd, UsdGeom  # type: ignore[import]
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        return None
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    bbox = cache.ComputeWorldBound(prim)
    r = bbox.GetRange()
    mn, mx = r.GetMin(), r.GetMax()
    # An empty or degenerate BBox returns Inf / very large values — treat as invalid.
    if any(not math.isfinite(v) or abs(v) > _LARGE for v in list(mn) + list(mx)):
        return None
    if r.IsEmpty():
        return None
    return mn, mx


def scatter_on_surface(
    stage_path: str,
    target_prim_path: str,
    source_prim_paths: list[str],
    count: int,
    seed: int = 0,
    rotation_jitter: float = 0.0,
    scale_min: float = 1.0,
    scale_max: float = 1.0,
    bounds_min: tuple[float, float, float] | None = None,
    bounds_max: tuple[float, float, float] | None = None,
) -> ScatterResult:
    """Scatter instances of source_prim_paths across target_prim_path's XZ surface.

    If the target has no geometry (empty mesh), provide bounds_min and bounds_max
    as explicit (x, y, z) world-space corners to define the scatter area.
    Example: bounds_min=(-10, 0, -5), bounds_max=(10, 0, 5) for a 20x10m floor.
    """
    stage = get_stage(stage_path)

    # Resolve scatter bounds — prefer explicit, fall back to BBox, then error.
    if bounds_min is not None and bounds_max is not None:
        mn = Gf.Vec3d(*bounds_min)
        mx = Gf.Vec3d(*bounds_max)
    else:
        result = _safe_bbox(stage, target_prim_path)
        if result is None:
            raise ValueError(
                f"Target prim '{target_prim_path}' has no geometry to compute bounds from. "
                "Pass bounds_min and bounds_max explicitly, e.g. bounds_min=(-10,0,-5), bounds_max=(10,0,5)."
            )
        mn, mx = result

    rng = random.Random(seed)
    created: list[str] = []

    parent_path = f"{target_prim_path}/Scattered"
    stage.DefinePrim(parent_path, "Xform")

    for i in range(count):
        src = source_prim_paths[i % len(source_prim_paths)]
        inst_path = f"{parent_path}/inst_{i:04d}"
        inst = stage.DefinePrim(inst_path, "Xform")
        src_prim = stage.GetPrimAtPath(src)
        if src_prim.IsValid():
            inst.GetReferences().AddInternalReference(src_prim.GetPath())

        x = rng.uniform(float(mn[0]), float(mx[0]))
        z = rng.uniform(float(mn[2]), float(mx[2]))
        set_translate(stage_path, inst_path, (x, 0.0, z))

        if rotation_jitter > 0:
            ry = rng.uniform(-rotation_jitter, rotation_jitter)
            set_rotate(stage_path, inst_path, (0.0, ry, 0.0))

        if scale_min != scale_max:
            s = rng.uniform(scale_min, scale_max)
            set_scale(stage_path, inst_path, (s, s, s))

        created.append(inst_path)

    return ScatterResult(created_paths=created, count=len(created), seed=seed)


def scatter_in_volume(
    stage_path: str,
    bounds: BoundingBox,
    source_prim_paths: list[str],
    count: int,
    seed: int = 0,
) -> ScatterResult:
    """Scatter instances randomly within an explicit bounding box volume."""
    stage = get_stage(stage_path)
    rng = random.Random(seed)
    created: list[str] = []

    container_path = "/World/ScatteredVolume"
    stage.DefinePrim(container_path, "Xform")

    for i in range(count):
        src = source_prim_paths[i % len(source_prim_paths)]
        inst_path = f"{container_path}/inst_{i:04d}"
        stage.DefinePrim(inst_path, "Xform")
        prim = stage.GetPrimAtPath(inst_path)
        src_prim = stage.GetPrimAtPath(src)
        if src_prim.IsValid():
            prim.GetReferences().AddInternalReference(src_prim.GetPath())

        x = rng.uniform(bounds.min.x, bounds.max.x)
        y = rng.uniform(bounds.min.y, bounds.max.y)
        z = rng.uniform(bounds.min.z, bounds.max.z)
        set_translate(stage_path, inst_path, (x, y, z))
        created.append(inst_path)

    return ScatterResult(created_paths=created, count=len(created), seed=seed)
