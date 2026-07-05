"""Chroma-based retrieval helpers for prompt augmentation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from config import get_settings
from utils.logging import get_logger

logger = get_logger(__name__)

try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency fallback
    chromadb = None


class ChromaRAG:
    """Simple wrapper around Chroma for style and documentation context."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.persist_dir = Path(self.settings.chroma_persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        if chromadb is not None:
            try:
                self.client = chromadb.PersistentClient(path=str(self.persist_dir))
            except Exception as exc:  # pragma: no cover - runtime fallback
                logger.exception("Unable to initialize Chroma client: %s", exc)

    def initialize(self) -> None:
        """Seed the vector store with style files and Remotion docs snippets."""
        if self.client is None:
            return
        collection_name = "video_styles"
        try:
            collection = self.client.get_or_create_collection(collection_name)
            style_files = [
                Path(__file__).resolve().parent.parent / "styles" / "cinematic.txt",
                Path(__file__).resolve().parent.parent / "styles" / "birthday.txt",
                Path(__file__).resolve().parent.parent / "styles" / "corporate.txt",
                Path(__file__).resolve().parent.parent / "styles" / "travel.txt",
            ]
            docs: list[str] = []
            ids: list[str] = []
            for file_path in style_files:
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    docs.append(content)
                    ids.append(file_path.stem)
            if docs:
                collection.add(documents=docs, ids=ids)
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.exception("Unable to seed Chroma collection: %s", exc)

    def query(self, query_text: str, limit: int = 3) -> list[dict[str, Any]]:
        """Query the vector store for similar context."""
        if self.client is None:
            return []
        try:
            collection = self.client.get_collection("video_styles")
            results = collection.query(query_texts=[query_text], n_results=limit)
            documents = results.get("documents", [[]])[0]
            return [{"text": doc} for doc in documents]
        except Exception as exc:  # pragma: no cover - runtime fallback
            logger.exception("Chroma query failed: %s", exc)
            return []


def get_style_context(style: str) -> str:
    """Load a style file from disk as plain-text context."""
    style_path = Path(__file__).resolve().parent.parent / "styles" / f"{style}.txt"
    if style_path.exists():
        return style_path.read_text(encoding="utf-8")
    return f"Style context for {style}"
