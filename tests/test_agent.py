"""Agent tests — uses recorded fixtures, no live LLM calls."""

from __future__ import annotations

import pytest


@pytest.mark.llm
def test_agent_run_live() -> None:
    """Live integration test — requires ANTHROPIC_API_KEY."""
    from usdagent.agent import run
    import tempfile, os

    with tempfile.TemporaryDirectory() as tmp:
        stage_path = os.path.join(tmp, "test.usda")
        result = run(
            prompt="Create a stage with a single cube at the origin.",
            stage_path=stage_path,
        )
        assert isinstance(result, str)
        assert len(result) > 0
