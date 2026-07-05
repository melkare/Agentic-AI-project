"""Script generation agent."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from config import get_settings
from models.pipeline import ScriptOutput
from rag.chroma_store import ChromaRAG, get_style_context
from utils.logging import get_logger

logger = get_logger(__name__)


class ScriptGeneratorAgent:
    """Generate Remotion React TypeScript code from storyboard context."""

    def __init__(self) -> None:
        self.settings = get_settings()
        provider = (self.settings.llm_provider or "openai").lower()
        is_grok = provider in {"grok", "xai", "x-ai"}
        api_key = self.settings.grok_api_key if is_grok else self.settings.openai_api_key
        base_url = "https://api.x.ai/v1" if is_grok else None
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None
        self.model_name = self.settings.grok_model if is_grok else self.settings.openai_model
        self.rag = ChromaRAG()

    def run(self, storyboard: dict[str, Any], prompt: str, analysis: dict[str, Any]) -> dict[str, Any]:
        """Generate a structured script payload and fallback Remotion-compatible code."""
        style = storyboard.get("style", "cinematic")
        style_context = get_style_context(style)
        retrieval_context = self.rag.query(prompt) or [{"text": style_context}]
        context_text = "\n".join(item.get("text", "") for item in retrieval_context if item.get("text"))
        if not context_text:
            context_text = style_context

        if self.client is None:
            output = self._fallback_payload(prompt, context_text, storyboard)
            return output.model_dump()

        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {
                        "role": "system",
                        "content": "You are a senior video engineer generating Remotion React TypeScript code and strict JSON.",
                    },
                    {
                        "role": "user",
                        "content": f"Create a Remotion video script from this storyboard and prompt. Use this context:\n{context_text}\n\nStoryboard: {json.dumps(storyboard)}",
                    },
                ],
                text={"format": {"type": "json_schema", "name": "script_output", "schema": {"type": "object", "properties": {"composition": {"type": "string"}, "sequence": {"type": "array", "items": {"type": "string"}}, "transitions": {"type": "array", "items": {"type": "string"}}, "text": {"type": "array", "items": {"type": "string"}}, "image_components": {"type": "array", "items": {"type": "string"}}, "music_placeholders": {"type": "array", "items": {"type": "string"}}, "source": {"type": "string"}}, "required": ["composition", "sequence", "transitions", "text", "image_components", "music_placeholders", "source"]}}},
            )
            text = response.output_text
            data = json.loads(text)
            return data
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.exception("Script generation failed: %s", exc)
            return self._fallback_payload(prompt, context_text, storyboard).model_dump()

    def _fallback_payload(self, prompt: str, context_text: str, storyboard: dict[str, Any]) -> ScriptOutput:
        scenes = storyboard.get("timeline", [])
        sequence = [f"<Sequence durationInFrames={{600}}>{scene.get('caption', 'Scene')}</Sequence>" for scene in scenes]
        return ScriptOutput(
            composition="<Composition id='Video' durationInFrames={3600} width={1920} height={1080} fps={30} />",
            sequence=sequence,
            transitions=["fade", "wipe"],
            text=[prompt, context_text[:120]],
            image_components=["<Img src={image} />" for _ in scenes],
            music_placeholders=["<Audio src='music.mp3' volume={0.2} />"],
            source="fallback",
        )
