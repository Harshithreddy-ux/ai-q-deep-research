import streamlit as st
import os
import re
from typing import List, TypedDict

# -------------------------
# UI FIRST (VERY IMPORTANT)
# -------------------------
st.set_page_config(
    page_title="AI-Q Deep Research",
    layout="wide",
    page_icon="🛡️"
)

st.title("🧠 AI-Q Deep Research Agent")
st.write("🚀 App started successfully")

# -------------------------
# ENV CHECK (SAFE)
# -------------------------
TAVILY_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_KEY:
    st.sidebar.warning("⚠️ TAVILY_API_KEY not found. Web search will be disabled.")

# -------------------------
# STATE
# -------------------------
class AgentState(TypedDict):
    research_plan: List[str]
    collected_data: List[str]
    steps_taken: int
    query: str

# -------------------------
# LAZY LOADERS (SAFE)
# -------------------------
def load_llm():
    try:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        return ChatNVIDIA(model="nvidia/llama-3.1-nemotron-70b-instruct")
    except Exception as e:
        st.error(f"❌ NVIDIA LLM failed to load: {e}")
        return None

def load_search_tool():
    if not TAVILY_KEY:
        return None
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        return TavilySearchResults(max_results=3)
    except Exception as e:
        st.warning(f"Tavily disabled: {e}")
        return None

# -------------------------
# AGENT LOGIC
# -------------------------
def planner(llm, query: str):
    from langchain_core.messages import SystemMessage, HumanMessage

    prompt = f"Break this into 3 specific research goals:\n{query}"
    response = llm.invoke([
        SystemMessage(content="You are a technical researcher."),
        HumanMessage(content=prompt)
    ])
    return re.findall(r"\d+\.\s*(.*)", response.content)[:3]

def researcher(search_tool, task: str):
    if not search_tool:
        return f"Search skipped for: {task}"
    result = search_tool.invoke({"query": task})
    return f"Goal: {task}\nResult: {result}"

def writer(llm, query: str, context: str):
    from langchain_core.messages import HumanMessage
    prompt = f"Write a deep technical report based on:\n{context}\n\nTopic: {query}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content

# -------------------------
# UI INTERACTION
# -------------------------
query = st.text_input(
    "Enter a research topic",
    placeholder="Compare Blackwell vs Hopper NVLink architecture"
)

if st.button("🚀 Run Deep Analysis"):
    if not query:
        st.error("Please enter a topic")
        st.stop()

    llm = load_llm()
    search_tool = load_search_tool()

    if not llm:
        st.stop()

    state: AgentState = {
        "query": query,
        "research_plan": [],
        "collected_data": [],
        "steps_taken": 0,
    }

    with st.spinner("Planning research goals..."):
        state["research_plan"] = planner(llm, query)

    with st.spinner("Collecting data..."):
        for task in state["research_plan"]:
            state["collected_data"].append(researcher(search_tool, task))

    with st.spinner("Writing final report..."):
        report = writer(llm, query, "\n---\n".join(state["collected_data"]))

    st.markdown("## 📊 Final Research Report")
    st.write(report)
