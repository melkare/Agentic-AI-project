"""Typed state definitions for the LangGraph-style pipeline."""

from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """State shaped for the agent workflow."""

    prompt: str
    images: list[str]
    analysis: dict[str, Any]
    storyboard: dict[str, Any]
    script: dict[str, Any]
    retrieval_context: str
    compiler_error: str | None
    retry_count: int
    status: str
    render_result: dict[str, Any]
    output_path: str | None
    metadata: dict[str, Any]
