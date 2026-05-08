"""Prim CRUD operations."""

from __future__ import annotations

from typing import Any

from pxr import Sdf  # type: ignore[import]

from usdagent.schemas import PrimInfo
from usdagent.tools.stage import get_stage


def create_prim(
    stage_path: str,
    prim_path: str,
    type_name: str,
    attributes: dict[str, Any] | None = None,
) -> PrimInfo:
    """Define a new typed prim at prim_path (e.g. Xform, Mesh, Sphere, Cube). Optionally set attributes."""
    stage = get_stage(stage_path)
    prim = stage.DefinePrim(prim_path, type_name)
    if attributes:
        for name, value in attributes.items():
            attr = prim.GetAttribute(name)
            if not attr:
                attr = prim.CreateAttribute(name, Sdf.ValueTypeNames.Token)
            attr.Set(value)
    return PrimInfo(
        path=prim_path,
        type_name=type_name,
        is_active=prim.IsActive(),
        children=[str(c.GetPath()) for c in prim.GetChildren()],
        attributes=attributes or {},
    )


def delete_prim(stage_path: str, prim_path: str) -> None:
    """Delete a prim and all its children from the stage."""
    stage = get_stage(stage_path)
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {prim_path}")
    stage.RemovePrim(prim_path)


def get_prim(stage_path: str, prim_path: str) -> PrimInfo:
    """Get info and attributes for the prim at prim_path."""
    stage = get_stage(stage_path)
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {prim_path}")
    attrs: dict[str, Any] = {}
    for attr in prim.GetAttributes():
        if attr.HasValue():
            attrs[attr.GetName()] = attr.Get()
    return PrimInfo(
        path=prim_path,
        type_name=prim.GetTypeName(),
        is_active=prim.IsActive(),
        children=[str(c.GetPath()) for c in prim.GetChildren()],
        attributes=attrs,
    )


def set_attribute(stage_path: str, prim_path: str, name: str, value: Any) -> None:
    """Set the value of an existing attribute on a prim."""
    stage = get_stage(stage_path)
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {prim_path}")
    attr = prim.GetAttribute(name)
    if not attr:
        raise AttributeError(f"Attribute '{name}' not found on {prim_path}")
    attr.Set(value)


def add_reference(stage_path: str, prim_path: str, asset_path: str) -> None:
    """Add a USD reference to an external asset at prim_path."""
    stage = get_stage(stage_path)
    prim = stage.OverridePrim(prim_path)
    prim.GetReferences().AddReference(asset_path)


def add_payload(stage_path: str, prim_path: str, asset_path: str) -> None:
    """Add a USD payload (deferred reference) to an external asset at prim_path."""
    stage = get_stage(stage_path)
    prim = stage.OverridePrim(prim_path)
    prim.GetPayloads().AddPayload(asset_path)
