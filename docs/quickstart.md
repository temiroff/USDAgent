# Quickstart

## Install

```bash
pip install usdagent
# or with uv:
uv add usdagent
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## CLI

```bash
# Create a new scene from a prompt
usdagent run "Create a warehouse with 50 shelf units" --stage warehouse.usda

# Validate an existing stage
usdagent validate scene.usda

# Print stage info
usdagent info scene.usda
```

## Python API

```python
from usdagent import run

result = run(
    prompt="Add a concrete floor material to /World/Floor",
    stage_path="scene.usda",
)
print(result)
```

## Use a different LLM

```bash
usdagent run --provider openai --model gpt-4o "Create a cube"
usdagent run --provider ollama --model llama3 "Create a cube"
```
