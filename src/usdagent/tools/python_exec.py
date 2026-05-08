"""Sandboxed Python execution escape hatch for complex USD ops."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from usdagent.schemas import ExecResult


_SANDBOX_PREAMBLE = """\
import sys, os
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf

stage = Usd.Stage.Open({stage_path!r})
"""


def run_usd_python(
    stage_path: str,
    code: str,
    timeout_s: int = 10,
) -> ExecResult:
    """Execute arbitrary USD Python in a subprocess with the stage pre-loaded as `stage`. Call stage.GetRootLayer().Save() to persist changes."""
    preamble = _SANDBOX_PREAMBLE.format(stage_path=stage_path)
    full_code = preamble + "\n" + textwrap.dedent(code)

    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(full_code)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return ExecResult(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
        )
    except subprocess.TimeoutExpired:
        return ExecResult(
            success=False,
            stderr=f"Execution timed out after {timeout_s}s",
        )
    finally:
        Path(script_path).unlink(missing_ok=True)
