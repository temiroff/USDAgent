"""End-to-end tests — tagged llm, skipped in CI by default."""

from __future__ import annotations

import os
import tempfile

import pytest


@pytest.mark.llm
def test_e2e_warehouse_scene() -> None:
    """Full warehouse scene from one sentence."""
    from usdagent.agent import run

    with tempfile.TemporaryDirectory() as tmp:
        stage_path = os.path.join(tmp, "warehouse.usda")
        result = run(
            prompt=(
                "Create a warehouse with 10 shelf units scattered on a 10x5m floor. "
                "Add a concrete material to the floor and metal to the shelves."
            ),
            stage_path=stage_path,
        )
        assert result
