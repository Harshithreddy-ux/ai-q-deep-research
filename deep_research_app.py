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

# =====================================================
# BACKGROUND ANIMATION (SUBTLE, NO LOGOS)
# =====================================================
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(270deg, #f7f7f7, #ffffff, #f2f2f2);
        background-size: 600% 600%;
        animation: gradientMove 18s ease infinite;
        font-family: Arial, sans-serif;
    }
    @keyframes gradientMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .small-text {
        font-size: 14px;
        line-height: 1.5;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h2 style='text-align:center;'>AI-Q Deep Research Agent</h2>"
    "<p style='text-align:center; color:#555;'>Interactive research system</p>",
    unsafe_allow_html=True
)

st.divider()

# =====================================================
# API KEYS
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing in Streamlit Secrets.")
    st.stop()

# =====================================================
# GROQ CLIENT
# =====================================================
from groq import Groq

@st.cache_resource(show_spinner=False)
def load_groq_client():
    return Groq(api_key=GROQ_API_KEY)

client = load_groq_client()

def clean_text(text: str) -> str:
    # remove emojis & symbols
    return re.sub(r"[^\x00-\x7F]+", "", text)

def groq_complete(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt[:6000]}],
            temperature=0.3,
            max_tokens=700,
        )
        return clean_text(response.choices[0].message.content)
    except Exception:
        return ""

# =====================================================
# TAVILY SEARCH
# =====================================================
def tavily_search(query: str) -> str:
    if not TAVILY_API_KEY:
        return "Web search unavailable."

    from tavily import TavilyClient
    tavily = TavilyClient(api_key=TAVILY_API_KEY)

    results = tavily.search(query=query, max_results=3)
    if not results.get("results"):
        return "No relevant web data found."

    return "\n".join(clean_text(r["content"][:800]) for r in results["results"])

# =====================================================
# AGENT LOGIC
# =====================================================
def plan_research(topic: str) -> List[str]:
    prompt = f"""
Create 5 detailed research goals for:
{topic}

Focus on:
- Business model
- Technology & logistics
- Pricing & customer experience
- Market growth
- Future outlook

Return as numbered list.
"""
    text = groq_complete(prompt)
    goals = re.findall(r"\d+\.\s*(.*)", text)

    if not goals:
        return [
            f"Business model comparison of {topic}",
            f"Technology and logistics comparison of {topic}",
            f"Pricing strategy and customer experience of {topic}",
            f"Market growth and regional dominance of {topic}",
            f"Strengths, weaknesses, and future outlook of {topic}",
        ]
    return goals[:5]

def write_report(topic: str, context: str) -> str:
    prompt = f"""
Write a LONG, detailed academic-style report on:

{topic}

Using this research:
{context}

Include:
Introduction
Detailed comparison sections
Advantages & disadvantages
Future outlook
Conclusion

Avoid emojis and symbols.
"""
    return groq_complete(prompt)

# =====================================================
# SEARCH-LIKE INPUT
# =====================================================
st.subheader("Enter Research Topic")
topic = st.text_input(
    "",
    placeholder="Search here... (e.g., Flipkart vs Amazon India)"
)

run = st.button("Run Deep Research", use_container_width=True)

# =====================================================
# PIPELINE
# =====================================================
if run:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    status.info("Planning research...")
    goals = plan_research(topic)
    progress.progress(20)

    st.subheader("Research Goals")
    for i, g in enumerate(goals, 1):
        st.markdown(f"<div class='small-text'><b>Goal {i}:</b> {g}</div>",
                    unsafe_allow_html=True)

    status.info("Gathering information...")
    research_blocks = []

    for idx, goal in enumerate(goals):
        with st.expander(f"Searching: {goal}", expanded=False):
            data = tavily_search(goal + " India e-commerce analysis")
            research_blocks.append(data)
            st.markdown(f"<div class='small-text'>{data}</div>",
                        unsafe_allow_html=True)
            progress.progress(min(30 + (idx + 1) * 10, 90))
            time.sleep(0.3)

    status.info("Generating final report...")
    report = write_report(topic, "\n\n".join(research_blocks))
    progress.progress(100)

    st.success("Research completed")

    st.divider()
    st.subheader("Final Research Report")

    st.markdown(
        f"<div class='small-text'>{report}</div>",
        unsafe_allow_html=True
    )

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.markdown(
    "<p style='text-align:center; font-size:13px; color:#666;'>AI-Q Deep Research Agent</p>",
    unsafe_allow_html=True
)
