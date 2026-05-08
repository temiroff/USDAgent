"""Translate / rotate / scale operations."""

from __future__ import annotations

from pxr import Gf, UsdGeom  # type: ignore[import]

from usdagent.schemas import Matrix4d, StageHandle
from usdagent.tools.stage import _get_stage


def _xformable(stage: object, path: str) -> UsdGeom.Xformable:
    from pxr import Usd  # type: ignore[import]
    prim = stage.GetPrimAtPath(path)  # type: ignore[attr-defined]
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {path}")
    xform = UsdGeom.Xformable(prim)
    if not xform:
        raise TypeError(f"Prim at {path} is not Xformable")
    return xform


def set_translate(
    handle: StageHandle,
    path: str,
    xyz: tuple[float, float, float],
) -> None:
    stage = _get_stage(handle)
    xform = _xformable(stage, path)
    op = _get_or_add_op(xform, UsdGeom.XformOp.TypeTranslate)
    op.Set(Gf.Vec3d(*xyz))


def set_rotate(
    handle: StageHandle,
    path: str,
    xyz: tuple[float, float, float],
) -> None:
    stage = _get_stage(handle)
    xform = _xformable(stage, path)
    op = _get_or_add_op(xform, UsdGeom.XformOp.TypeRotateXYZ)
    op.Set(Gf.Vec3f(*xyz))


def set_scale(
    handle: StageHandle,
    path: str,
    xyz: tuple[float, float, float],
) -> None:
    stage = _get_stage(handle)
    xform = _xformable(stage, path)
    op = _get_or_add_op(xform, UsdGeom.XformOp.TypeScale)
    op.Set(Gf.Vec3f(*xyz))


def get_world_transform(handle: StageHandle, path: str) -> Matrix4d:
    stage = _get_stage(handle)
    prim = stage.GetPrimAtPath(path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {path}")
    xform_cache = UsdGeom.XformCache()
    matrix = xform_cache.GetLocalToWorldTransform(prim)
    rows = [list(matrix.GetRow(i)) for i in range(4)]
    return Matrix4d(values=rows)


def _get_or_add_op(xform: UsdGeom.Xformable, op_type: int) -> UsdGeom.XformOp:
    for op in xform.GetOrderedXformOps():
        if op.GetOpType() == op_type:
            return op
    return xform.AddXformOp(op_type)
