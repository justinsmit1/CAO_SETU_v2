"""Nep-onderdelen om het invullen te testen zonder API: ``NepLLM`` (vaste antwoorden) en ``LijstZoeker``.

    llm = NepLLM({"05 Vakantiebijslag": antwoord})           # één antwoord per blok
    llm = NepLLM({"05 Vakantiebijslag": [fout, goed]})       # opeenvolgende antwoorden (herkansing)
    llm = NepLLM({"05 Vakantiebijslag": lambda berichten, schema: {...}})
    llm.aanroepen  # [(blok_naam_schema, berichten, schema), ...] om te controleren wat het LLM te zien kreeg
"""

import copy
from collections.abc import Callable
from typing import Any

from .invullen.blokken import BLOKKEN, Blok
from .zoeken import Fragment

Antwoord = dict[str, Any] | list[dict[str, Any]] | Callable[[list[dict[str, str]], dict[str, Any]], dict[str, Any]]


class NepLLM:
    def __init__(self, antwoorden: dict[str, Antwoord], blokken: tuple[Blok, ...] = BLOKKEN):
        # Sleutels mogen de bloknaam ("05 Vakantiebijslag") of de schemanaam zijn.
        namen = {b.naam: b.schema_naam for b in blokken}
        self.antwoorden = {namen.get(k, k): copy.deepcopy(v) if not callable(v) else v for k, v in antwoorden.items()}
        self.aanroepen: list[tuple[str, list[dict[str, str]], dict[str, Any]]] = []

    def vraag_json(self, berichten: list[dict[str, str]], schema: dict[str, Any], naam: str) -> dict[str, Any]:
        self.aanroepen.append((naam, copy.deepcopy(berichten), schema))
        if naam not in self.antwoorden:
            return leeg_antwoord(schema)
        antwoord = self.antwoorden[naam]
        if callable(antwoord):
            return antwoord(berichten, schema)
        if isinstance(antwoord, list):
            return copy.deepcopy(antwoord.pop(0) if len(antwoord) > 1 else antwoord[0])
        return copy.deepcopy(antwoord)


def leeg_antwoord(schema: dict[str, Any]) -> dict[str, Any]:
    """Een geldig antwoord zonder ingevulde waarden (alles ``null``/leeg)."""
    waarden = {k: ([] if s.get("type") == "array" else _leeg_object(s)) for k, s in schema["properties"]["waarden"]["properties"].items()}
    return {"waarden": waarden, "onderbouwing": [], "niet_gevonden": list(waarden)}


def _leeg_object(s: dict[str, Any]) -> Any:
    if s.get("type") == "object":  # mapping: alle sleutels aanwezig, elk leeg
        return {k: ([] if w.get("type") == "array" else None) for k, w in s["properties"].items()}
    return None


class LijstZoeker:
    """Zoekt in een vaste lijst fragmenten: score = aantal woorden uit de vraag dat in het fragment voorkomt."""

    def __init__(self, fragmenten: list[Fragment]):
        self.fragmenten = fragmenten

    def zoek(self, vraag: str, top_k: int) -> list[Fragment]:
        woorden = {w for w in vraag.lower().split() if len(w) > 3}
        gescoord = []
        for f in self.fragmenten:
            score = sum(w in f.tekst.lower() for w in woorden)
            if score:
                gescoord.append(Fragment(f.document, f.pagina, f.sectie, f.tekst, float(score)))
        return sorted(gescoord, key=lambda f: f.score, reverse=True)[:top_k]
