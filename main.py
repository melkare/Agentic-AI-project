"""Application entrypoint for the FastAPI service."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import get_settings
from graph.graph import run_pipeline
from models.pipeline import GenerateRequest
from state import AgentState
from utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health probe endpoint."""
    return {"status": "ok"}


@app.post("/generate")
def generate(request: GenerateRequest) -> dict[str, object]:
    """Generate a storyboard, script, and video artifact."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    state: AgentState = {
        "prompt": request.prompt,
        "images": request.images,
        "retry_count": 0,
    }
    result = run_pipeline(state)
    return {"status": result.get("status", "completed"), "result": result}


@app.post("/render")
def render_video() -> dict[str, object]:
    """Render a placeholder video artifact."""
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "rendered.mp4"
    output_path.write_bytes(b"render placeholder")
    return {"output_path": str(output_path)}


@app.get("/status")
def status() -> dict[str, object]:
    """Simple status endpoint."""
    return {"status": "ready", "service": settings.app_name}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
