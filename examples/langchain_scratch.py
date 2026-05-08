"""
LangChain scratch file — run each section independently to understand what it does.

Usage:
    uv run python examples/langchain_scratch.py              # runs all sections
    uv run python examples/langchain_scratch.py --section 2  # runs one section
"""

from __future__ import annotations
import argparse


MODEL = "qwen2.5:7b"


# ---------------------------------------------------------------------------
# 1. Basic chat — message in, message out
# ---------------------------------------------------------------------------

def section_1_basic_chat():
    print("\n=== 1. Basic Chat ===")
    from langchain_ollama import ChatOllama
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = ChatOllama(model=MODEL)
    response = llm.invoke([
        SystemMessage(content="You are a terse VFX assistant."),
        HumanMessage(content="What is USD in one sentence?"),
    ])
    print("Response:", response.content)
    print("Type returned:", type(response).__name__)


# ---------------------------------------------------------------------------
# 2. Tool calling — give it a Python function, it decides when to call it
# ---------------------------------------------------------------------------

def section_2_tool_calling():
    print("\n=== 2. Tool Calling ===")
    from langchain_ollama import ChatOllama
    from langchain_core.tools import tool

    @tool
    def get_prim_info(prim_path: str) -> str:
        "Get info about a USD prim at the given path."
        return f"{prim_path}: type=Xform, children=3, active=True"

    @tool
    def list_materials(stage_path: str) -> str:
        "List all materials in a USD stage."
        return f"{stage_path}: [Concrete, Metal, Glass]"

    llm = ChatOllama(model=MODEL).bind_tools([get_prim_info, list_materials])
    response = llm.invoke("What materials are in my scene.usda?")

    print("Content:", response.content or "(empty — model wants to call a tool)")
    print("Tool calls:", response.tool_calls)

    # If the model called a tool, execute it and show the result
    for tc in response.tool_calls:
        tool_map = {"get_prim_info": get_prim_info, "list_materials": list_materials}
        fn = tool_map.get(tc["name"])
        if fn:
            result = fn.invoke(tc["args"])
            print(f"  Tool '{tc['name']}' returned: {result}")


# ---------------------------------------------------------------------------
# 3. Chain — pipe steps together with |
# ---------------------------------------------------------------------------

def section_3_chain():
    print("\n=== 3. Chain (prompt | llm | parser) ===")
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    llm = ChatOllama(model=MODEL)
    prompt = ChatPromptTemplate.from_template(
        "Explain {topic} in exactly one sentence for a VFX artist."
    )
    chain = prompt | llm | StrOutputParser()

    for topic in ["USD stage composition", "PointInstancer", "USD materials"]:
        result = chain.invoke({"topic": topic})
        print(f"  {topic}:\n    {result}")


# ---------------------------------------------------------------------------
# 4. Memory — conversation that remembers previous turns
# ---------------------------------------------------------------------------

def section_4_memory():
    print("\n=== 4. Conversation Memory ===")
    from langchain_ollama import ChatOllama
    from langchain_core.messages import HumanMessage

    llm = ChatOllama(model=MODEL)
    history = []

    turns = [
        "My name is Alex and I work on a VFX pipeline.",
        "What tools am I probably using?",
        "What is my name?",
    ]

    for user_msg in turns:
        history.append(HumanMessage(content=user_msg))
        response = llm.invoke(history)
        history.append(response)
        print(f"  User: {user_msg}")
        print(f"  AI:   {response.content[:120]}")
        print()


# ---------------------------------------------------------------------------
# 5. Streaming — get tokens as they arrive
# ---------------------------------------------------------------------------

def section_5_streaming():
    print("\n=== 5. Streaming ===")
    from langchain_ollama import ChatOllama
    from langchain_core.messages import HumanMessage

    llm = ChatOllama(model=MODEL)
    print("  Tokens: ", end="", flush=True)
    for chunk in llm.stream([HumanMessage(content="Count from 1 to 5.")]):
        print(chunk.content, end="", flush=True)
    print()


# ---------------------------------------------------------------------------
# 6. Structured output — force the model to return a specific schema
# ---------------------------------------------------------------------------

def section_6_structured_output():
    print("\n=== 6. Structured Output (Pydantic schema) ===")
    from langchain_ollama import ChatOllama
    from pydantic import BaseModel, Field

    class SceneDescription(BaseModel):
        prim_count: int = Field(description="Estimated number of prims")
        has_materials: bool = Field(description="Whether the scene has materials")
        complexity: str = Field(description="low, medium, or high")

    llm = ChatOllama(model=MODEL)
    structured_llm = llm.with_structured_output(SceneDescription)

    result = structured_llm.invoke(
        "A warehouse with 50 scattered objects and 2 materials."
    )
    print("  Result:", result)
    print("  Type:", type(result).__name__)
    if result:
        print("  Prim count:", result.prim_count)
        print("  Has materials:", result.has_materials)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SECTIONS = {
    1: ("Basic chat", section_1_basic_chat),
    2: ("Tool calling", section_2_tool_calling),
    3: ("Chain", section_3_chain),
    4: ("Memory", section_4_memory),
    5: ("Streaming", section_5_streaming),
    6: ("Structured output", section_6_structured_output),
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", type=int, default=None,
                        help="Run only this section number (1-6)")
    parser.add_argument("--model", default=MODEL,
                        help="Ollama model name")
    args = parser.parse_args()

    MODEL = args.model  # type: ignore[assignment]

    import warnings
    warnings.filterwarnings("ignore")

    if args.section:
        name, fn = SECTIONS[args.section]
        print(f"Running section {args.section}: {name}")
        fn()
    else:
        for num, (name, fn) in SECTIONS.items():
            fn()
            input(f"\n  [Enter to continue to section {num + 1}]" if num < len(SECTIONS) else "\n  [Enter to exit]")
