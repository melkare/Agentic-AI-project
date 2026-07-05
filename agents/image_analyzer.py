"""Image analyzer agent."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from openai import OpenAI

from config import get_settings
from models.pipeline import ImageAnalysis
from utils.logging import get_logger

logger = get_logger(__name__)


class ImageAnalyzerAgent:
    """Analyze images using OpenAI vision-style capabilities with fallback."""

    def __init__(self) -> None:
        self.settings = get_settings()
        provider = (self.settings.llm_provider or "openai").lower()
        is_grok = provider in {"grok", "xai", "x-ai"}
        api_key = self.settings.grok_api_key if is_grok else self.settings.openai_api_key
        base_url = "https://api.x.ai/v1" if is_grok else None
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None
        self.model_name = self.settings.grok_model if is_grok else self.settings.openai_model

    def run(self, images: list[str], prompt: str) -> dict[str, Any]:
        """Analyze image content and produce structured metadata."""

        analyses: list[dict[str, Any]] = []
        for image_path in images:
            path = Path(image_path)
            if not path.exists():
                continue
            encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
            analysis = self._analyze_with_fallback(encoded, path.name, prompt)
            analyses.append(analysis)

        if not analyses:
            analyses.append(self._build_default_analysis(prompt))

        return {"images": analyses}

    def _analyze_with_fallback(self, encoded: str, file_name: str, prompt: str) -> dict[str, Any]:
        if self.client is None:
            return self._build_default_analysis(prompt)

        try:
            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {
                        "role": "system",
                        "content": "You are a vision assistant that outputs strict JSON for video planning.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": f"Analyze this image for a video prompt: {prompt}"},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{encoded}",
                            },
                        ],
                    },
                ],
                text={"format": {"type": "json_schema", "name": "image_analysis", "schema": {"type": "object", "properties": {"scene": {"type": "string"}, "objects": {"type": "array", "items": {"type": "string"}}, "people": {"type": "array", "items": {"type": "string"}}, "emotions": {"type": "array", "items": {"type": "string"}}, "quality": {"type": "string"}, "summary": {"type": "string"}}, "required": ["scene", "objects", "people", "emotions", "quality", "summary"]}}},
            )
            text = response.output_text
            Parsed = json.loads(text)
            return Parsed
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.exception("Vision analysis failed for %s: %s", file_name, exc)
            return self._build_default_analysis(prompt)

    def _build_default_analysis(self, prompt: str) -> dict[str, Any]:
        model = ImageAnalysis(
            scene="cinematic scene",
            objects=["subject", "background"],
            people=["person"],
            emotions=["joy"],
            quality="good",
            summary=f"Fallback analysis for prompt: {prompt}",
        )
        return model.model_dump()
