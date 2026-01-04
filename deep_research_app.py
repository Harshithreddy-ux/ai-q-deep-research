import streamlit as st
import os
import re
import time
from typing import List, TypedDict

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI-Q Deep Research Agent",
    layout="wide"
)

st.title("AI-Q Deep Research Agent")
st.caption("Groq + Tavily powered technical research assistant")

st.divider()

# =====================================================
# ENV KEYS
# =====================================================
GROQ_KEY = os.getenv("GROQ_API_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_KEY:
    st.warning("GROQ_API_KEY not found. App will not generate real answers.")
if not TAVILY_KEY:
    st.warning("TAVILY_API_KEY not found. Web research disabled.")

# =====================================================
# STATE
# =====================================================
class AgentState(TypedDict):
    query: str
    research_plan: List[str]
    research_data: List[str]
    report: str

# =====================================================
# LOADERS (STABLE)
# =====================================================
@st.cache_resource(show_spinner=False)
def load_llm():
    from langchain_groq import ChatGroq
    return ChatGroq(
        api_key=GROQ_KEY,
        model="llama3-8b-8192",
        temperature=0.3,
        max_tokens=1024
    )

def load_search_tool():
    if not TAVILY_KEY:
        return None
    from langchain_community.tools.tavily_search import TavilySearchResults
    return TavilySearchResults(max_results=3)

# =====================================================
# AGENT LOGIC (NO invoke(), ONLY predict())
# =====================================================
def plan_research(llm, query: str) -> List[str]:
    prompt = f"""
You are a senior technical researcher.

Break the topic below into EXACTLY 3 research goals.
Return ONLY a numbered list.

Topic:
{query}
"""
    response = llm.predict(prompt)

    goals = re.findall(r"\d+\.\s*(.*)", response)
    return goals[:3]

def research_step(search_tool, goal: str) -> str:
    if not search_tool:
        return f"{goal}: (web search unavailable)"
    result = search_tool.run(goal)
    return f"{goal}:\n{result}"

def write_report(llm, query: str, context: str) -> str:
    prompt = f"""
Write a detailed technical comparison report.

Topic:
{query}

Use the following researched information:
{context}

Structure the report with:
- Introduction
- Feature comparison
- Advantages & disadvantages
- Conclusion
"""
    return llm.predict(prompt)

# =====================================================
# UI INPUT
# =====================================================
query = st.text_input(
    "Enter a research topic",
    placeholder="Compare Flipkart and Amazon in Indian e-commerce market"
)

run = st.button("Run Deep Research")

# =====================================================
# MAIN PIPELINE
# =====================================================
if run:
    if not query.strip():
        st.error("Please enter a topic")
        st.stop()

    if not GROQ_KEY:
        st.error("Groq API key missing. Cannot run research.")
        st.stop()

    llm = load_llm()
    search_tool = load_search_tool()

    state: AgentState = {
        "query": query,
        "research_plan": [],
        "research_data": [],
        "report": ""
    }

    progress = st.progress(0)
    status = st.empty()

    # ---------------- PLAN ----------------
    status.info("Planning research goals...")
    state["research_plan"] = plan_research(llm, query)
    progress.progress(25)
    time.sleep(0.3)

    st.subheader("Research Plan")
    for i, g in enumerate(state["research_plan"], 1):
        st.markdown(f"**{i}. {g}**")

    # ---------------- RESEARCH ----------------
    status.info("Collecting web research...")
    for idx, goal in enumerate(state["research_plan"]):
        with st.spinner(f"Researching: {goal}"):
            data = research_step(search_tool, goal)
            state["research_data"].append(data)
            progress.progress(40 + idx * 15)
            time.sleep(0.3)

    # ---------------- WRITE ----------------
    status.info("Writing final report...")
    context = "\n\n".join(state["research_data"])
    state["report"] = write_report(llm, query, context)
    progress.progress(100)

    status.success("Research complete")

    st.divider()
    st.subheader("Final Research Report")
    st.write(state["report"])

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.caption("AI-Q Deep Research Agent • Groq + Tavily • Streamlit Cloud")
