import streamlit as st
import os
import re
from typing import Annotated, List, TypedDict, Literal
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage

# CONFIGURATION: load from .env via config.py
from config import apply_env, missing_keys

apply_env()
missing = missing_keys()
if missing:
    pass

st.set_page_config(page_title="AI-Q Deep Research", layout="wide", page_icon="🛡️")

# THE BRAIN
llm = ChatNVIDIA(model="nvidia/llama-3.1-nemotron-70b-instruct")
search_tool = TavilySearchResults(max_results=3)

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    research_plan: List[str]
    collected_data: List[str]
    steps_taken: int

# --- NODES ---
def planner(state: AgentState):
    import streamlit as st
    import re
    from typing import Annotated, List, TypedDict
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    from langchain_community.tools.tavily_search import TavilySearchResults
    from langchain_core.messages import HumanMessage, SystemMessage
    from config import apply_env, missing_keys

    apply_env()
    missing = missing_keys()
    if missing:
        # show warning in UI later
        pass

    st.set_page_config(page_title="AI-Q Deep Research", layout="wide", page_icon="🛡️")

    # THE BRAIN
    llm = ChatNVIDIA(model="nvidia/llama-3.1-nemotron-70b-instruct")
    search_tool = TavilySearchResults(max_results=3)

    class AgentState(TypedDict):
        messages: Annotated[List, ...]
        research_plan: List[str]
        collected_data: List[str]
        steps_taken: int


    def planner(state: AgentState):
        query = state["messages"][0].content
        prompt = f"Break this into 3 specific research goals: {query}. Output as a numbered list."
        response = llm.invoke([SystemMessage(content="You are a Technical Researcher."), HumanMessage(content=prompt)])
        tasks = re.findall(r'\d+\.\s*(.*)', response.content)
        return {"research_plan": tasks[:3], "steps_taken": 0}


    def researcher(state: AgentState):
        idx = state["steps_taken"]
        if not state.get("research_plan"):
            return {"collected_data": [], "steps_taken": idx}
        task = state["research_plan"][idx % len(state["research_plan"])]
        results = search_tool.invoke({"query": task})
        return {"collected_data": [f"Goal: {task}\nResult: {results}"], "steps_taken": idx + 1}


    def writer(state: AgentState):
        context = "\n---\n".join(state.get("collected_data", []))
        query = state["messages"][0].content
        prompt = f"Write a deep technical report based on: {context} for: {query}"
        response = llm.invoke([HumanMessage(content=prompt)])
        return getattr(response, "content", str(response))


    st.title("🧠 Deep Research Agent — Lite UI")
    st.markdown("Enter a topic and run the agent (uses mock tools if API keys are missing).")

    if missing:
        st.sidebar.warning(f"Missing env keys: {', '.join(missing)}")

    user_input = st.text_input("Enter Topic", placeholder="Compare Blackwell vs Hopper NVLink...")

    if st.button("🚀 Run Deep Analysis"):
        if not user_input:
            st.error("Please enter a research topic first.")
        else:
            state = {
                "messages": [HumanMessage(content=user_input)],
                "research_plan": [],
                "collected_data": [],
                "steps_taken": 0,
            }
            with st.spinner("Planning research goals..."):
                state.update(planner(state))
            with st.spinner("Collecting data..."):
                state.update(researcher(state))
            with st.spinner("Writing report..."):
                report = writer(state)
            st.markdown("### 📊 Final Analysis Report")
            st.write(report)
            try:
                from storage import save_run

                save_run(user_input, report)
                st.success("Run saved")
            except Exception:
                st.warning("Could not save run")