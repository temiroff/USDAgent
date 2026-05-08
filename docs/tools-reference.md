# Tools Reference

## Stage

| Function | Description |
|---|---|
| `open_stage(path)` | Open an existing .usda/.usd file |
| `create_stage(path, up_axis)` | Create a new stage |
| `save_stage(handle, path?)` | Save in-place or export to path |
| `list_prims(handle, root?)` | List all prims under root |
| `get_stage_metadata(handle)` | Up axis, meters/unit, layer count |

## Prims

| Function | Description |
|---|---|
| `create_prim(handle, path, type, attrs?)` | Define a new typed prim |
| `delete_prim(handle, path)` | Remove prim and children |
| `get_prim(handle, path)` | Read prim info + attributes |
| `set_attribute(handle, path, name, value)` | Set an existing attribute |
| `add_reference(handle, path, asset_path)` | Add a USD reference |
| `add_payload(handle, path, asset_path)` | Add a USD payload |

## Materials

| Function | Description |
|---|---|
| `create_material(handle, path, shader_type?)` | Create UsdPreviewSurface material |
| `set_shader_input(handle, mat_path, input, value)` | Set diffuseColor, roughness, etc. |
| `bind_material(handle, prim_path, mat_path)` | Bind material to a prim |

## Transforms

| Function | Description |
|---|---|
| `set_translate(handle, path, (x,y,z))` | Set world-space position |
| `set_rotate(handle, path, (x,y,z))` | Set XYZ Euler rotation in degrees |
| `set_scale(handle, path, (x,y,z))` | Set scale |
| `get_world_transform(handle, path)` | Get 4x4 world matrix |

## Scatter

| Function | Description |
|---|---|
| `scatter_on_surface(handle, target, sources, count, seed, rot_jitter, scale_range)` | Scatter on prim's XZ bounds |
| `scatter_in_volume(handle, bounds, sources, count, seed)` | Scatter in explicit bounding box |

## Validation

| Function | Description |
|---|---|
| `validate_stage(handle)` | Full integrity check → ValidationReport |
| `find_broken_references(handle)` | List unresolvable asset paths |
| `check_layer_stack(handle)` | Check for duplicate/dirty layers |

## Python Escape Hatch

| Function | Description |
|---|---|
| `run_usd_python(handle, code, timeout_s?)` | Run arbitrary USD Python in subprocess |
