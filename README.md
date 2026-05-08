# USDAgent

**Orchestrate USD scenes via natural language.**

```bash
usdagent run --stage warehouse.usda \
  "Create a warehouse with 50 randomized shelf units in a 20x10m floor area, \
   add concrete material to the floor, metal material to the shelves, vary heights 2-3m"
```

```
[planner] Decomposed into 6 steps
[tool] create_stage warehouse.usda
[tool] create_prim /World/Floor type=Mesh
[tool] create_material /World/Looks/Concrete
[tool] bind_material /World/Floor → Concrete
[tool] scatter_on_surface target=/World/Floor count=50 ...
[tool] validate_stage → OK
[done] 47s · 6 tool calls · scene saved.
```

---

## Install

```bash
pip install usdagent
export ANTHROPIC_API_KEY=sk-ant-...
```

Requires Python 3.11+ and `usd-core`.

## Quick Start

```python
from usdagent import run

result = run(
    prompt="Add a 10x10m concrete floor with 20 scattered crates",
    stage_path="scene.usda",
)
```

## Features

- Natural language → USD stage operations
- Procedural scatter on surfaces and in volumes
- Material creation and binding (UsdPreviewSurface)
- Scene validation — catches broken refs and layer issues
- Works **headless** — no Omniverse app required
- Optional Omniverse Kit extension for live preview
- Supports Anthropic Claude, OpenAI, and local Ollama models
- Full Python API + CLI

## CLI

```bash
usdagent run "Create a scene"            # NL → USD
usdagent validate scene.usda            # integrity check
usdagent info scene.usda                # metadata
```

## Architecture

```
User Prompt → Planner LLM → Tool Selector → Tool Execution → Validate → Reflect → done/loop
```

Built on LangGraph. Stage handle lives in agent state — never serialized into LLM context.
Every mutation batch ends with USD validation.

## License

Apache 2.0
