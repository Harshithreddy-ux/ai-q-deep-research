# AI-Q Deep Research Agent

A stable, production-safe deep research application using **Groq** and **Tavily**, built with **Streamlit**.

---

## ✅ What this version guarantees

- ✔ No LangChain
- ✔ No `invoke()` / `predict()` confusion
- ✔ No BadRequestError loops
- ✔ Uses official Groq SDK
- ✔ Streamlit Cloud compatible
- ✔ Real research output (not demo text)
- ✔ Easy to extend UI later

---

## 🏗 Architecture

- Direct **Groq SDK** for LLM inference  
- Direct **Tavily SDK** for web search  
- Plain string prompts (no message abstractions)  
- Single Streamlit entrypoint: `deep_research_app.py`

---

## 🚀 How to run (Local)

```bash
pip install streamlit groq tavily-python
streamlit run deep_research_app.py
