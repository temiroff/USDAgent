"""Material and shader assignment."""

from __future__ import annotations

from typing import Any

from pxr import UsdShade  # type: ignore[import]

from usdagent.schemas import MaterialInfo, StageHandle
from usdagent.tools.stage import _get_stage


def create_material(
    handle: StageHandle,
    path: str,
    shader_type: str = "UsdPreviewSurface",
) -> MaterialInfo:
    """Create a new material prim with a shader at path/Shader. Default shader is UsdPreviewSurface."""
    stage = _get_stage(handle)
    material = UsdShade.Material.Define(stage, path)
    shader = UsdShade.Shader.Define(stage, f"{path}/Shader")
    shader.CreateIdAttr(shader_type)
    material.CreateSurfaceOutput().ConnectToSource(
        shader.ConnectableAPI(), "surface"
    )
    return MaterialInfo(
        path=path,
        type_name="Material",
        shader_type=shader_type,
    )


def set_shader_input(
    handle: StageHandle,
    material_path: str,
    input_name: str,
    value: Any,
) -> None:
    """Set a shader input on a material (e.g. diffuseColor, roughness, metallic, opacity)."""
    stage = _get_stage(handle)
    shader_path = f"{material_path}/Shader"
    shader = UsdShade.Shader.Get(stage, shader_path)
    if not shader:
        raise ValueError(f"Shader not found at {shader_path}")
    inp = shader.GetInput(input_name)
    if not inp:
        inp = shader.CreateInput(input_name, _infer_sdf_type(value))
    inp.Set(value)


def bind_material(
    handle: StageHandle,
    prim_path: str,
    material_path: str,
) -> None:
    """Bind a material to a prim so it renders with that material."""
    stage = _get_stage(handle)
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise ValueError(f"Prim does not exist: {prim_path}")
    material = UsdShade.Material.Get(stage, material_path)
    if not material:
        raise ValueError(f"Material does not exist: {material_path}")
    UsdShade.MaterialBindingAPI.Apply(prim).Bind(material)


def _infer_sdf_type(value: Any) -> Any:
    from pxr import Sdf  # type: ignore[import]
    if isinstance(value, float):
        return Sdf.ValueTypeNames.Float
    if isinstance(value, int):
        return Sdf.ValueTypeNames.Int
    if isinstance(value, tuple) and len(value) == 3:
        return Sdf.ValueTypeNames.Color3f
    if isinstance(value, tuple) and len(value) == 4:
        return Sdf.ValueTypeNames.Color4f
    return Sdf.ValueTypeNames.Token
