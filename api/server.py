"""FastAPI backend — streams investigation events via Server-Sent Events."""
from __future__ import annotations

import asyncio
import json
import os
import queue
import threading
from pathlib import Path
from typing import Any

# Load .env from project root if present
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from phase2_agent.commander import IncidentCommander
from phase3_evaluator import evaluator

app = FastAPI(title="Vigil API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_SCENARIO = json.loads(
    (Path(__file__).parent.parent / "phase2_agent/scenarios/packet_loss_sj.json").read_text()
)


def _result_preview(tool: str, result: dict) -> str:
    """Produce a short, human-readable summary of a tool result."""
    if tool == "run_spl_query":
        stats = result.get("stats", {})
        if "avg_out_errors" in stats:
            return (
                f"avg_out_errors={stats['avg_out_errors']:,}  "
                f"avg_drops={stats['avg_drops']:,}  "
                f"spike_at={stats.get('spike_at','')}"
            )
        if "top_src" in stats:
            return f"top_src={stats['top_src']}  pct={stats.get('top_src_pct')}%  {stats.get('anomaly','')}"
        return stats.get("message", "no events")
    if tool == "generate_spl":
        return result.get("spl", "")[:120]
    if tool == "search_indexes":
        return f"{result.get('total', 0)} indexes available"
    if tool == "get_knowledge_objects":
        return f"{result.get('total', 0)} objects"
    if tool == "get_network_topology":
        return f"{result.get('total_devices', 0)} device(s)"
    if tool == "get_telemetry_metrics":
        m = result.get("metrics", {})
        if m:
            return (
                f"out_errors={m.get('out_errors','?')}  "
                f"utilization={m.get('utilization_pct','?')}%  "
                f"anomaly={result.get('anomaly')}"
            )
    return str(result)[:120]


def _is_anomaly(tool: str, result: dict) -> bool:
    if tool == "run_spl_query":
        return bool(result.get("stats", {}).get("anomaly"))
    if tool == "get_telemetry_metrics":
        return bool(result.get("anomaly"))
    return False


@app.get("/api/scenario")
async def get_scenario() -> dict:
    return _SCENARIO


@app.get("/api/run")
async def run_investigation() -> StreamingResponse:
    q: queue.Queue[dict | None] = queue.Queue()

    def background() -> None:
        commander = IncidentCommander()

        def on_event(event_type: str, data: Any) -> None:
            if event_type == "state_change":
                event: dict = {
                    "type": "state_change",
                    "state": data.get("to") or data.get("state"),
                }
                if "from" in data:
                    event["from_state"] = data["from"]
                q.put(event)
            elif event_type == "tool_call":
                result = data.get("result", {})
                q.put({
                    "type": "tool_call",
                    "tool": data["tool"],
                    "input_preview": str(list(data.get("input", {}).values())[:1])[:80],
                    "result_preview": _result_preview(data["tool"], result),
                    "duration_ms": data.get("duration_ms", 0),
                    "anomaly": _is_anomaly(data["tool"], result),
                    "input_full": data.get("input_full", ""),
                    "result_full": data.get("result_full", ""),
                })

        try:
            report = commander.run(_SCENARIO, callback=on_event)
            q.put({
                "type": "report",
                "data": {
                    "incident_id": report.incident_id,
                    "final_state": report.final_state,
                    "hypothesis": report.hypothesis,
                    "evidence": report.evidence,
                    "tool_calls": report.tool_calls,
                    "recommended_action": report.recommended_action,
                    "confidence": report.confidence,
                    "total_tokens": report.total_tokens,
                    "input_tokens": report.input_tokens,
                    "output_tokens": report.output_tokens,
                    "duration_secs": report.duration_secs,
                },
            })

            eval_results = evaluator.evaluate(report)
            q.put({"type": "eval_results", "data": eval_results})
        except Exception as exc:
            q.put({"type": "error", "message": str(exc)})
        finally:
            q.put(None)

    threading.Thread(target=background, daemon=True).start()

    async def stream():
        while True:
            try:
                item = q.get_nowait()
                if item is None:
                    yield 'data: {"type":"done"}\n\n'
                    break
                yield f"data: {json.dumps(item)}\n\n"
            except queue.Empty:
                await asyncio.sleep(0.05)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Serve built React app in production (SPA catch-all — must be last)
_dist = Path(__file__).parent.parent / "ui/dist"
if _dist.exists():
    from fastapi.responses import FileResponse

    # Serve static assets at /assets so API routes at /api/* take priority
    app.mount("/assets", StaticFiles(directory=str(_dist / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = "") -> FileResponse:  # noqa: ARG001
        return FileResponse(str(_dist / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
