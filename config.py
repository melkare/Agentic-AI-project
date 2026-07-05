"""Application configuration and environment settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from pydantic import BaseModel, Field

BASE_DIR: Final[Path] = Path(__file__).resolve().parent
INPUTS_DIR: Final[Path] = BASE_DIR / "inputs"
OUTPUTS_DIR: Final[Path] = BASE_DIR / "outputs"
STYLES_DIR: Final[Path] = BASE_DIR / "styles"
REMOTION_DIR: Final[Path] = BASE_DIR / "remotion"


class Settings(BaseModel):
    """Runtime configuration for the video generation pipeline."""

    app_name: str = Field(default="ai-video-studio")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    openai_api_key: str | None = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    grok_api_key: str | None = Field(default_factory=lambda: os.getenv("GROK_API_KEY"))
    grok_model: str = Field(default_factory=lambda: os.getenv("GROK_MODEL", "grok-2-latest"))
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openai").strip().lower())
    max_retries: int = Field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    output_dir: str = Field(default_factory=lambda: os.getenv("OUTPUT_DIR", str(OUTPUTS_DIR)))
    input_dir: str = Field(default_factory=lambda: os.getenv("INPUT_DIR", str(INPUTS_DIR)))
    chroma_persist_dir: str = Field(default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "vectorstore")))


def get_settings() -> Settings:
    """Return a configured settings object."""

    return Settings()
