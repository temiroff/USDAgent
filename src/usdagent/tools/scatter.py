"""Procedural placement — scatter on surface or in volume."""

from __future__ import annotations

import random

from pxr import Usd, UsdGeom  # type: ignore[import]

from usdagent.schemas import BoundingBox, ScatterResult
from usdagent.tools.stage import get_stage
from usdagent.tools.transforms import set_rotate, set_scale, set_translate


def scatter_on_surface(
    stage_path: str,
    target_prim_path: str,
    source_prim_paths: list[str],
    count: int,
    seed: int = 0,
    rotation_jitter: float = 0.0,
    scale_min: float = 1.0,
    scale_max: float = 1.0,
) -> ScatterResult:
    """Scatter instances of source_prim_paths randomly across the XZ bounds of target_prim_path."""
    stage = get_stage(stage_path)
    prim = stage.GetPrimAtPath(target_prim_path)
    if not prim.IsValid():
        raise ValueError(f"Target prim does not exist: {target_prim_path}")

    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
    bbox = bbox_cache.ComputeWorldBound(prim)
    bbox_range = bbox.GetRange()
    min_pt = bbox_range.GetMin()
    max_pt = bbox_range.GetMax()

    rng = random.Random(seed)
    created: list[str] = []

    parent_path = f"{target_prim_path}/Scattered"
    stage.DefinePrim(parent_path, "Xform")

    for i in range(count):
        src = source_prim_paths[i % len(source_prim_paths)]
        inst_path = f"{parent_path}/inst_{i:04d}"
        inst = stage.DefinePrim(inst_path, "Xform")
        inst.GetReferences().AddReference("", stage.GetPrimAtPath(src).GetPath())

        x = rng.uniform(min_pt[0], max_pt[0])
        z = rng.uniform(min_pt[2], max_pt[2])
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
        prim.GetReferences().AddReference("", stage.GetPrimAtPath(src).GetPath())

        x = rng.uniform(bounds.min.x, bounds.max.x)
        y = rng.uniform(bounds.min.y, bounds.max.y)
        z = rng.uniform(bounds.min.z, bounds.max.z)
        set_translate(stage_path, inst_path, (x, y, z))
        created.append(inst_path)

    return ScatterResult(created_paths=created, count=len(created), seed=seed)
