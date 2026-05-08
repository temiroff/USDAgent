"""USD tool modules — one function per tool, all fully typed."""

from usdagent.tools.materials import bind_material, create_material, set_shader_input
from usdagent.tools.prims import (
    add_payload,
    add_reference,
    create_prim,
    delete_prim,
    get_prim,
    set_attribute,
)
from usdagent.tools.python_exec import run_usd_python
from usdagent.tools.scatter import scatter_in_volume, scatter_on_surface
from usdagent.tools.stage import (
    create_stage,
    get_stage_metadata,
    list_prims,
    open_stage,
    save_stage,
)
from usdagent.tools.transforms import (
    get_world_transform,
    set_rotate,
    set_scale,
    set_translate,
)
from usdagent.tools.validate import (
    check_layer_stack,
    find_broken_references,
    validate_stage,
)

__all__ = [
    "open_stage", "create_stage", "save_stage", "list_prims", "get_stage_metadata",
    "create_prim", "delete_prim", "get_prim", "set_attribute", "add_reference", "add_payload",
    "create_material", "set_shader_input", "bind_material",
    "set_translate", "set_rotate", "set_scale", "get_world_transform",
    "scatter_on_surface", "scatter_in_volume",
    "validate_stage", "find_broken_references", "check_layer_stack",
    "run_usd_python",
]
