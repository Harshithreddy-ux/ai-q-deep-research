# Deep Research Agent — Requirements & Metrics (concise)

## 1. Goal
- Provide a web-accessible research agent that: accepts a user research topic, plans a short research agenda, searches relevant sources, and composes a detailed technical report.

## 2. Primary user flows
- Web UI (Streamlit): enter topic -> run agent -> stream progress -> view and save final report.
- HTTP API (FastAPI): POST /run with JSON {topic} -> returns final report (and optionally stream progress).

## 3. Inputs / Outputs
- Input: short natural-language topic string and optional settings (max steps, backend).
- Output: structured report text, run metadata (timestamp, backend used, steps), and collected raw search snippets.

## 4. Success metrics
- Relevance/accuracy: human-rated relevance of the final report (0–5).
- Completeness: fraction of planned sub-goals addressed in report.
- Latency: time to first intermediate result and time to final report (target < 30s for mocks, <120s for live LLMs).
- Reliability: successful runs / total runs (target > 95%).
- Cost (if using paid APIs): $ per run budget threshold.

## 5. Constraints & non-functional
- Secrets must not be hard-coded; use `.env` or platform secrets.
- Allow offline/mock mode for local testing without API keys.
- Persist run history locally (`runs.json`) with optionally configurable retention.

## 6. MVP feature set (short-term)
- Streamlit UI with: topic input, sidebar settings, example topics, streaming progress, save-run button.
- FastAPI `/run` endpoint for programmatic access.
- Config via `config.py` + `.env.example`.
- Local JSON storage of runs and basic UI for browsing runs.
- Mock LLM/search fallback to enable local testing.

## 7. Next-phase features (later)
- WebSocket streaming for live progress and partial reports.
- Job queue / background worker for long-running experiments.
- Authentication for multi-user access.
- Model-training scaffold and dataset pipelines for custom model experiments.
- Metrics dashboard (latency, cost, success-rate) with logging to file or monitoring system.

## 8. Minimal evaluation process
- Create a small set of 10 benchmark topics. For each, run agent and collect final reports.
- Have 3 reviewers rate relevance (0–5) and completeness (0–1). Compute average scores and identify failure modes.

## 9. Acceptance criteria for MVP
- UI runs successfully in mock mode with no API key.
- With valid API keys, the app can invoke external LLM and search tools and return a readable report.
- Run history persists and is viewable in the UI.
- Basic README + run instructions present.
