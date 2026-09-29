"""CLI: ingest CAO PDFs into a FAISS index, then ask questions against them."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mistralai.client import Mistral

from setu_kern.bronnen.cao_pdf.pijplijn.cao_index import embed_cao_chunks, parse_cao_structure
from setu_kern.bronnen.cao_pdf.pijplijn.config import load_config
from setu_kern.bronnen.cao_pdf.pijplijn.embeddings import embed_texts
from setu_kern.bronnen.cao_pdf.pijplijn.extraction import build_converter, extract_pdf
from setu_kern.bronnen.cao_pdf.pijplijn.qa import TOP_K, answer_question
from setu_kern.bronnen.cao_pdf.pijplijn.store import VectorStore, index_exists

DEFAULT_INDEX_DIR = Path("index")


def cmd_ingest(args: argparse.Namespace) -> None:
    config = load_config()
    client = Mistral(api_key=config.api_key)
    index_dir = Path(args.index_dir)

    print("Loading marker-pdf models...", file=sys.stderr)
    converter = build_converter()

    all_cao_chunks = []
    for pdf_arg in args.pdfs:
        pdf_path = Path(pdf_arg)
        print(f"Extracting {pdf_path.name}...", file=sys.stderr)
        pages = extract_pdf(converter, pdf_path)
        cao_chunks = parse_cao_structure(
            pages,
            version=args.version,
            effective_from=args.effective_from,
            effective_to=args.effective_to,
        )
        print(f"  -> {len(pages)} pages, {len(cao_chunks)} chunks", file=sys.stderr)
        all_cao_chunks.extend(cao_chunks)

    if not all_cao_chunks:
        raise SystemExit("No text extracted from the given PDF(s).")

    print(f"Embedding {len(all_cao_chunks)} chunks...", file=sys.stderr)
    vectors = embed_cao_chunks(client, config.embed_model, all_cao_chunks)
    all_chunks = [c.as_generic_chunk() for c in all_cao_chunks]

    store = VectorStore(dim=vectors.shape[1])
    if index_exists(index_dir):
        store = VectorStore.load(index_dir)
    store.add(all_chunks, vectors)
    store.save(index_dir)
    print(f"Saved index to {index_dir}/ ({len(store.chunks)} chunks total)", file=sys.stderr)


def cmd_ask(args: argparse.Namespace) -> None:
    config = load_config()
    client = Mistral(api_key=config.api_key)
    index_dir = Path(args.index_dir)
    if not index_exists(index_dir):
        raise SystemExit(f"No index found at {index_dir}/. Run `ingest` first.")

    store = VectorStore.load(index_dir)
    query_vector = embed_texts(client, config.embed_model, [args.question])[0]
    sources = store.search(query_vector, top_k=args.top_k)

    result = answer_question(client, config.model, args.question, sources)
    print(
        json.dumps(
            {
                "answer": result.answer,
                "citations": result.citations,
                "insufficient_information": result.insufficient_information,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="CAO retrieval-augmented Q&A")
    subparsers = parser.add_subparsers(required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Extract and index one or more CAO PDFs")
    ingest_parser.add_argument("pdfs", nargs="+", help="Path(s) to CAO PDF file(s)")
    ingest_parser.add_argument("--index-dir", default=str(DEFAULT_INDEX_DIR))
    ingest_parser.add_argument(
        "--version",
        help="CAO version/looptijd label for these PDFs, e.g. '2026' or '2025-2026'. "
        "Re-ingesting the same CAO under a different --version adds new dated chunks "
        "instead of overwriting the previous version's articles.",
    )
    ingest_parser.add_argument(
        "--effective-from", help="Date (YYYY-MM-DD) this version becomes effective."
    )
    ingest_parser.add_argument(
        "--effective-to", help="Date (YYYY-MM-DD) this version stops being effective."
    )
    ingest_parser.set_defaults(func=cmd_ingest)

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the indexed CAO's")
    ask_parser.add_argument("question")
    ask_parser.add_argument("--index-dir", default=str(DEFAULT_INDEX_DIR))
    ask_parser.add_argument("--top-k", type=int, default=TOP_K)
    ask_parser.set_defaults(func=cmd_ask)

    args = parser.parse_args()
    args.func(args)



if __name__ == "__main__":
    main()
