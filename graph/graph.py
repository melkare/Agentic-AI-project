"""LangGraph-style workflow orchestration for the pipeline."""

from __future__ import annotations

from typing import Any, Callable

from agents.compiler import CompilerAgent
from agents.image_analyzer import ImageAnalyzerAgent
from agents.renderer import RendererAgent
from agents.script_generator import ScriptGeneratorAgent
from agents.storyboard_agent import StoryboardAgent
from state import AgentState
from utils.logging import get_logger

logger = get_logger(__name__)


def build_graph() -> Any:
    """Create a simple graph object with the requested workflow."""

    return {"nodes": ["analyzer", "storyboard", "generator", "compiler", "renderer"]}


def run_pipeline(state: AgentState) -> AgentState:
    """Execute the full pipeline using the implemented agents."""

    prompt = state.get("prompt", "")
    images = state.get("images", [])

    analyzer = ImageAnalyzerAgent()
    storyboard_agent = StoryboardAgent()
    generator = ScriptGeneratorAgent()
    compiler = CompilerAgent()
    renderer = RendererAgent()

    analysis = analyzer.run(images, prompt)
    storyboard = storyboard_agent.run(analysis, prompt)
    generator_output = generator.run(storyboard, prompt, analysis)

    compiler_result = compiler.run(generator_output)
    if not compiler_result.get("success"):
        state["compiler_error"] = compiler_result.get("error")
        state["retry_count"] = state.get("retry_count", 0) + 1
        if state.get("retry_count", 0) < 3:
            logger.info("Compiler failed, retrying script generation")
            generator_output = generator.run(storyboard, prompt, analysis)
            compiler_result = compiler.run(generator_output)

    render_result = renderer.run(compiler_result)
    state.update(
        {
            "analysis": analysis,
            "storyboard": storyboard,
            "script": generator_output,
            "compiler_error": compiler_result.get("error") if not compiler_result.get("success") else None,
            "status": "completed" if compiler_result.get("success") else "failed",
            "render_result": render_result,
            "output_path": render_result.get("output_path"),
            "metadata": {"prompt": prompt, "images": images},
        }
    )
    return state
