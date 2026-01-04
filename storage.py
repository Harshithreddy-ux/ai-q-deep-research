import json
from pathlib import Path
from datetime import datetime

RUNS_PATH = Path(__file__).parent / "runs.json"


def _load_runs():
    if not RUNS_PATH.exists():
        return []
    try:
        return json.loads(RUNS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_runs(runs):
    RUNS_PATH.write_text(json.dumps(runs, indent=2, ensure_ascii=False), encoding="utf-8")


def save_run(topic: str, report: str, metadata: dict | None = None):
    runs = _load_runs()
    entry = {
        "id": len(runs) + 1,
        "topic": topic,
        "report": report,
        "metadata": metadata or {},
        "ts": datetime.utcnow().isoformat() + "Z",
    }
    runs.insert(0, entry)
    _save_runs(runs)
    return entry


def list_runs(limit: int = 50):
    runs = _load_runs()
    return runs[:limit]
