"""Example 03 — Robot test environment for Isaac Sim."""

from __future__ import annotations

from usdagent.agent import run

PROMPT = (
    "Create a robot test scene: a flat 10x10m arena with a rubber-grip floor material, "
    "4 obstacle boxes of random sizes (0.3-0.8m) placed in the interior, "
    "and a start marker (thin flat cylinder) at (0,0,0) and goal marker at (8,0,8)."
)

if __name__ == "__main__":
    result = run(prompt=PROMPT, stage_path="robot_test.usda")
    print(result)
