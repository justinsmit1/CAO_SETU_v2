"""Document extraction via marker-pdf (local, open-source, no API key needed)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from setu_kern.bronnen.cao_pdf.pijplijn.config import load_hf_token

PAGE_BREAK_RE = re.compile(r"\{(\d+)\}-{10,}")


@dataclass(frozen=True)
class Page:
    """One extracted page of a source document."""

    document: str
    page_number: int  # 1-based, for citations
    markdown: str


def build_converter() -> PdfConverter:
    """Loads the marker models once; reuse across multiple PDFs."""
    hf_token = load_hf_token()
    if hf_token:
        os.environ.setdefault("HF_TOKEN", hf_token)

    return PdfConverter(
        artifact_dict=create_model_dict(),
        config={"paginate_output": True},
    )


def extract_pdf(converter: PdfConverter, pdf_path: Path) -> list[Page]:
    """Run marker-pdf on a local PDF, returning its pages as markdown."""
    pdf_path = Path(pdf_path)
    rendered = converter(str(pdf_path))
    markdown, _, _ = text_from_rendered(rendered)

    splits = PAGE_BREAK_RE.split(markdown)
    # splits = ['', '0', '<page 0 text>', '1', '<page 1 text>', ...]
    pages = []
    for page_id_str, text in zip(splits[1::2], splits[2::2]):
        text = text.strip()
        if text:
            pages.append(
                Page(document=pdf_path.name, page_number=int(page_id_str) + 1, markdown=text)
            )
    return pages
