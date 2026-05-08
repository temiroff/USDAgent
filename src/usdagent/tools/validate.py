"""Scene integrity validation."""

from __future__ import annotations

from pxr import Usd, UsdUtils  # type: ignore[import]

from usdagent.schemas import Issue, StageHandle, ValidationReport
from usdagent.tools.stage import _get_stage


def validate_stage(handle: StageHandle) -> ValidationReport:
    """Run a full integrity check on the stage and return a ValidationReport with all issues."""
    stage = _get_stage(handle)
    issues: list[Issue] = []
    broken = find_broken_references(handle)

    for ref_path in broken:
        issues.append(Issue(severity="error", path=ref_path, message="Broken reference"))

    layer_issues = check_layer_stack(handle)
    issues.extend(layer_issues)

    return ValidationReport(
        is_valid=len([i for i in issues if i.severity == "error"]) == 0,
        issues=issues,
        broken_references=broken,
    )


def find_broken_references(handle: StageHandle) -> list[str]:
    """Return a list of asset paths that cannot be resolved in the current stage."""
    broken: list[str] = []
    try:
        result = UsdUtils.ComputeAllDependencies(handle.path)
        unresolved = result[2] if len(result) >= 3 else []
        broken.extend(str(u) for u in unresolved)
    except Exception:
        pass
    return broken


def check_layer_stack(handle: StageHandle) -> list[Issue]:
    """Check the layer stack for duplicate or unsaved layers."""
    stage = _get_stage(handle)
    issues: list[Issue] = []
    seen: set[str] = set()
    for layer in stage.GetLayerStack():
        ident = layer.identifier
        if ident in seen:
            issues.append(
                Issue(severity="warning", path=ident, message="Duplicate layer in stack")
            )
        seen.add(ident)
        if not layer.IsMuted() and layer.dirty:
            issues.append(
                Issue(severity="info", path=ident, message="Layer has unsaved changes")
            )
    return issues
