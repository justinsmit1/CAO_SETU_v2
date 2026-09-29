"""CAO-aware structuring + embedding.

Generic char-count chunking (llm_pipeline.chunking) treats a CAO like any other
PDF. Dutch CAO's have a real, load-bearing structure instead: Hoofdstuk ->
Artikel -> lid, plus Bijlagen (annexes) and a version/looptijd the text is only
valid for. This module parses that structure out of the OCR'd markdown so each
retrievable unit is a legal unit (an artikel or a single lid within it) rather
than an arbitrary slice of characters, and tags each unit with the CAO version
and effective period it was ingested under so amendments don't silently
overwrite each other in the index.

Scope note: this only covers structured chunking + embedding. Hybrid
lexical/vector retrieval (BM25/Qdrant), a separate salary-table index,
werkingssfeer/applicability matching, and a CAO knowledge graph are bigger
architectural changes and are intentionally not part of this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

import numpy as np
from mistralai.client import Mistral

from setu_kern.bronnen.cao_pdf.pijplijn.embeddings import embed_texts
from setu_kern.bronnen.cao_pdf.pijplijn.extraction import Page

MAX_UNIT_SIZE = 1600  # characters; split oversized artikel/lid text further
UNIT_OVERLAP = 200

_HOOFDSTUK_RE = re.compile(
    r"^\s{0,3}#{0,6}\s*\**\s*Hoofdstuk\s+([IVXLCDM]+|\d+[a-z]?)\b[.:]?\s*(.*)$",
    re.IGNORECASE,
)
_ARTIKEL_RE = re.compile(
    r"^\s{0,3}#{0,6}\s*\**\s*Artikel\s+(\d+[a-z]?)\b[.:]?\s*(.*)$", re.IGNORECASE
)
_BIJLAGE_RE = re.compile(
    r"^\s{0,3}#{0,6}\s*\**\s*Bijlage\s+([IVXLCDM]+|\d+[a-z]?)\b[.:]?\s*(.*)$",
    re.IGNORECASE,
)
_LID_RE = re.compile(r"^\s{0,3}(\d{1,2})\.\s+(\S.*)$")
_MD_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")


@dataclass(frozen=True)
class CaoChunk:
    """One retrievable CAO legal unit (an artikel, or a single lid within one)."""

    document: str
    page_number: int  # 1-based, page the unit starts on
    hoofdstuk: str | None
    artikel: str | None
    lid: str | None
    heading: str | None
    annex: bool
    version: str | None
    effective_from: str | None
    effective_to: str | None
    text: str

    @property
    def section(self) -> str | None:
        """Human-readable breadcrumb, e.g. 'Hoofdstuk 2 > Artikel 12 lid 3 - Overwerk'."""
        parts = []
        if self.hoofdstuk:
            parts.append(f"Hoofdstuk {self.hoofdstuk}")
        if self.artikel:
            label = f"Artikel {self.artikel}"
            if self.lid:
                label += f" lid {self.lid}"
            parts.append(label)
        breadcrumb = " > ".join(parts) if parts else None
        if self.heading:
            return f"{breadcrumb} - {self.heading}" if breadcrumb else self.heading
        return breadcrumb

    def as_generic_chunk(self):
        """Bridge to llm_pipeline.chunking.Chunk, for use with the existing VectorStore."""
        from setu_kern.bronnen.cao_pdf.pijplijn.chunking import Chunk

        return Chunk(
            document=self.document,
            page_number=self.page_number,
            section=self.section,
            text=self.text,
        )


@dataclass
class _Unit:
    hoofdstuk: str | None
    artikel: str | None
    lid: str | None
    heading: str | None
    annex: bool
    page_number: int
    lines: list[str]


def _flush(unit: _Unit | None, document: str, version_kwargs: dict) -> CaoChunk | None:
    if unit is None:
        return None
    text = "\n".join(unit.lines).strip()
    if not text:
        return None
    return CaoChunk(
        document=document,
        page_number=unit.page_number,
        hoofdstuk=unit.hoofdstuk,
        artikel=unit.artikel,
        lid=unit.lid,
        heading=unit.heading,
        annex=unit.annex,
        text=text,
        **version_kwargs,
    )


def _split_oversized(chunk: CaoChunk) -> list[CaoChunk]:
    """Splits a chunk whose text exceeds MAX_UNIT_SIZE, e.g. an unstructured preamble."""
    if len(chunk.text) <= MAX_UNIT_SIZE:
        return [chunk]

    pieces = []
    start = 0
    while start < len(chunk.text):
        end = min(start + MAX_UNIT_SIZE, len(chunk.text))
        piece = chunk.text[start:end].strip()
        if piece:
            pieces.append(replace(chunk, text=piece))
        if end == len(chunk.text):
            break
        start = end - UNIT_OVERLAP
    return pieces


def parse_cao_structure(
    pages: list[Page],
    *,
    version: str | None = None,
    effective_from: str | None = None,
    effective_to: str | None = None,
) -> list[CaoChunk]:
    """Parses OCR'd CAO pages into Hoofdstuk/Artikel/lid/Bijlage-tagged chunks.

    `version`/`effective_from`/`effective_to` describe the looptijd this specific
    document covers, so amendments from a later ingest of the same CAO land as
    separate chunks (tagged with their own version) instead of overwriting the
    old text in the index.
    """
    version_kwargs = {
        "version": version,
        "effective_from": effective_from,
        "effective_to": effective_to,
    }

    document = pages[0].document if pages else ""
    chunks: list[CaoChunk] = []
    current = _Unit(
        hoofdstuk=None,
        artikel=None,
        lid=None,
        heading=None,
        annex=False,
        page_number=pages[0].page_number if pages else 1,
        lines=[],
    )

    def start_new(**overrides) -> None:
        nonlocal current
        flushed = _flush(current, document, version_kwargs)
        if flushed:
            chunks.extend(_split_oversized(flushed))
        current = replace(current, lines=[], **overrides)

    for page in pages:
        for line in page.markdown.splitlines():
            stripped = line.strip()
            if not stripped:
                current.lines.append("")
                continue

            if m := _HOOFDSTUK_RE.match(line):
                start_new(
                    hoofdstuk=m.group(1),
                    artikel=None,
                    lid=None,
                    heading=m.group(2).strip() or None,
                    annex=False,
                    page_number=page.page_number,
                )
            elif m := _BIJLAGE_RE.match(line):
                start_new(
                    artikel=None,
                    lid=None,
                    heading=f"Bijlage {m.group(1)} {m.group(2)}".strip(),
                    annex=True,
                    page_number=page.page_number,
                )
            elif m := _ARTIKEL_RE.match(line):
                start_new(
                    artikel=m.group(1),
                    lid=None,
                    heading=m.group(2).strip() or None,
                    page_number=page.page_number,
                )
            elif current.artikel and (m := _LID_RE.match(line)):
                start_new(lid=m.group(1), page_number=page.page_number)
                current.lines.append(m.group(2))
            elif m := _MD_HEADING_RE.match(line):
                start_new(heading=m.group(1).strip(), page_number=page.page_number)
            else:
                current.lines.append(stripped)

    flushed = _flush(current, document, version_kwargs)
    if flushed:
        chunks.extend(_split_oversized(flushed))

    return chunks


def build_embedding_text(chunk: CaoChunk) -> str:
    """Prefixes the legal-unit breadcrumb onto the text so embeddings capture
    context a bare paragraph would lose (e.g. which artikel a lone 'lid 2' belongs to)."""
    header_bits = [chunk.document]
    if chunk.version:
        header_bits.append(f"versie {chunk.version}")
    if chunk.section:
        header_bits.append(chunk.section)
    header = " | ".join(header_bits)
    return f"{header}\n{chunk.text}"


def embed_cao_chunks(client: Mistral, model: str, chunks: list[CaoChunk]) -> np.ndarray:
    texts = [build_embedding_text(chunk) for chunk in chunks]
    return embed_texts(client, model, texts)
