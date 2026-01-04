import streamlit as st
import os
import re
import time

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI-Q Knowledge & Research Assistant",
    layout="wide"
)

# =====================================================
# IMPROVED SNOW ANIMATION (LAYERED)
# =====================================================
st.markdown(
    """
    <style>
    body {
        background: #fafafa;
        font-family: Arial, sans-serif;
    }
    .snow {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
    }
    .flake {
        position: absolute;
        top: -10px;
        color: #cfcfcf;
        font-size: 10px;
        animation-name: fall;
        animation-timing-function: linear;
        animation-iteration-count: infinite;
        opacity: 0.8;
    }
    @keyframes fall {
        to {
            transform: translateY(110vh);
        }
    }
    .content {
        font-size: 15px;
        line-height: 1.7;
        color: #1a1a1a;
        background: white;
        padding: 14px;
        border-radius: 6px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Snow layers
for i in range(40):
    st.markdown(
        f"<div class='flake' style='left:{i*2.5}%; animation-duration:{8+i%6}s;'>*</div>",
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
# GROQ SETUP
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing.")
    st.stop()

from groq import Groq

@st.cache_resource
def groq_client():
    return Groq(api_key=GROQ_API_KEY)

client = groq_client()

def groq_call(prompt: str) -> str:
    try:
        res = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt[:4000]}],
            temperature=0.4,
            max_tokens=700,
        )
        return re.sub(r"[^\x00-\x7F]+", "", res.choices[0].message.content)
    except Exception:
        return "Unable to generate content at this time."

# =====================================================
# SECTION GENERATOR (KEY FIX)
# =====================================================
def explain_section(topic: str, section: str) -> str:
    prompt = f"""
Explain the following section in detail:

Topic: {topic}
Section: {section}

Requirements:
- Clear explanation
- History/years if applicable
- Real-world relevance
- Student-friendly language
"""
    return groq_call(prompt)

# =====================================================
# INPUT
# =====================================================
st.subheader("Enter Topic")
topic = st.text_input("", placeholder="e.g., laptop")

run = st.button("Generate Explanation", use_container_width=True)

# =====================================================
# MAIN PIPELINE
# =====================================================
if run:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    sections = [
        "Definition and overview",
        "History and evolution",
        "Technology and working principles",
        "Types and categories",
        "Uses and importance",
        "Business model and industry ecosystem",
        "Market share and major players",
        "Pricing strategies and customer segments",
        "Advantages and disadvantages",
        "Current trends and future outlook"
    ]

    progress = st.progress(0)
    st.subheader("Detailed Explanation")

    for i, sec in enumerate(sections, 1):
        st.markdown(f"### {i}. {sec}")
        content = explain_section(topic, sec)
        st.markdown(f"<div class='content'>{content}</div>", unsafe_allow_html=True)
        progress.progress(int((i / len(sections)) * 100))
        time.sleep(0.3)

    st.success("Completed")

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.markdown(
    "<p style='text-align:center;font-size:13px;color:#666;'>AI-Q Assistant</p>",
    unsafe_allow_html=True
)
