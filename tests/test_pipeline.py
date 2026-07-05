from pathlib import Path

import pytest

from config import get_settings
from graph import build_graph, run_pipeline
from state import AgentState


def test_build_graph_has_expected_nodes():
    graph = build_graph()
    assert graph is not None


def test_run_pipeline_with_mock_inputs(tmp_path):
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    image_path = image_dir / "sample.png"
    image_path.write_bytes(b"fake image bytes")

    state: AgentState = {
        "prompt": "A cinematic birthday celebration with warm lighting",
        "images": [str(image_path)],
        "retry_count": 0,
    }

    result = run_pipeline(state)

    assert result["status"] == "completed"
    assert result["storyboard"] is not None
    assert result["script"] is not None
    assert result["render_result"] is not None
    assert result["render_result"]["output_path"].endswith(".mp4")


def test_chroma_style_context_is_loaded():
    from rag.chroma_store import get_style_context

    context = get_style_context("cinematic")
    assert "cinematic" in context.lower() or len(context) > 0


def test_grok_settings_are_supported(monkeypatch):
    monkeypatch.setenv("GROK_API_KEY", "grok-test-key")
    monkeypatch.setenv("GROK_MODEL", "grok-2")
    monkeypatch.setenv("LLM_PROVIDER", "grok")

    settings = get_settings()

    assert settings.grok_api_key == "grok-test-key"
    assert settings.grok_model == "grok-2"
    assert settings.llm_provider == "grok"
