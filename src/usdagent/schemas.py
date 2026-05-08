"""Pydantic models for all tool inputs and outputs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Stage
# ---------------------------------------------------------------------------

class StageHandle(BaseModel):
    """Lightweight reference to an open USD stage."""
    path: str
    up_axis: str = "Y"

    class Config:
        arbitrary_types_allowed = True


class PrimInfo(BaseModel):
    path: str
    type_name: str
    is_active: bool = True
    children: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)


class StageMetadata(BaseModel):
    path: str
    up_axis: str
    meters_per_unit: float
    layer_count: int
    prim_count: int


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

class Vec3f(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


class Matrix4d(BaseModel):
    """Row-major 4x4 matrix."""
    values: list[list[float]] = Field(
        default_factory=lambda: [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

class MaterialInfo(PrimInfo):
    shader_type: str = "UsdPreviewSurface"
    inputs: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Scatter
# ---------------------------------------------------------------------------

class BoundingBox(BaseModel):
    min: Vec3f = Field(default_factory=Vec3f)
    max: Vec3f = Field(default_factory=lambda: Vec3f(x=1, y=1, z=1))


class ScatterResult(BaseModel):
    created_paths: list[str]
    count: int
    seed: int


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class Issue(BaseModel):
    severity: str  # "error" | "warning" | "info"
    path: str
    message: str


class ValidationReport(BaseModel):
    is_valid: bool
    issues: list[Issue] = Field(default_factory=list)
    broken_references: list[str] = Field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")


# ---------------------------------------------------------------------------
# Python exec
# ---------------------------------------------------------------------------

class ExecResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""
    return_value: Any = None
