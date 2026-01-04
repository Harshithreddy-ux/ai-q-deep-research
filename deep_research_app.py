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

st.markdown(
    """
    <h1 style="text-align:center;">AI-Q Deep Research Agent</h1>
    <p style="text-align:center;color:gray;">
    Interactive research system with live execution flow
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# API KEYS
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing. Add it in Streamlit → Settings → Secrets.")
    st.stop()

# =====================================================
# GROQ CLIENT (OFFICIAL SDK)
# =====================================================
from groq import Groq

@st.cache_resource(show_spinner=False)
def load_groq_client():
    return Groq(api_key=GROQ_API_KEY)

client = load_groq_client()

def groq_complete(prompt: str) -> str:
    try:
        prompt = prompt[:6000]  # safety limit

        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=512,
        )

        return response.choices[0].message.content

    except Exception as e:
        return ""

# =====================================================
# TAVILY SEARCH (LIMITED SIZE)
# =====================================================
def tavily_search(query: str) -> str:
    if not TAVILY_API_KEY:
        return "Web search unavailable."

    from tavily import TavilyClient
    tavily = TavilyClient(api_key=TAVILY_API_KEY)

    results = tavily.search(query=query, max_results=3)

    if not results.get("results"):
        return "No web data found."

    return "\n".join(r["content"][:1000] for r in results["results"])

# =====================================================
# AGENT LOGIC
# =====================================================
def plan_research(topic: str) -> List[str]:
    prompt = f"""
Break the topic below into EXACTLY 3 research goals.
Return ONLY a numbered list.

Topic:
{topic}
"""
    text = groq_complete(prompt)

    goals = re.findall(r"\d+\.\s*(.*)", text)
    return goals[:3]

def write_report(topic: str, context: str) -> str:
    prompt = f"""
Write a structured technical comparison report.

Topic:
{topic}

Research information:
{context}

Structure:
- Introduction
- Feature comparison
- Pros and cons
- Conclusion
"""
    return groq_complete(prompt)

# =====================================================
# UI INPUT
# =====================================================
st.subheader("Enter Research Topic")

topic = st.text_input(
    "",
    placeholder="Compare Flipkart and Amazon in the Indian e-commerce market"
)

run = st.button("Run Deep Research", use_container_width=True)

# =====================================================
# INTERACTIVE PIPELINE
# =====================================================
if run:
    if not topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    # ---------------- PLAN ----------------
    status.info("Planning research goals...")
    time.sleep(0.5)

    goals = plan_research(topic)

    # 🔴 SAFETY CHECK (YOU ASKED ABOUT THIS)
    if not goals:
        st.error("Failed to generate research goals. Please try again.")
        st.stop()

    progress.progress(25)

    st.subheader("Research Goals")
    for i, goal in enumerate(goals, 1):
        with st.expander(f"Goal {i}", expanded=True):
            st.write(goal)

    # ---------------- SEARCH ----------------
    status.info("Collecting information from the web...")
    time.sleep(0.5)

    research_blocks = []
    st.subheader("Information Gathering")

    for idx, goal in enumerate(goals):
        with st.expander(f"Searching: {goal}", expanded=True):
            with st.spinner("Searching..."):
                result = tavily_search(goal)
                research_blocks.append(result)
                st.write(result[:1000])
                progress.progress(40 + (idx + 1) * 15)
                time.sleep(0.4)

    # ---------------- WRITE ----------------
    status.info("Writing final report...")
    time.sleep(0.5)

    report = write_report(topic, "\n\n".join(research_blocks))
    progress.progress(100)

    status.success("Research completed successfully")

    # ---------------- OUTPUT ----------------
    st.divider()
    st.subheader("Final Research Report")
    with st.expander("View Report", expanded=True):
        st.write(report)

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.markdown(
    "<p style='text-align:center;color:gray;'>AI-Q Deep Research Agent • Interactive Mode</p>",
    unsafe_allow_html=True
)
