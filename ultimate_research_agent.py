import streamlit as st
import os
import re
from typing import Annotated, List, TypedDict, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from config import apply_env, missing_keys
from agent_core import stream_agent, run_agent
from storage import save_run, list_runs
from datetime import datetime
import streamlit.components.v1 as components

# 1. API CONFIG (NVIDIA & TAVILY) - read from config/.env
from config import apply_env, missing_keys

apply_env()
missing = missing_keys()
if missing:
    # show a warning in the UI if keys are missing, but don't crash on import
    pass

st.set_page_config(page_title="NVIDIA AI-Q Deep Research", layout="wide", page_icon="🛡️")

apply_env()

missing = missing_keys()
if missing:
    st.sidebar.warning(f"Missing env keys: {', '.join(missing)}")

# 2. THE BRAIN & TOOLS (Updated to langchain-tavily)
llm = ChatNVIDIA(model="nvidia/llama-3.1-nemotron-70b-instruct")
search_tool = TavilySearch(max_results=3)

class AgentState(TypedDict):
    messages: Annotated[List, list]
    research_plan: List[str]
    collected_data: List[str]
    steps_taken: int

# --- NODES ---
def planner(state: AgentState):
    query = state["messages"][0].content
    prompt = f"Break this into 3 specific research goals: {query}. Output only a numbered list."
    response = llm.invoke([SystemMessage(content="You are a Technical Researcher."), HumanMessage(content=prompt)])
    tasks = re.findall(r'\d+\.\s*(.*)', response.content)
    return {"research_plan": tasks[:3], "steps_taken": 0}

def researcher(state: AgentState):
    idx = state["steps_taken"]
    task = state["research_plan"][idx % len(state["research_plan"])]
    results = search_tool.invoke({"query": task})
    return {"collected_data": [f"Goal: {task}\nResult: {results}"], "steps_taken": idx + 1}

def writer(state: AgentState):
    context = "\n---\n".join(state["collected_data"])
    query = state["messages"][0].content
    prompt = f"Write a deep technical report based on: {context} for: {query}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

def router(state: AgentState) -> Literal["researcher", "writer"]:
    return "researcher" if state["steps_taken"] < len(state.get("research_plan", [])) else "writer"

# BUILD GRAPH
builder = StateGraph(AgentState)
builder.add_node("planner", planner); builder.add_node("researcher", researcher); builder.add_node("writer", writer)
builder.add_edge(START, "planner"); builder.add_edge("planner", "researcher")
builder.add_conditional_edges("researcher", router); builder.add_edge("writer", END)
app = builder.compile()

# --- STREAMLIT UI ---
st.title("🛡️ NVIDIA AI-Q: Deep Research Interface")
st.markdown("---")

# Modern styling and header
css = """
<style>
body {
    background: linear-gradient(120deg, #0f172a 0%, #071033 100%);
    color: #e6eef8;
}
.hero {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 18px;
    border-radius: 12px;
    background: linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    box-shadow: 0 4px 30px rgba(2,6,23,0.6);
}
.hero h1 { margin: 0; font-size: 28px }
.hero p { margin: 0; opacity: 0.8 }
.card {
    background: rgba(255,255,255,0.02);
    padding: 12px;
    border-radius: 10px;
}
.accent { color: #7dd3fc }
.logo-anim { width: 96px; height: 96px }
</style>
"""

st.markdown(css, unsafe_allow_html=True)

st.markdown(
        """
        <div class="hero">
            <div>
                <svg class="logo-anim" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="g" x1="0%" x2="100%">
                            <stop stop-color="#7dd3fc" offset="0%" />
                            <stop stop-color="#60a5fa" offset="100%" />
                        </linearGradient>
                    </defs>
                    <circle cx="50" cy="50" r="40" fill="url(#g)">
                        <animate attributeName="r" values="36;40;36" dur="3s" repeatCount="indefinite" />
                    </circle>
                    <text x="50%" y="54%" font-size="18" fill="#041d3a" text-anchor="middle" font-family="Arial">AI-Q</text>
                </svg>
            </div>
            <div>
                <h1>Deep Research Agent <span class="accent">UI</span></h1>
                <p>Enter a topic, watch the agent plan, search and compose a deep technical report.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
)

st.sidebar.header("Agent Settings")
backend = st.sidebar.selectbox("Backend", ["auto (NVIDIA if available)", "mock local"])
steps = st.sidebar.slider("Max research steps", 1, 6, 3)

# Example topics
st.sidebar.markdown("**Example topics**")
examples = [
    "Compare Blackwell vs Hopper NVLink performance",
    "Design efficient data pipeline for multi-GPU training",
    "Survey recent advances in self-supervised learning",
]
chosen = st.sidebar.selectbox("Pick an example", ["(choose)"] + examples)
if st.sidebar.button("Use example") and chosen != "(choose)":
    user_input = chosen
    st.experimental_set_query_params(topic=chosen)

# Saved runs
st.sidebar.markdown("---")
st.sidebar.markdown("**Saved runs**")
runs = list_runs(20)
for r in runs:
    with st.sidebar.expander(f"{r['id']}: {r['topic']} ({r['ts'][:19]})", expanded=False):
        st.write(r.get("metadata", {}))
        st.write(r["report"][:1000])

user_input = st.text_input("Enter Topic", placeholder="Compare Blackwell vs Hopper...")

if st.button("🚀 Run Deep Analysis"):
    if not user_input:
        st.error("Please enter a research topic first.")
    else:
        inputs = {"messages": [HumanMessage(content=user_input)]}
        st.info("Agent running — streaming progress below")
        progress = st.progress(0)
        step_count = 0
        # Stream outputs from agent_core
        for output in stream_agent(inputs):
            step_count += 1
            progress.progress(min(step_count * 100 // max(1, steps), 100))
            for node, _ in output.items():
                st.write(f"✅ Phase **{node}** complete.")
        final_state = run_agent(inputs)
        st.markdown("### 📊 Final Analysis Report")
        report_text = None
        if "messages" in final_state:
            st.success("Report Generated Successfully")
            report_text = final_state["messages"][-1].content
            st.write(report_text)
        else:
            st.write(final_state)
            report_text = str(final_state)
        # Save run
        try:
            entry = save_run(user_input, report_text, metadata={"backend": backend, "steps": steps})
            st.success(f"Saved run as #{entry['id']} at {entry['ts'][:19]}")
        except Exception as e:
            st.error(f"Failed to save run: {e}")
        st.balloons()

# WebSocket-run option (in-browser streaming)
st.markdown("---")
st.markdown("**Or run via WebSocket (live streaming to this browser)**")
ws_topic = st.text_input("Topic for WebSocket run", value="")
if st.button("🚀 Run (WebSocket)"):
        if not ws_topic:
                st.error("Enter a topic for WebSocket run.")
        else:
                # Embed a small HTML+JS component that connects to the websocket endpoint
                escaped = ws_topic.replace('"', '&quot;')
                # Ensure the embedded JS connects to the FastAPI backend (port 8000)
                html = f"""
                <div id="ws-root">
                    <div style="background:#001122;color:#cfeffd;border-radius:8px;padding:12px;">
                        <strong>WebSocket Stream</strong>
                        <div id="messages" style="white-space:pre-wrap;margin-top:8px;max-height:400px;overflow:auto;font-family:monospace;"></div>
                    </div>
                </div>
                <script>
                (function(){{
                    const out = document.getElementById('messages');
                    const topic = "{escaped}";
                      const wsScheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                      // connect explicitly to backend port 8000 where FastAPI runs
                      const host = window.location.hostname;
                      const url = wsScheme + '//' + host + ':8000/ws/run';
                    const ws = new WebSocket(url);
                    ws.onopen = () => {{ ws.send(JSON.stringify({{topic: topic}})); out.innerText += '\n[connected]\n'; }};
                    ws.onmessage = (ev) => {{ out.innerText += '\n' + ev.data + '\n'; out.scrollTop = out.scrollHeight; }};
                    ws.onclose = () => {{ out.innerText += '\n[closed]\n'; }};
                    ws.onerror = (e) => {{ out.innerText += '\n[error] ' + e + '\n'; }};
                }})();
                </script>
                """
                components.html(html, height=480)