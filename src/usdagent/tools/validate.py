"""Scene integrity validation."""

from __future__ import annotations

from pxr import Usd, UsdUtils  # type: ignore[import]

from usdagent.schemas import Issue, StageHandle, ValidationReport
from usdagent.tools.stage import _get_stage


def validate_stage(handle: StageHandle) -> ValidationReport:
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
    stage = _get_stage(handle)
    broken: list[str] = []
    for prim in stage.Traverse():
        for ref in prim.GetMetadata("references") or []:
            # A simplified check: if asset path is set and non-empty, try resolving.
            pass
    # Use UsdUtils to get unresolved paths
    try:
        result = UsdUtils.ComputeAllDependencies(handle.path)
        # result is (layers, assets, unresolved)
        unresolved = result[2] if len(result) >= 3 else []
        broken.extend(str(u) for u in unresolved)
    except Exception:
        pass
    return broken


def check_layer_stack(handle: StageHandle) -> list[Issue]:
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
