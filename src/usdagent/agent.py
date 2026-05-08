"""LangGraph agent definition — planner + executor + validator loop."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage  # type: ignore[import]
from langgraph.graph import END, StateGraph, add_messages  # type: ignore[import]

from usdagent import tools
from usdagent.llm import Provider, get_llm
from usdagent.prompts import SYSTEM_PROMPT
from usdagent.schemas import StageHandle


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    stage_handle: StageHandle | None
    iteration: int


_ALL_TOOLS = [
    tools.open_stage,
    tools.create_stage,
    tools.save_stage,
    tools.list_prims,
    tools.get_stage_metadata,
    tools.create_prim,
    tools.delete_prim,
    tools.get_prim,
    tools.set_attribute,
    tools.add_reference,
    tools.add_payload,
    tools.create_material,
    tools.set_shader_input,
    tools.bind_material,
    tools.set_translate,
    tools.set_rotate,
    tools.set_scale,
    tools.get_world_transform,
    tools.scatter_on_surface,
    tools.scatter_in_volume,
    tools.validate_stage,
    tools.find_broken_references,
    tools.check_layer_stack,
    tools.run_usd_python,
]


_TOOL_MAP: dict[str, Any] = {fn.__name__: fn for fn in _ALL_TOOLS}


def build_agent(
    provider: Provider | str = Provider.ANTHROPIC,
    model: str | None = None,
    max_iterations: int = 20,
) -> Any:
    llm = get_llm(provider, model)
    llm_with_tools = llm.bind_tools(_ALL_TOOLS)

    def planner(state: AgentState) -> dict[str, Any]:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response], "iteration": state.get("iteration", 0) + 1}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            if state.get("iteration", 0) >= max_iterations:
                return END
            return "tools"
        return END

    def sequential_tools(state: AgentState) -> dict[str, Any]:
        """Execute tool calls one at a time — avoids USD stage race conditions."""
        last = state["messages"][-1]
        results: list[ToolMessage] = []
        for tc in last.tool_calls:
            fn = _TOOL_MAP.get(tc["name"])
            if fn is None:
                content = f"Unknown tool: {tc['name']}"
            else:
                try:
                    result = fn(**tc["args"])
                    content = str(result)
                except Exception as exc:
                    content = f"Error: {exc}"
            results.append(ToolMessage(content=content, tool_call_id=tc["id"]))
        return {"messages": results}

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner)
    graph.add_node("tools", sequential_tools)
    graph.set_entry_point("planner")
    graph.add_conditional_edges("planner", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "planner")

    return graph.compile()


def _summarize_tool_calls(messages: list[AnyMessage]) -> str:
    """Build a summary from tool call history when the LLM returns no final text."""
    calls: list[str] = []
    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                args = ", ".join(f"{k}={v!r}" for k, v in tc.get("args", {}).items())
                calls.append(f"[tool] {tc['name']}({args})")
        elif isinstance(msg, ToolMessage):
            calls.append(f"  → {str(msg.content)[:120]}")
    return "\n".join(calls) if calls else "(no tool calls recorded)"


def run(
    prompt: str,
    stage_path: str | None = None,
    provider: Provider | str = Provider.ANTHROPIC,
    model: str | None = None,
) -> str:
    agent = build_agent(provider=provider, model=model)
    user_msg = prompt
    if stage_path:
        user_msg = f"Stage: {stage_path}\n\n{prompt}"

    result = agent.invoke(
        {
            "messages": [HumanMessage(content=user_msg)],
            "stage_handle": None,
            "iteration": 0,
        }
    )

    last = result["messages"][-1]
    content = last.content if hasattr(last, "content") else str(last)

    # Small models often return empty content after tool calls — fall back to a trace summary.
    if not content or not content.strip():
        content = "Done.\n\n" + _summarize_tool_calls(result["messages"])

    # Auto-save any stages that were created/modified but not explicitly saved.
    _auto_save_open_stages()

    return content


def _auto_save_open_stages() -> None:
    from usdagent.tools.stage import _open_stages
    for path, stage in _open_stages.items():
        try:
            if stage.GetRootLayer().dirty:
                stage.GetRootLayer().Save()
        except Exception:
            pass
