# Deep Research Agent (Streamlit)

Quick start:

1. Copy `.env.example` to `.env` and fill in your API keys.

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run ultimate_research_agent.py
```

Notes:
- The apps are refactored to read `NVIDIA_API_KEY` and `TAVILY_API_KEY` from environment variables or a `.env` file via `config.py`.
- The apps are refactored to read `NVIDIA_API_KEY` and `TAVILY_API_KEY` from environment variables or a `.env` file via `config.py`.

- API backend: `agent_api.py` exposes `/run` (POST) and `/ws/run` (WebSocket) for streaming.
- CLI: `run_agent_cli.py topic` runs the agent from the command line.
- Training: `train/train.py` is a tiny training scaffold. Example dry-run:

```bash
python train/train.py --dry-run
```

Tests and CI:

- Run unit tests locally:

```bash
python -m pytest -q
```

- A GitHub Actions workflow is included at `.github/workflows/ci.yml`.

Deployment:
- Services run locally at:
	- Streamlit UI: `http://127.0.0.1:8501`
	- FastAPI docs: `http://127.0.0.1:8000/docs`
	- WebSocket endpoint: `ws://127.0.0.1:8000/ws/run`

If you'd like a public URL, I can set up ngrok or deploy to Render/Fly.
 
Docker / Deployment
-------------------
You can run the project in Docker (both API and UI in one container for convenience) or use `docker-compose` to run locally.

Build the image:
```bash
docker build -t deep-research-agent .
```

Run with Docker (ports 8000 and 8501 exposed):
```bash
docker run -e NVIDIA_API_KEY=your_key -e TAVILY_API_KEY=your_key -p 8000:8000 -p 8501:8501 deep-research-agent
```

Or use docker-compose:
```bash
docker-compose up --build
```

Deploy to Render / Fly:
- Push this repo to GitHub.
- Create a new Web Service on Render using Docker; point it to the Dockerfile in this repo and set environment variables `NVIDIA_API_KEY` and `TAVILY_API_KEY` in the Render dashboard. Expose ports 8000/8501 as separate services if you want independent endpoints.

