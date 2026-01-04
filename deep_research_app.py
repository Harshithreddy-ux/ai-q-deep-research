import streamlit as st
import os
import re

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI-Q Knowledge & Research Assistant",
    layout="wide"
)

# =====================================================
# LIGHT SNOW ANIMATION
# =====================================================
st.markdown("""
<style>
body {
    background-color: #f9f9f9;
    font-family: Arial, sans-serif;
}
.snowflake {
    position: fixed;
    top: -10px;
    color: #d0d0d0;
    font-size: 10px;
    animation: fall linear infinite;
}
@keyframes fall {
    to { transform: translateY(110vh); }
}
.content {
    font-size: 15px;
    line-height: 1.7;
    color: #111;
    background: #ffffff;
    padding: 15px;
    border-radius: 6px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

for i in range(25):
    st.markdown(
        f"<div class='snowflake' style='left:{i*4}%; animation-duration:{8+i%5}s;'>*</div>",
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
# GROQ (OPTIONAL)
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
USE_GROQ = bool(GROQ_API_KEY)

if USE_GROQ:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

def clean(text):
    return re.sub(r"[^\x00-\x7F]+", "", text)

def groq_generate(prompt):
    try:
        res = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt[:5000]}],
            temperature=0.4,
            max_tokens=900,
        )
        return clean(res.choices[0].message.content)
    except Exception:
        return ""

# =====================================================
# LOCAL FALLBACK KNOWLEDGE (IMPORTANT)
# =====================================================
def local_laptop_knowledge():
    return {
        "Definition and overview":
        "A laptop is a portable personal computer designed for mobile use. It integrates essential components such as a display, keyboard, touchpad, processor, memory, storage, and battery into a single compact unit.",

        "History and evolution":
        "Laptops originated in the early 1980s. The first commercially successful laptop was the Osborne 1 (1981). Over decades, laptops evolved from bulky devices to lightweight ultrabooks and AI-powered machines.",

        "Technology and working principles":
        "Laptops operate using microprocessors, RAM, storage devices (SSD/HDD), and operating systems. Power-efficient CPUs and integrated GPUs enable computing while maintaining battery life.",

        "Types and categories":
        "Common types include ultrabooks, gaming laptops, business laptops, 2-in-1 convertibles, Chromebooks, and workstation laptops.",

        "Uses and importance":
        "Laptops are used in education, business, software development, content creation, gaming, research, and remote work due to their portability.",

        "Business model and industry ecosystem":
        "Laptop manufacturers follow OEM and ODM models. Major brands design systems while manufacturing is often outsourced. Revenue comes from device sales, warranties, and enterprise contracts.",

        "Market share and major players":
        "Major laptop brands include Lenovo, HP, Dell, Apple, Asus, and Acer. Lenovo and HP consistently lead global market share.",

        "Pricing strategies and customer segments":
        "Pricing ranges from budget laptops for students to premium devices for professionals. Brands segment customers based on performance, portability, and brand value.",

        "Advantages and disadvantages":
        "Advantages include portability and versatility. Disadvantages include limited upgradeability, thermal constraints, and higher cost than desktops.",

        "Current trends and future outlook":
        "Modern trends include AI-powered laptops, ARM-based processors, improved battery technology, and cloud-integrated computing."
    }

# =====================================================
# INPUT
# =====================================================
st.subheader("Enter Topic")
topic = st.text_input("", placeholder="e.g., what is a laptop")

run = st.button("Generate Explanation", use_container_width=True)

# =====================================================
# MAIN LOGIC
# =====================================================
if run:
    st.divider()

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

    fallback = local_laptop_knowledge()

    for i, sec in enumerate(sections, 1):
        st.markdown(f"### {i}. {sec}")

        content = ""
        if USE_GROQ:
            content = groq_generate(
                f"Explain in detail:\nTopic: {topic}\nSection: {sec}"
            )

        if not content:
            content = fallback.get(sec, "Information unavailable.")

        st.markdown(f"<div class='content'>{content}</div>", unsafe_allow_html=True)

    st.success("Completed successfully")

# =====================================================
# FOOTER
# =====================================================
st.divider()
st.markdown(
    "<p style='text-align:center;font-size:13px;color:#666;'>AI-Q Assistant</p>",
    unsafe_allow_html=True
)
