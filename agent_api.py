"""Simple FastAPI backend to run the research agent via HTTP."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from agent_core import run_agent, stream_agent

app = FastAPI(title="Deep Research Agent API")


class RunRequest(BaseModel):
    topic: str


@app.post("/run")
def run(req: RunRequest):
    inputs = {"messages": [ {"content": req.topic, "type": "human"} ]}
    # agent_core expects actual message objects; construct simple wrapper for compatibility
    from langchain_core.messages import HumanMessage
    inputs = {"messages": [HumanMessage(content=req.topic)]}
    final = run_agent(inputs)
    # final may contain message objects; serialize conservatively
    out = {}
    if "messages" in final:
        msgs = final["messages"]
        out["messages"] = [getattr(m, 'content', str(m)) for m in msgs]
    else:
        out["state"] = final
    return out


@app.websocket("/ws/run")
async def websocket_run(websocket: WebSocket):
    """Accepts a JSON message {"topic": "..."} then streams intermediate outputs.

    The generator in `stream_agent` is synchronous; run it in a background thread
    and use `asyncio.run_coroutine_threadsafe` to send JSON messages over the WebSocket.
    """
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        topic = data.get("topic")
        from langchain_core.messages import HumanMessage
        inputs = {"messages": [HumanMessage(content=topic)]}

        import asyncio, threading

        loop = asyncio.get_event_loop()

        def worker():
            # stream intermediate outputs
            try:
                for output in stream_agent(inputs):
                    coro = websocket.send_json(output)
                    asyncio.run_coroutine_threadsafe(coro, loop)
                # final state
                final = run_agent(inputs)
                if "messages" in final:
                    msgs = [getattr(m, 'content', str(m)) for m in final["messages"]]
                    coro = websocket.send_json({"final": msgs})
                else:
                    coro = websocket.send_json({"final": final})
                asyncio.run_coroutine_threadsafe(coro, loop)
            except Exception:
                pass

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        # keep connection open while worker runs
        while t.is_alive():
            await asyncio.sleep(0.1)

        await websocket.close()
    except WebSocketDisconnect:
        return
