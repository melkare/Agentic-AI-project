"""Pydantic models used by the API and agents."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ImageAnalysis(BaseModel):
    """Structured analysis of an image."""

    scene: str = Field(default="unknown")
    objects: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    quality: str = Field(default="good")
    summary: str = Field(default="")


class StoryboardScene(BaseModel):
    """A single storyboard scene."""

    title: str
    description: str
    camera_movement: str
    caption: str
    transition: str
    duration: int


class StoryboardPlan(BaseModel):
    """The planned storyboard generated from images and prompt."""

    timeline: list[StoryboardScene] = Field(default_factory=list)
    ordering: list[str] = Field(default_factory=list)
    style: str = Field(default="cinematic")
    summary: str = Field(default="")


class ScriptOutput(BaseModel):
    """Generated Remotion-based script payload."""

    composition: str
    sequence: list[str] = Field(default_factory=list)
    transitions: list[str] = Field(default_factory=list)
    text: list[str] = Field(default_factory=list)
    image_components: list[str] = Field(default_factory=list)
    music_placeholders: list[str] = Field(default_factory=list)
    source: str = Field(default="fallback")


class CompilerResult(BaseModel):
    """Result of a compilation attempt."""

    success: bool
    output_path: str | None = None
    error: str | None = None


class RenderResult(BaseModel):
    """Result of the rendering step."""

    output_path: str
    format: str = Field(default="mp4")
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerateRequest(BaseModel):
    """Request payload accepted by the generation endpoint."""

    prompt: str
    images: list[str] = Field(default_factory=list)
