"""A small FAISS-backed vector store for CAO chunks, persisted to disk."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np

from cao_setu_v2.llm_pipeline.chunking import Chunk

INDEX_FILE = "index.faiss"
METADATA_FILE = "metadata.jsonl"


def index_exists(directory: Path) -> bool:
    """True only if a complete, loadable index is on disk (not just the directory)."""
    directory = Path(directory)
    return (directory / INDEX_FILE).exists() and (directory / METADATA_FILE).exists()


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


class VectorStore:
    """Cosine-similarity search over chunk embeddings (FAISS IndexFlatIP)."""

    def __init__(self, dim: int):
        self.index = faiss.IndexFlatIP(dim)
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        self.index.add(_normalize(vectors))
        self.chunks.extend(chunks)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if self.index.ntotal == 0:
            return []
        query = _normalize(query_vector.reshape(1, -1))
        scores, indices = self.index.search(query, min(top_k, self.index.ntotal))
        return [
            (self.chunks[idx], float(score))
            for idx, score in zip(indices[0], scores[0])
            if idx != -1
        ]

    def save(self, directory: Path) -> None:
        """Writes to temp files and swaps them in, so a crash mid-save can't
        leave a directory with an incomplete/missing index.faiss."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        index_tmp = directory / f"{INDEX_FILE}.tmp"
        metadata_tmp = directory / f"{METADATA_FILE}.tmp"

        faiss.write_index(self.index, str(index_tmp))
        with metadata_tmp.open("w", encoding="utf-8") as f:
            for chunk in self.chunks:
                f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")

        os.replace(index_tmp, directory / INDEX_FILE)
        os.replace(metadata_tmp, directory / METADATA_FILE)

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        directory = Path(directory)
        index = faiss.read_index(str(directory / INDEX_FILE))
        store = cls.__new__(cls)
        store.index = index
        store.chunks = []
        with (directory / METADATA_FILE).open("r", encoding="utf-8") as f:
            for line in f:
                store.chunks.append(Chunk(**json.loads(line)))
        return store
