"""Example 01 — Warehouse scene from one sentence.

Run:
    uv run python examples/01_warehouse.py
or:
    usdagent run --stage warehouse.usda "Create a warehouse with 50 randomized shelf units..."
"""

from __future__ import annotations

import os

from usdagent.agent import run

PROMPT = (
    "Create a warehouse with 50 randomized shelf units in a 20x10m floor area. "
    "Add concrete material to the floor and metal material to the shelves. "
    "Vary shelf heights between 2-3m."
)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="qwen2.5:7b")
    args = parser.parse_args()

    stage_path = "warehouse.usda"
    print(f"Generating: {stage_path}  [{args.provider}/{args.model}]")
    result = run(prompt=PROMPT, stage_path=stage_path, provider=args.provider, model=args.model)
    print(result)
    print(f"\nSaved: {os.path.abspath(stage_path)}")
