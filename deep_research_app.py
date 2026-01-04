import streamlit as st
import os
import re
import time
from typing import List, TypedDict

# =========================================================
# PAGE CONFIG (NO LOGO)
# =========================================================
st.set_page_config(
    page_title="AI-Q Deep Research Agent",
    layout="wide"
)

# =========================================================
# HEADER (CLEAN)
# =========================================================
st.markdown(
    """
    <h1 style='text-align:center;'>AI-Q Deep Research Agent</h1>
    <p style='text-align:center;color:gray;'>
    Interactive multi-step technical research assistant
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# ENV CHECK
# =========================================================
TAVILY_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_KEY:
    st.sidebar.warning("Web search disabled (TAVILY_API_KEY not found)")

# =========================================================
# STATE
# =========================================================
class AgentState(TypedDict):
    query: str
    research_plan: List[str]
    collected_data: List[str]

# =========================================================
# LAZY LOADERS (SAFE FOR CLOUD)
# =========================================================
@st.cache_resource(show_spinner=False)
def load_llm():
    try:
        if not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("GROQ_API_KEY missing")

        from langchain_groq import ChatGroq

        return ChatGroq(
            model="llama3-70b-8192",
            temperature=0.3
        )

    except Exception as e:
        from langchain_core.messages import AIMessage

        class MockLLM:
            def invoke(self, messages):
                return AIMessage(
                    content=f"""
Demo mode active.

Reason:
{e}

This shows the research pipeline works.
"""
                )

        return MockLLM()


def load_search_tool():
    if not TAVILY_KEY:
        return None
    from langchain_community.tools.tavily_search import TavilySearchResults
    return TavilySearchResults(max_results=3)

# =========================================================
# AGENT FUNCTIONS
# =========================================================
def plan_research(llm, query: str) -> List[str]:
    import re
    from langchain_core.messages import HumanMessage

    prompt = f"""
Break the following topic into exactly 3 clear research goals.
Return them as a numbered list.

Topic:
{query}
"""

    response = llm.invoke([
        HumanMessage(
            content=f"You are a senior technical researcher.\n\n{prompt}"
        )
    ])

    return re.findall(r"\d+\.\s*(.*)", response.content)[:3]



def research_step(search_tool, task: str) -> str:
    if not search_tool:
        return f"{task}\n(No web search – offline reasoning only)"
    result = search_tool.invoke({"query": task})
    return f"{task}\n{result}"

def write_report(llm, query: str, context: str) -> str:
    from langchain_core.messages import HumanMessage

    prompt = f"""
Write a structured technical report using the information below.

Context:
{context}

Topic:
{query}
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    return response.content



# =========================================================
# UI INPUT
# =========================================================
query = st.text_input(
    "Enter a research topic",
    placeholder="Compare Blackwell vs Hopper NVLink architecture",
    key="query_input"
)

run = st.button("Run Deep Analysis")

# =========================================================
# MAIN EXECUTION
# =========================================================
if run:
    query = st.session_state.get("query_input", "").strip()

    if not query:
        st.error("Please enter a topic")
        st.stop()

    state: AgentState = {
        "query": query,
        "research_plan": [],
        "collected_data": []
    }

    progress = st.progress(0)
    status = st.empty()

    # LOAD MODELS
    status.info("Initializing research engine...")
    llm = load_llm()
    search_tool = load_search_tool()
    progress.progress(10)
    time.sleep(0.3)

    # PLANNING
    status.info("Planning research goals...")
    with st.spinner("Generating research plan"):
        state["research_plan"] = plan_research(llm, query)
    progress.progress(30)
    time.sleep(0.3)

    st.subheader("Research Plan")
    for i, goal in enumerate(state["research_plan"], 1):
        st.markdown(f"**{i}. {goal}**")

    # RESEARCH
    status.info("Collecting information...")
    for idx, task in enumerate(state["research_plan"]):
        with st.spinner(f"Researching: {task}"):
            result = research_step(search_tool, task)
            state["collected_data"].append(result)
            progress.progress(50 + idx * 10)
            time.sleep(0.3)

    # WRITING
    status.info("Writing final report...")
    with st.spinner("Synthesizing insights"):
        report = write_report(
            llm,
            query,
            "\n\n".join(state["collected_data"])
        )
    progress.progress(100)

    status.success("Analysis complete")

    st.divider()

    # OUTPUT (INTERACTIVE)
    st.subheader("Final Research Report")

    with st.expander("Show Report", expanded=True):
        st.write(report)

    st.success("Done")

# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption("AI-Q Deep Research Agent • Streamlit Cloud Optimized")
