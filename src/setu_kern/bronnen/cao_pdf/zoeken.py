"""Zoeken in de cao: welke fragmenten krijgt het LLM per blok te zien.

Het invullen kent alleen het ``Zoeker``-protocol, niet FAISS of Mistral. ``IndexZoeker`` zoekt in een index die met
de pijplijn is gemaakt (``python -m setu_kern.bronnen.cao_pdf.pijplijn.cli ingest cao.pdf``); in tests volstaat een
eenvoudige zoeker (``nep.LijstZoeker``).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .invullen.blokken import Blok


@dataclass(frozen=True)
class Fragment:
    """Een stuk cao-tekst met de plek waar het staat."""

    document: str
    pagina: int
    sectie: str | None  # bijv. "Hoofdstuk 3 > Artikel 12 lid 1 - Vakantiebijslag"
    tekst: str
    score: float = 0.0


class Zoeker(Protocol):
    def zoek(self, vraag: str, top_k: int) -> list[Fragment]: ...


def zoek_voor_blok(zoeker: Zoeker, blok: Blok, vraagteksten: list[str], top_k: int = 8) -> list[Fragment]:
    """Zoekt met de zoektermen van het blok en met de vraagteksten; dubbele fragmenten tellen één keer (hoogste
    score). Geeft de beste ``top_k`` terug, in volgorde van score."""
    vragen = [*blok.zoektermen, " ".join(vraagteksten[:5])]
    beste: dict[tuple[str, int, str], Fragment] = {}
    for vraag in (v for v in vragen if v.strip()):
        for f in zoeker.zoek(vraag, top_k):
            sleutel = (f.document, f.pagina, f.tekst)
            if sleutel not in beste or f.score > beste[sleutel].score:
                beste[sleutel] = f
    return sorted(beste.values(), key=lambda f: f.score, reverse=True)[:top_k]


class IndexZoeker:
    """Zoekt in een FAISS-index van de pijplijn, met Mistral-embeddings (het embed-model uit config.toml)."""

    def __init__(self, store: Any, client: Any, embed_model: str):
        self.store, self.client, self.embed_model = store, client, embed_model

    @classmethod
    def laad(cls, index_map: str | Path) -> "IndexZoeker":
        from mistralai.client import Mistral

        from .pijplijn.config import load_config
        from .pijplijn.store import VectorStore, index_exists

        if not index_exists(Path(index_map)):
            raise FileNotFoundError(
                f"Geen index in {index_map}. Maak die eerst: "
                f"python -m setu_kern.bronnen.cao_pdf.pijplijn.cli ingest cao.pdf --index-dir {index_map}"
            )
        config = load_config()
        return cls(VectorStore.load(Path(index_map)), Mistral(api_key=config.api_key), config.embed_model)

    def zoek(self, vraag: str, top_k: int) -> list[Fragment]:
        from .pijplijn.embeddings import embed_texts

        vector = embed_texts(self.client, self.embed_model, [vraag])[0]
        return [
            Fragment(c.document, c.page_number, c.section, c.text, score)
            for c, score in self.store.search(vector, top_k=top_k)
        ]
