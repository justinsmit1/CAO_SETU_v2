"""Splits OCR'd pages into overlapping text chunks, keeping citation metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass

from cao_setu_v2.llm_pipeline.extraction import Page

CHUNK_SIZE = 1200  # characters
CHUNK_OVERLAP = 200

_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    document: str
    page_number: int
    section: str | None
    text: str


def _current_section(markdown: str, offset: int) -> str | None:
    """Last markdown heading appearing at or before `offset`."""
    section = None
    for match in _HEADING_RE.finditer(markdown):
        if match.start() > offset:
            break
        section = match.group(1).strip()
    return section


def chunk_page(page: Page) -> list[Chunk]:
    text = page.markdown.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(
                Chunk(
                    document=page.document,
                    page_number=page.page_number,
                    section=_current_section(text, start),
                    text=piece,
                )
            )
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def chunk_pages(pages: list[Page]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in pages:
        chunks.extend(chunk_page(page))
    return chunks
