# System Architecture — Deep Research Agent (concise)

## Overview
The system is composed of three layers:

- UI layer: Streamlit app (`ultimate_research_agent.py`) — user input, settings, streaming progress, saved runs.
- API layer: FastAPI (`agent_api.py`) — programmatic access to run jobs synchronously (future websocket support).
- Agent core: `agent_core.py` — StateGraph orchestration (planner, researcher, writer), pluggable LLM/search tools, mock fallbacks.

Support components:
- `config.py` + `.env` — secrets and runtime config.
- `storage.py` (`runs.json`) — persisted run history.
- `specs.md`, `architecture.md` — documentation/requirements.

## Component responsibilities
- Streamlit UI: handles user flows, shows progress, triggers agent runs via `agent_core.run_agent`/`stream_agent`, persists runs via `storage.save_run`.
- FastAPI: exposes `/run` endpoint that adapts incoming JSON to the agent-core message format and returns serialized results.
- Agent core: builds and compiles the `StateGraph` with three nodes — `planner`, `researcher`, `writer`. Uses real tool implementations when available, otherwise mocks for local testing.

## Data flow (request -> report)
1. User submits topic in UI or POSTs to `/run`.
2. UI/API creates `inputs` with a single `HumanMessage` and calls `stream_agent` for streaming or `run_agent` for final result.
3. StateGraph executes: planner -> researcher (loop) -> writer. Intermediate outputs are streamed back to caller.
4. Final state contains `messages` (report). UI displays and saves report; API returns JSON.

## Extensibility points
- Replace mock `MockLLM` / `MockSearch` with concrete adapters (NVIDIA, OpenAI, Google) by implementing `invoke` compatibility.
- Add WebSocket streaming by converting `agent_api` to include an `async` stream endpoint that yields messages.
- Add background job queue (Redis/RQ, Celery) for long jobs and return job IDs.
- Add authentication and per-user storage for multi-user deployments.

## Scaling & deployment notes
- For local dev: `streamlit run ultimate_research_agent.py` is sufficient; mock mode allows offline testing.
- For production: host `agent_api` behind Uvicorn+Gunicorn, secure API keys via environment or secret manager, use Redis-backed queue for concurrency, and add logging/metrics.

## Next recommended implementation
- Add WebSocket streaming endpoint in `agent_api.py` and make the Streamlit UI connect (via JavaScript or polling) to show partial outputs in real-time.
- Implement an async worker queue and persist job status to `runs.json` or a small DB.
