"""Material and shader assignment."""

from __future__ import annotations

from typing import Any

from pxr import UsdShade  # type: ignore[import]

from usdagent.schemas import MaterialInfo
from usdagent.tools.stage import get_stage


def create_material(
    stage_path: str,
    material_path: str,
    shader_type: str = "UsdPreviewSurface",
) -> MaterialInfo:
    """Create a new material prim with a shader at material_path/Shader. Default shader is UsdPreviewSurface."""
    stage = get_stage(stage_path)
    material = UsdShade.Material.Define(stage, material_path)
    shader = UsdShade.Shader.Define(stage, f"{material_path}/Shader")
    shader.CreateIdAttr(shader_type)
    material.CreateSurfaceOutput().ConnectToSource(
        shader.ConnectableAPI(), "surface"
    )
    return MaterialInfo(
        path=material_path,
        type_name="Material",
        shader_type=shader_type,
    )


def set_shader_input(
    stage_path: str,
    material_path: str,
    input_name: str,
    value: Any,
) -> None:
    """Set a shader input on a material (e.g. diffuseColor, roughness, metallic, opacity)."""
    stage = get_stage(stage_path)
    shader_path = f"{material_path}/Shader"
    shader = UsdShade.Shader.Get(stage, shader_path)
    if not shader:
        raise ValueError(f"Shader not found at {shader_path}")
    inp = shader.GetInput(input_name)
    if not inp:
        inp = shader.CreateInput(input_name, _infer_sdf_type(value))
    inp.Set(value)


def bind_material(
    stage_path: str,
    prim_path: str,
    material_path: str,
) -> None:
    """Bind a material to a prim so it renders with that material."""
    stage = get_stage(stage_path)
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
