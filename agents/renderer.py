"""Renderer agent for producing the final MP4 artifact."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from config import get_settings
from utils.logging import get_logger

logger = get_logger(__name__)


class RendererAgent:
    """Copy or render an MP4 into the output directory."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, compiler_result: dict[str, Any]) -> dict[str, Any]:
        """Render the final video and return metadata."""
        output_dir = Path(self.settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        source_path = Path(compiler_result.get("output_path", ""))
        if source_path.exists() and source_path.suffix == ".mp4":
            target_path = output_dir / source_path.name
            shutil.copy2(source_path, target_path)
            return {"output_path": str(target_path), "format": "mp4", "metadata": {"source": str(source_path)}}

        placeholder_path = output_dir / "placeholder.mp4"
        placeholder_path.write_bytes(b"placeholder")
        return {"output_path": str(placeholder_path), "format": "mp4", "metadata": {"source": "fallback"}}
