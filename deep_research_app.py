import streamlit as st
import os
import re
import time
from typing import List

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI-Q Deep Research Agent",
    layout="wide"
)

st.title("🧠 AI-Q Deep Research Agent")
st.caption("Clean rebuild • Groq + Tavily • Stable Streamlit Cloud version")
st.divider()

# =====================================================
# API KEYS (from Streamlit Secrets or env)
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing. Add it in Streamlit → App Settings → Secrets.")
    st.stop()

if not TAVILY_API_KEY:
    st.warning("TAVILY_API_KEY not found. Web research will be limited.")

# =====================================================
# GROQ CLIENT (OFFICIAL SDK – NO LANGCHAIN)
# =====================================================
from groq import Groq

@st.cache_resource(show_spinner=False)
def load_groq_client():
    return Groq(api_key=GROQ_API_KEY)

client = load_groq_client()

def groq_complete(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content

# =====================================================
# TAVILY SEARCH (OPTIONAL)
# =====================================================
def tavily_search(query: str) -> str:
    if not TAVILY_API_KEY:
        return "Web search unavailable (TAVILY_API_KEY missing)."

    from tavily import TavilyClient
    tavily = TavilyClient(api_key=TAVILY_API_KEY)

    results = tavily.search(query=query, max_results=3)

    if not results.get("results"):
        return "No web results found."

    return "\n\n".join(
        f"- {r['content']}" for r in results["results"]
    )

# =====================================================
# AGENT LOGIC (SIMPLE & SAFE)
# =====================================================
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

Structure:
- Introduction
- Feature comparison
- Pros and cons
- Conclusion
"""
    return groq_complete(prompt)

# =====================================================
# UI
# =====================================================
topic = st.text_input(
    "Enter a research topic",
    placeholder="Compare Flipkart and Amazon in the Indian e-commerce market"
)

run = st.button("🚀 Run Deep Research")

if run:
    if not topic.strip():
        st.error("Please enter a topic.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    # STEP 1: PLAN
    status.info("Planning research goals...")
    goals = plan_research(topic)
    progress.progress(25)
    time.sleep(0.3)

    st.subheader("📌 Research Goals")
    for i, g in enumerate(goals, 1):
        st.markdown(f"**{i}. {g}**")

    # STEP 2: SEARCH
    status.info("Collecting web research...")
    research_blocks = []
    for idx, goal in enumerate(goals):
        with st.spinner(f"Searching: {goal}"):
            research_blocks.append(tavily_search(goal))
            progress.progress(40 + idx * 15)
            time.sleep(0.3)

    # STEP 3: WRITE
    status.info("Writing final report...")
    report = write_report(topic, "\n\n".join(research_blocks))
    progress.progress(100)

    status.success("Research complete")

    st.divider()
    st.subheader("📄 Final Research Report")
    st.write(report)

st.divider()
st.caption("AI-Q Deep Research Agent • Stable clean rebuild")
# =====================================================
# ✅ GUARANTEES OF THIS IMPLEMENTATION
# =====================================================
# ✔ No LangChain
# ✔ No invoke() / predict() confusion
# ✔ No BadRequestError loops
# ✔ Uses official Groq SDK
# ✔ Streamlit Cloud compatible
# ✔ Produces real research output (not demo text)
# ✔ Easy to extend UI later (animations, pages, PDF, etc.)
#
# Architecture:
# - Direct Groq SDK (stable)
# - Direct Tavily SDK (search)
# - Plain string prompts only
# - Single Streamlit entrypoint
#
# This file is intentionally simple and production-safe.
# =====================================================
