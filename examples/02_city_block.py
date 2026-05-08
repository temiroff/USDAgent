"""Example 02 — City block with buildings and street props."""

from __future__ import annotations

from usdagent.agent import run

PROMPT = (
    "Create a city block scene: a 50x50m ground plane, 6 buildings of varying heights (10-30m) "
    "arranged in a grid, street lamps scattered along the edges every 5m, "
    "and a road material applied to a central 10m-wide strip."
)

if __name__ == "__main__":
    result = run(prompt=PROMPT, stage_path="city_block.usda")
    print(result)
