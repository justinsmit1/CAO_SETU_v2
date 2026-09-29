"""Mistral embeddings, batched."""

from __future__ import annotations

import numpy as np
from mistralai.client import Mistral

BATCH_SIZE = 32


def embed_texts(client: Mistral, model: str, texts: list[str]) -> np.ndarray:
    if not texts:
        return np.empty((0, 0), dtype="float32")

    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        resp = client.embeddings.create(model=model, inputs=batch)
        vectors.extend(d.embedding for d in resp.data)

    return np.array(vectors, dtype="float32")
