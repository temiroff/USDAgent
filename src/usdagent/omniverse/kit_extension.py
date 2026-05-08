"""Optional Omniverse Kit extension — live preview hook.

Import only from kit_extension.py — never from usdagent core.
Requires: omni.kit, omni.usd (Omniverse Kit runtime).
"""

from __future__ import annotations

# These imports only resolve inside an Omniverse Kit process.
try:
    import omni.ext  # type: ignore[import]
    import omni.usd  # type: ignore[import]

    _KIT_AVAILABLE = True
except ImportError:
    _KIT_AVAILABLE = False


def is_available() -> bool:
    return _KIT_AVAILABLE


def sync_stage(stage_path: str) -> None:
    """Push a saved USDA to the live Kit viewport."""
    if not _KIT_AVAILABLE:
        raise RuntimeError("Omniverse Kit is not available in this process.")
    ctx = omni.usd.get_context()
    ctx.open_stage(stage_path)
