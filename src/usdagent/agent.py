"""LangGraph agent definition — planner + executor + validator loop."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage  # type: ignore[import]
from langgraph.graph import END, StateGraph, add_messages  # type: ignore[import]
from langgraph.prebuilt import ToolNode  # type: ignore[import]

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

    tool_node = ToolNode(_ALL_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("planner")
    graph.add_conditional_edges("planner", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "planner")

    return graph.compile()


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
    return last.content if hasattr(last, "content") else str(last)
