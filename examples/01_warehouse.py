"""Example 01 — Warehouse scene.

Builds directly via the tool API for guaranteed correctness,
then optionally asks the LLM to validate and describe what was created.

Run:
    uv run python examples/01_warehouse.py
    uv run python examples/01_warehouse.py --llm   # also run LLM validation step
"""

from __future__ import annotations

import argparse
import os

from usdagent.tools.materials import bind_material, create_material, set_shader_input
from usdagent.tools.prims import create_prim
from usdagent.tools.scatter import scatter_on_surface
from usdagent.tools.stage import create_stage, save_stage
from usdagent.tools.transforms import set_scale, set_translate
from usdagent.tools.validate import validate_stage


def build_warehouse(stage_path: str) -> None:
    create_stage(stage_path)

    # Root
    create_prim(stage_path, "/World", "Xform")

    # Floor — Cube scaled flat to 20x10m
    create_prim(stage_path, "/World/Floor", "Cube")
    set_scale(stage_path, "/World/Floor", (10.0, 0.05, 5.0))  # half-extents → 20x0.1x10m

    # Shelf unit template — tall cube
    create_prim(stage_path, "/World/ShelfUnit", "Cube")
    set_scale(stage_path, "/World/ShelfUnit", (0.5, 1.25, 0.2))  # 1x2.5x0.4m

    # Materials
    create_prim(stage_path, "/World/Looks", "Scope")
    create_material(stage_path, "/World/Looks/Concrete")
    set_shader_input(stage_path, "/World/Looks/Concrete", "diffuseColor", (0.4, 0.4, 0.4))
    set_shader_input(stage_path, "/World/Looks/Concrete", "roughness", 0.9)

    create_material(stage_path, "/World/Looks/Metal")
    set_shader_input(stage_path, "/World/Looks/Metal", "diffuseColor", (0.6, 0.6, 0.7))
    set_shader_input(stage_path, "/World/Looks/Metal", "metallic", 1.0)
    set_shader_input(stage_path, "/World/Looks/Metal", "roughness", 0.2)

    bind_material(stage_path, "/World/Floor", "/World/Looks/Concrete")
    bind_material(stage_path, "/World/ShelfUnit", "/World/Looks/Metal")

    # Scatter 50 shelf units on the floor — explicit bounds in world space
    result = scatter_on_surface(
        stage_path,
        target_prim_path="/World/Floor",
        source_prim_paths=["/World/ShelfUnit"],
        count=50,
        seed=42,
        rotation_jitter=180.0,
        scale_min=0.8,
        scale_max=1.2,
        bounds_min=(-9.0, 0.0, -4.5),
        bounds_max=(9.0, 0.0, 4.5),
    )
    print(f"  Scattered {result.count} shelf units")

    report = validate_stage(stage_path)
    print(f"  Validation: {'OK' if report.is_valid else 'ISSUES'} — {len(report.issues)} issue(s)")

    save_stage(stage_path)


PROMPT = (
    "Validate the warehouse scene at warehouse.usda and describe what was built: "
    "prims, materials, and scatter result."
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="Run LLM validation step after build")
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="qwen2.5:7b")
    args = parser.parse_args()

    stage_path = "warehouse.usda"
    print(f"Building: {stage_path}")
    build_warehouse(stage_path)
    print(f"Saved:    {os.path.abspath(stage_path)}")

    if args.llm:
        from usdagent.agent import run
        print("\nRunning LLM validation...")
        result = run(prompt=PROMPT, stage_path=stage_path, provider=args.provider, model=args.model)
        print(result)
