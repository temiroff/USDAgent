"""Example 01 — Warehouse scene with real mesh geometry and PointInstancer.

Run:
    uv run python examples/01_warehouse.py
"""

from __future__ import annotations

import math
import os
import random

from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade  # type: ignore[import]


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _make_floor(stage: Usd.Stage, path: str, width: float, depth: float) -> None:
    """Flat quad-mesh plane at Y=0, centered at origin."""
    mesh = UsdGeom.Mesh.Define(stage, path)
    hw, hd = width / 2, depth / 2
    mesh.CreatePointsAttr([
        Gf.Vec3f(-hw, 0,  hd),
        Gf.Vec3f( hw, 0,  hd),
        Gf.Vec3f( hw, 0, -hd),
        Gf.Vec3f(-hw, 0, -hd),
    ])
    mesh.CreateFaceVertexCountsAttr([4])
    mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    mesh.CreateSubdivisionSchemeAttr("none")
    mesh.CreateNormalsAttr([Gf.Vec3f(0, 1, 0)] * 4)
    mesh.SetNormalsInterpolation("vertex")


def _make_box(
    stage: Usd.Stage,
    path: str,
    w: float,
    h: float,
    d: float,
) -> None:
    """Box mesh with pivot at bottom-center (Y=0 to Y=h)."""
    mesh = UsdGeom.Mesh.Define(stage, path)
    hw, hd = w / 2, d / 2
    pts = [
        Gf.Vec3f(-hw, 0,  hd),  # 0 bot front-left
        Gf.Vec3f( hw, 0,  hd),  # 1 bot front-right
        Gf.Vec3f( hw, 0, -hd),  # 2 bot back-right
        Gf.Vec3f(-hw, 0, -hd),  # 3 bot back-left
        Gf.Vec3f(-hw, h,  hd),  # 4 top front-left
        Gf.Vec3f( hw, h,  hd),  # 5 top front-right
        Gf.Vec3f( hw, h, -hd),  # 6 top back-right
        Gf.Vec3f(-hw, h, -hd),  # 7 top back-left
    ]
    mesh.CreatePointsAttr(pts)
    mesh.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
    mesh.CreateFaceVertexIndicesAttr([
        0, 3, 2, 1,  # bottom
        4, 5, 6, 7,  # top
        0, 1, 5, 4,  # front
        3, 7, 6, 2,  # back
        0, 4, 7, 3,  # left
        1, 2, 6, 5,  # right
    ])
    mesh.CreateSubdivisionSchemeAttr("none")


def _make_material(
    stage: Usd.Stage,
    path: str,
    diffuse: tuple[float, float, float],
    roughness: float,
    metallic: float = 0.0,
) -> UsdShade.Material:
    mat = UsdShade.Material.Define(stage, path)
    shader = UsdShade.Shader.Define(stage, f"{path}/Shader")
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*diffuse))
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
    shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(metallic)
    mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
    return mat


def _bind(stage: Usd.Stage, prim_path: str, mat: UsdShade.Material) -> None:
    prim = stage.GetPrimAtPath(prim_path)
    UsdShade.MaterialBindingAPI.Apply(prim).Bind(mat)


# ---------------------------------------------------------------------------
# PointInstancer scatter
# ---------------------------------------------------------------------------

def _scatter_instancer(
    stage: Usd.Stage,
    instancer_path: str,
    prototype_path: str,
    count: int,
    bounds_min: tuple[float, float, float],
    bounds_max: tuple[float, float, float],
    seed: int = 42,
    rotation_jitter: float = 360.0,
    scale_min: float = 0.8,
    scale_max: float = 1.2,
) -> None:
    """Scatter prototype using UsdGeom.PointInstancer — renders correctly in Blender."""
    rng = random.Random(seed)
    instancer = UsdGeom.PointInstancer.Define(stage, instancer_path)
    instancer.GetPrototypesRel().AddTarget(prototype_path)

    positions, orientations, scales, proto_indices = [], [], [], []

    for _ in range(count):
        x = rng.uniform(bounds_min[0], bounds_max[0])
        z = rng.uniform(bounds_min[2], bounds_max[2])
        positions.append(Gf.Vec3f(x, 0.0, z))

        ry = math.radians(rng.uniform(0, rotation_jitter))
        half = ry / 2
        orientations.append(Gf.Quath(math.cos(half), Gf.Vec3h(0, math.sin(half), 0)))

        s = rng.uniform(scale_min, scale_max)
        scales.append(Gf.Vec3f(s, s, s))
        proto_indices.append(0)

    instancer.CreatePositionsAttr(positions)
    instancer.CreateOrientationsAttr(orientations)
    instancer.CreateScalesAttr(scales)
    instancer.CreateProtoIndicesAttr(proto_indices)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_warehouse(stage_path: str) -> None:
    stage = Usd.Stage.CreateNew(stage_path)
    UsdGeom.SetStageUpAxis(stage, "Y")
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    # Root
    UsdGeom.Xform.Define(stage, "/World")

    # Floor — flat quad mesh, 20×10m at Y=0
    _make_floor(stage, "/World/Floor", width=20.0, depth=10.0)

    # Materials
    UsdGeom.Scope.Define(stage, "/World/Looks")
    concrete = _make_material(stage, "/World/Looks/Concrete",
                              diffuse=(0.40, 0.38, 0.35), roughness=0.9)
    metal = _make_material(stage, "/World/Looks/Metal",
                           diffuse=(0.60, 0.62, 0.65), roughness=0.2, metallic=1.0)

    _bind(stage, "/World/Floor", concrete)

    # Shelf unit prototype — bind material BEFORE deactivating parent
    UsdGeom.Xform.Define(stage, "/World/Prototypes")
    _make_box(stage, "/World/Prototypes/ShelfUnit", w=1.0, h=2.5, d=0.4)
    _bind(stage, "/World/Prototypes/ShelfUnit", metal)
    stage.GetPrimAtPath("/World/Prototypes").SetActive(False)

    # Scatter 50 shelf units on the floor via PointInstancer
    _scatter_instancer(
        stage,
        instancer_path="/World/ShelfInstancer",
        prototype_path="/World/Prototypes/ShelfUnit",
        count=50,
        bounds_min=(-9.0, 0.0, -4.5),
        bounds_max=( 9.0, 0.0,  4.5),
        seed=42,
        rotation_jitter=360.0,
        scale_min=0.85,
        scale_max=1.15,
    )

    stage.GetRootLayer().Save()
    print(f"  Prims: {sum(1 for _ in stage.Traverse())}")
    print(f"  Saved: {os.path.abspath(stage_path)}")


if __name__ == "__main__":
    print("Building warehouse.usda ...")
    build_warehouse("warehouse.usda")
    print("Done. Import into Blender: File > Import > USD (.usda)")
