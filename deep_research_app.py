import streamlit as st
import os
import re
import time
from typing import List

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="AI-Q Knowledge & Research Assistant", layout="wide")

# =====================================================
# SNOW BACKGROUND ANIMATION
# =====================================================
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(270deg, #f9f9f9, #ffffff);
        overflow-x: hidden;
        font-family: Arial, sans-serif;
    }
    .snowflake {
        position: fixed;
        top: -10px;
        color: #bbb;
        font-size: 12px;
        animation: fall linear infinite;
        opacity: 0.7;
    }
    @keyframes fall {
        to { transform: translateY(110vh); }
    }
    .content {
        font-size: 14px;
        line-height: 1.6;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

for i in range(18):
    st.markdown(
        f"<div class='snowflake' style='left:{i*5}%; animation-duration:{10+i}s;'>*</div>",
        unsafe_allow_html=True
    )

# =====================================================
# HEADER
# =====================================================
st.markdown(
    "<h2 style='text-align:center;'>AI-Q Knowledge & Research Assistant</h2>"
    "<p style='text-align:center;color:#555;'>Concepts • Industry • Market • Future</p>",
    unsafe_allow_html=True
)
st.divider()

# =====================================================
# API KEYS
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing. Add it in Streamlit → Secrets.")
    st.stop()

from groq import Groq

@st.cache_resource(show_spinner=False)
def load_groq():
    return Groq(api_key=GROQ_API_KEY)

client = load_groq()

def clean_text(text: str) -> str:
    return re.sub(r"[^\x00-\x7F]+", "", text)

def groq_complete(prompt: str) -> str:
    try:
        res = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt[:6000]}],
            temperature=0.4,
            max_tokens=900,
        )
        return clean_text(res.choices[0].message.content)
    except Exception:
        return "Content generation failed. Please try again."

# =====================================================
# SMART OUTLINE (ALWAYS FULL TOPICS)
# =====================================================
def plan_research(topic: str) -> List[str]:
    prompt = f"""
Create a comprehensive outline for the topic below.

The outline MUST include:
- Definition and overview
- History and evolution
- Technology or working principles
- Types or categories
- Uses and importance
- Business model and industry ecosystem
- Market share and major players
- Pricing strategies and customer segments
- Advantages and disadvantages
- Current trends and future outlook

Return the outline as a numbered list.

Topic:
{topic}
"""
    text = groq_complete(prompt)
    goals = re.findall(r"\d+\.\s*(.*)", text)

    if not goals:
        return [
            f"Definition and overview of {topic}",
            f"History and evolution of {topic}",
            f"Technology and working principles of {topic}",
            f"Types and categories of {topic}",
            f"Uses and importance of {topic}",
            f"Business model and industry ecosystem of {topic}",
            f"Market share and major players in {topic}",
            f"Pricing strategies and customer segments of {topic}",
            f"Advantages and disadvantages of {topic}",
            f"Current trends and future outlook of {topic}",
        ]

    return goals[:10]

# =====================================================
# FINAL REPORT GENERATION (LONG & DETAILED)
# =====================================================
def write_report(topic: str, context: str) -> str:
    prompt = f"""
Write a VERY DETAILED, structured, academic-style explanation on:

{topic}

Use the information below:
{context}

Your response MUST include the following sections clearly:

1. Introduction and Definition
2. Historical Background and Evolution (with years)
3. Technology / Working Principles
4. Types or Categories
5. Uses and Importance in Real Life
6. Business Model and Industry Ecosystem
7. Market Share and Major Companies
8. Pricing Strategies and Customer Segments
9. Advantages and Disadvantages
10. Current Trends and Innovations
11. Future Scope and Outlook
12. Conclusion

Write clearly and thoroughly.
Avoid symbols and emojis.
"""
    return groq_complete(prompt)

# =====================================================
# INPUT
# =====================================================
st.subheader("Enter Topic")
query = st.text_input("", placeholder="e.g., What is a laptop")

run = st.button("Generate", use_container_width=True)

# =====================================================
# MAIN PIPELINE
# =====================================================
if run:
    if not query.strip():
        st.warning("Please enter a topic.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    status.info("Planning content...")
    goals = plan_research(query)
    progress.progress(25)

    st.subheader("Content Outline")
    for i, g in enumerate(goals, 1):
        st.markdown(f"<div class='content'><b>{i}. {g}</b></div>", unsafe_allow_html=True)

    status.info("Generating full explanation...")
    progress.progress(60)

    context = "\n".join(goals)
    report = write_report(query, context)

    progress.progress(100)
    status.success("Completed")

    st.divider()
    st.subheader("Final Explanation")

    st.markdown(
        f"<div class='content'>{report}</div>",
        unsafe_allow_html=True
    )

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.markdown(
    "<p style='text-align:center;font-size:13px;color:#666;'>AI-Q Assistant</p>",
    unsafe_allow_html=True
)
