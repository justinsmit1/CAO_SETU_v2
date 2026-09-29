"""Retrieval-augmented question answering with structured, cited JSON output."""

from __future__ import annotations

import json
from dataclasses import dataclass

from mistralai.client import Mistral

from cao_setu_v2.llm_pipeline.chunking import Chunk

TOP_K = 5

ANSWER_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
            "description": "The answer to the question, in the same language as the question.",
        },
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "document": {"type": "string"},
                    "page": {"type": "integer"},
                    "section": {"type": ["string", "null"]},
                    "quote": {
                        "type": "string",
                        "description": "The exact snippet from the source that supports the answer.",
                    },
                },
                "required": ["document", "page", "section", "quote"],
                "additionalProperties": False,
            },
        },
        "insufficient_information": {
            "type": "boolean",
            "description": "True if the retrieved context does not contain the answer.",
        },
    },
    "required": ["answer", "citations", "insufficient_information"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """\
You answer questions about Dutch collective labour agreements (CAO's) using ONLY the \
provided excerpts. Every claim in your answer must be backed by at least one citation \
pointing at the document, page number, and an exact quote from the excerpts. If the \
excerpts do not contain the answer, set insufficient_information to true and explain \
what is missing in the answer field instead of guessing."""


@dataclass(frozen=True)
class Answer:
    answer: str
    citations: list[dict]
    insufficient_information: bool
    sources: list[tuple[Chunk, float]]


def _format_context(sources: list[tuple[Chunk, float]]) -> str:
    parts = []
    for chunk, score in sources:
        header = f"[{chunk.document}, page {chunk.page_number}"
        if chunk.section:
            header += f", section: {chunk.section}"
        header += f", relevance: {score:.2f}]"
        parts.append(f"{header}\n{chunk.text}")
    return "\n\n---\n\n".join(parts)


def answer_question(
    client: Mistral,
    model: str,
    question: str,
    sources: list[tuple[Chunk, float]],
) -> Answer:
    context = _format_context(sources)
    user_prompt = f"Excerpts:\n\n{context}\n\nQuestion: {question}"

    resp = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "cao_answer",
                "schema": ANSWER_JSON_SCHEMA,
                "strict": True,
            },
        },
    )
    payload = json.loads(resp.choices[0].message.content)

    return Answer(
        answer=payload["answer"],
        citations=payload["citations"],
        insufficient_information=payload["insufficient_information"],
        sources=sources,
    )
