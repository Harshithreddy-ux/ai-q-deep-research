"""Shared agent core: builds the StateGraph and exposes run/stream helpers.
This module gracefully falls back to mock LLM/search if APIs aren't configured.
"""
from typing import Generator
import os
from config import apply_env, missing_keys

apply_env()

try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
except Exception:
    ChatNVIDIA = None

try:
    from langchain_tavily import TavilySearch
except Exception:
    TavilySearch = None

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Annotated, List, TypedDict
import re


class MockLLM:
    def __init__(self, **_):
        pass

    def invoke(self, messages):
        # Return a simple deterministic response for testing
        last = messages[-1].content if messages else ""
        return SystemMessage(content=f"[mock response] Processed: {last}")


class MockSearch:
    def __init__(self, max_results=3, **_):
        self.max_results = max_results

    def invoke(self, params):
        q = params.get("query") if isinstance(params, dict) else str(params)
        return f"[mock search results for '{q}']"


# Instantiate tools (real if available, otherwise mock)
LLM_AVAILABLE = ChatNVIDIA and bool(os.getenv("NVIDIA_API_KEY"))
SEARCH_AVAILABLE = TavilySearch and bool(os.getenv("TAVILY_API_KEY"))

llm = ChatNVIDIA(model="nvidia/llama-3.1-nemotron-70b-instruct") if LLM_AVAILABLE else MockLLM()
search_tool = TavilySearch(max_results=3) if SEARCH_AVAILABLE else MockSearch(max_results=3)


class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    research_plan: List[str]
    collected_data: List[str]
    steps_taken: int


def planner(state: AgentState):
    query = state["messages"][0].content
    prompt = f"Break this into 3 specific research goals: {query}. Output only a numbered list."
    response = llm.invoke([SystemMessage(content="You are a Technical Researcher."), HumanMessage(content=prompt)])
    text = getattr(response, 'content', str(response))
    tasks = re.findall(r'\d+\.\s*(.*)', text)
    if not tasks:
        # fallback split
        tasks = [f"Investigate: {query} - part {i+1}" for i in range(3)]
    return {"research_plan": tasks[:3], "steps_taken": 0}


def researcher(state: AgentState):
    idx = state.get("steps_taken", 0)
    plan = state.get("research_plan", [])
    if not plan:
        return {"collected_data": ["[no plan]"], "steps_taken": idx + 1}
    task = plan[idx % len(plan)]
    results = search_tool.invoke({"query": task})
    return {"collected_data": [f"Goal: {task}\nResult: {results}"], "steps_taken": idx + 1}


def writer(state: AgentState):
    context = "\n---\n".join(state.get("collected_data", []))
    query = state["messages"][0].content
    prompt = f"Write a deep technical report based on: {context} for: {query}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}


def router(state: AgentState):
    return "researcher" if state.get("steps_taken", 0) < len(state.get("research_plan", [])) else "writer"


# Build graph
builder = StateGraph(AgentState)
builder.add_node("planner", planner)
builder.add_node("researcher", researcher)
builder.add_node("writer", writer)
builder.add_edge(START, "planner")
builder.add_edge("planner", "researcher")
builder.add_conditional_edges("researcher", router)
builder.add_edge("writer", END)

AGENT_APP = builder.compile()


def stream_agent(inputs) -> Generator:
    """Yield intermediate outputs from the agent graph (mirrors StateGraph.stream)."""
    for output in AGENT_APP.stream(inputs):
        yield output


def run_agent(inputs):
    return AGENT_APP.invoke(inputs)


__all__ = ["stream_agent", "run_agent", "AGENT_APP"]
