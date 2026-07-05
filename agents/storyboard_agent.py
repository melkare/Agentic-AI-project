"""Storyboard planning agent."""

from __future__ import annotations

from typing import Any

from models.pipeline import StoryboardPlan, StoryboardScene
from utils.logging import get_logger

logger = get_logger(__name__)


class StoryboardAgent:
    """Turn image analyses and prompt into a storyboard plan."""

    def run(self, analysis: dict[str, Any], prompt: str) -> dict[str, Any]:
        """Generate a timeline with scene ordering and shot details."""

        scenes: list[StoryboardScene] = []
        analyses = analysis.get("images", [])
        for index, item in enumerate(analyses, start=1):
            scenes.append(
                StoryboardScene(
                    title=f"Scene {index}",
                    description=item.get("summary", "A polished scene"),
                    camera_movement="slow dolly in",
                    caption=f"{prompt} - scene {index}",
                    transition="fade",
                    duration=4,
                )
            )

        plan = StoryboardPlan(
            timeline=scenes,
            ordering=[f"scene_{idx}" for idx in range(1, len(scenes) + 1)],
            style="cinematic",
            summary=f"Storyboard for: {prompt}",
        )
        return plan.model_dump()
