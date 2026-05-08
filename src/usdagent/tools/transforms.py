"""Translate / rotate / scale operations."""

from __future__ import annotations

from pxr import Gf, UsdGeom  # type: ignore[import]

from usdagent.schemas import Matrix4d
from usdagent.tools.stage import get_stage


def _xformable(stage: object, prim_path: str) -> UsdGeom.Xformable:
    prim = stage.GetPrimAtPath(prim_path)  # type: ignore[attr-defined]
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {prim_path}")
    xform = UsdGeom.Xformable(prim)
    if not xform:
        raise TypeError(f"Prim at {prim_path} is not Xformable")
    return xform


def set_translate(
    stage_path: str,
    prim_path: str,
    xyz: tuple[float, float, float],
) -> None:
    """Set the translation (position) of a prim in world space."""
    stage = get_stage(stage_path)
    xform = _xformable(stage, prim_path)
    op = _get_or_add_op(xform, UsdGeom.XformOp.TypeTranslate)
    op.Set(Gf.Vec3d(*xyz))


def set_rotate(
    stage_path: str,
    prim_path: str,
    xyz: tuple[float, float, float],
) -> None:
    """Set the XYZ Euler rotation of a prim in degrees."""
    stage = get_stage(stage_path)
    xform = _xformable(stage, prim_path)
    op = _get_or_add_op(xform, UsdGeom.XformOp.TypeRotateXYZ)
    op.Set(Gf.Vec3f(*xyz))


def set_scale(
    stage_path: str,
    prim_path: str,
    xyz: tuple[float, float, float],
) -> None:
    """Set the scale of a prim on X, Y, Z axes."""
    stage = get_stage(stage_path)
    xform = _xformable(stage, prim_path)
    op = _get_or_add_op(xform, UsdGeom.XformOp.TypeScale)
    op.Set(Gf.Vec3f(*xyz))


def get_world_transform(stage_path: str, prim_path: str) -> Matrix4d:
    """Get the 4x4 world-space transform matrix of a prim."""
    stage = get_stage(stage_path)
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {prim_path}")
    xform_cache = UsdGeom.XformCache()
    matrix = xform_cache.GetLocalToWorldTransform(prim)
    rows = [list(matrix.GetRow(i)) for i in range(4)]
    return Matrix4d(values=rows)


def _get_or_add_op(xform: UsdGeom.Xformable, op_type: int) -> UsdGeom.XformOp:
    for op in xform.GetOrderedXformOps():
        if op.GetOpType() == op_type:
            return op
    return xform.AddXformOp(op_type)
