"""Prim CRUD operations."""

from __future__ import annotations

from typing import Any

from pxr import Sdf, Usd  # type: ignore[import]

from usdagent.schemas import PrimInfo, StageHandle
from usdagent.tools.stage import _get_stage


def create_prim(
    handle: StageHandle,
    path: str,
    type_name: str,
    attributes: dict[str, Any] | None = None,
) -> PrimInfo:
    """Define a new typed prim at path (e.g. Xform, Mesh, Sphere, Cube). Optionally set attributes."""
    stage = _get_stage(handle)
    prim = stage.DefinePrim(path, type_name)
    if attributes:
        for name, value in attributes.items():
            attr = prim.GetAttribute(name)
            if not attr:
                attr = prim.CreateAttribute(name, Sdf.ValueTypeNames.Token)
            attr.Set(value)
    return PrimInfo(
        path=path,
        type_name=type_name,
        is_active=prim.IsActive(),
        children=[str(c.GetPath()) for c in prim.GetChildren()],
        attributes=attributes or {},
    )


def delete_prim(handle: StageHandle, path: str) -> None:
    """Delete a prim and all its children from the stage."""
    stage = _get_stage(handle)
    prim = stage.GetPrimAtPath(path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {path}")
    stage.RemovePrim(path)


def get_prim(handle: StageHandle, path: str) -> PrimInfo:
    """Get info and attributes for the prim at path."""
    stage = _get_stage(handle)
    prim = stage.GetPrimAtPath(path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {path}")
    attrs: dict[str, Any] = {}
    for attr in prim.GetAttributes():
        if attr.HasValue():
            attrs[attr.GetName()] = attr.Get()
    return PrimInfo(
        path=path,
        type_name=prim.GetTypeName(),
        is_active=prim.IsActive(),
        children=[str(c.GetPath()) for c in prim.GetChildren()],
        attributes=attrs,
    )


def set_attribute(handle: StageHandle, path: str, name: str, value: Any) -> None:
    """Set the value of an existing attribute on a prim."""
    stage = _get_stage(handle)
    prim = stage.GetPrimAtPath(path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {path}")
    attr = prim.GetAttribute(name)
    if not attr:
        raise AttributeError(f"Attribute '{name}' not found on {path}")
    attr.Set(value)


def add_reference(handle: StageHandle, path: str, asset_path: str) -> None:
    """Add a USD reference to an external asset at prim path."""
    stage = _get_stage(handle)
    prim = stage.OverridePrim(path)
    prim.GetReferences().AddReference(asset_path)


def add_payload(handle: StageHandle, path: str, asset_path: str) -> None:
    """Add a USD payload (deferred reference) to an external asset at prim path."""
    stage = _get_stage(handle)
    prim = stage.OverridePrim(path)
    prim.GetPayloads().AddPayload(asset_path)
