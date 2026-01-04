import streamlit as st
import os
import re
import time
from typing import List

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="AI-Q Deep Research Agent",
    layout="wide"
)

st.title("AI-Q Deep Research Agent")
st.caption("Groq + Tavily powered research system (stable build)")

st.divider()

# =============================
# API KEYS
# =============================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing in Streamlit Secrets")
    st.stop()

if not TAVILY_API_KEY:
    st.warning("TAVILY_API_KEY missing – web search limited")

# =============================
# GROQ CLIENT (OFFICIAL SDK)
# =============================
from groq import Groq

@st.cache_resource(show_spinner=False)
def load_groq_client():
    return Groq(api_key=GROQ_API_KEY)

client = load_groq_client()

# =============================
# TAVILY SEARCH
# =============================
def tavily_search(query: str) -> str:
    if not TAVILY_API_KEY:
        return "Web search unavailable."

    from tavily import TavilyClient
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    results = tavily.search(query=query, max_results=3)
    return "\n".join([r["content"] for r in results["results"]])

# =============================
# LLM FUNCTIONS (PURE GROQ)
# =============================
def groq_complete(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return completion.choices[0].message.content

# =============================
# AGENT LOGIC
# =============================
def plan_research(topic: str) -> List[str]:
    prompt = f"""
Break the topic below into EXACTLY 3 research goals.
Return ONLY a numbered list.

Topic:
{topic}
"""
    text = groq_complete(prompt)
    return re.findall(r"\d+\.\s*(.*)", text)[:3]

def write_report(topic: str, context: str) -> str:
    prompt = f"""
Write a structured technical comparison report.

Topic:
{topic}

Use this research information:
{context}

Include:
- Introduction
- Feature comparison
- Pros & cons
- Conclusion
"""
    return groq_complete(prompt)

# =============================
# UI
# =============================
topic = st.text_input(
    "Enter a research topic",
    placeholder="Compare Flipkart and Amazon in India"
)

run = st.button("Run Deep Research")

if run:
    if not topic.strip():
        st.error("Please enter a topic")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    # PLAN
    status.info("Planning research goals...")
    goals = plan_research(topic)
    progress.progress(30)
    time.sleep(0.3)

    st.subheader("Research Goals")
    for i, g in enumerate(goals, 1):
        st.markdown(f"**{i}. {g}**")

    # SEARCH
    status.info("Collecting web research...")
    research_blocks = []
    for idx, goal in enumerate(goals):
        with st.spinner(f"Searching: {goal}"):
            research_blocks.append(tavily_search(goal))
            progress.progress(40 + idx * 15)
            time.sleep(0.3)

    # WRITE
    status.info("Writing final report...")
    report = write_report(topic, "\n\n".join(research_blocks))
    progress.progress(100)

    status.success("Research complete")

    st.divider()
    st.subheader("Final Research Report")
    st.write(report)

st.divider()
st.caption("Stable Groq + Tavily implementation • No LangChain")
