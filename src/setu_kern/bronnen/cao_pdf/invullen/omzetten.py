"""Omzetten tussen het formuliermodel en de JSON van het LLM (volgens ``schema.blok_schema``).

- ``van_waarden``: LLM-JSON → invoer voor ``Model.model_validate`` (keuzes terug naar enum-leden, lege delen weg);
- ``naar_waarden``: een ingevuld model → LLM-JSON (voor de nep-LLM en de rondgang-test);
- ``bladeren`` / ``verwijder``: de ingevulde bladwaarden als paden (``bedrag.percentage.percentage``,
  ``beloningen[0].salarisschalen[1].naam``), om de onderbouwing per waarde te controleren.
"""

import copy
import re
from typing import Any

from pydantic import BaseModel

from .typen import Beperking, Soort, Veld, enum_lid, enum_waarde, velden_van


# --- LLM → model
def van_waarden(model: type[BaseModel], data: dict[str, Any] | None, velden: Any = None, beperking: Beperking | None = None) -> dict[str, Any]:
    uit: dict[str, Any] = {}
    for v in velden_van(model, velden, beperking):
        waarde = _van(v.soort, v, (data or {}).get(v.naam))
        if not _leeg(waarde):
            uit[v.naam] = waarde
    return uit


def _van(soort: Soort, v: Veld, waarde: Any) -> Any:
    if waarde is None:
        return None
    if soort.vorm == "lijst":
        items = [_van(soort.element, v, w) for w in waarde or []]
        return [w for w in items if not _leeg(w)]
    if soort.vorm == "mapping":
        return {
            enum_lid(soort.sleutel, k): w
            for k, w in ((k, _van(soort.element, v, w)) for k, w in (waarde or {}).items())
            if not _leeg(w)
        }
    if soort.vorm == "model":
        return van_waarden(soort.doel, waarde, None, v.beperking) if isinstance(waarde, dict) else waarde
    if soort.vorm == "enum":
        return enum_lid(soort.doel, waarde)
    return waarde  # getallen, tekst, datum/tijd als tekst: Pydantic zet ze om en controleert ze


def _leeg(waarde: Any) -> bool:
    return waarde is None or waarde == "" or waarde == [] or waarde == {}


# --- model → LLM
def naar_waarden(instantie: BaseModel | None, model: type[BaseModel], velden: Any = None, beperking: Beperking | None = None) -> dict[str, Any]:
    return {v.naam: _naar(v.soort, v, getattr(instantie, v.naam, None)) for v in velden_van(model, velden, beperking)}


def _naar(soort: Soort, v: Veld, waarde: Any) -> Any:
    if soort.vorm == "lijst":
        return [_naar(soort.element, v, w) for w in waarde or []]
    if soort.vorm == "mapping":
        waarde = waarde or {}
        return {enum_waarde(k): _naar(soort.element, v, waarde.get(k)) for k in soort.sleutel}
    if waarde is None:
        return None
    if soort.vorm == "model":
        return naar_waarden(waarde, soort.doel, None, v.beperking)
    if soort.vorm == "enum":
        return enum_waarde(waarde)
    if soort.vorm == "tijd":
        return waarde.strftime("%H:%M")
    if soort.vorm == "datum":
        return waarde.isoformat()
    if soort.vorm == "bool":
        return True if waarde else None
    return waarde


# --- paden
def bladeren(data: Any, pad: str = "") -> list[tuple[str, Any]]:
    """Alle ingevulde bladwaarden met hun pad."""
    if isinstance(data, dict):
        return [b for k, w in data.items() for b in bladeren(w, f"{pad}.{k}" if pad else str(k))]
    if isinstance(data, list):
        return [b for i, w in enumerate(data) for b in bladeren(w, f"{pad}[{i}]")]
    return [] if data is None else [(pad, data)]


_DEEL = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def verwijder(data: dict[str, Any], pad: str) -> dict[str, Any]:
    """Een kopie van ``data`` waarin de waarde op ``pad`` leeg (``null``) is."""
    uit = copy.deepcopy(data)
    delen = [int(i) if i else k for k, i in _DEEL.findall(pad)]
    cur: Any = uit
    for deel in delen[:-1]:
        try:
            cur = cur[deel]
        except (KeyError, IndexError, TypeError):
            return uit
    if isinstance(cur, dict) and delen[-1] in cur:
        cur[delen[-1]] = None
    elif isinstance(cur, list) and isinstance(delen[-1], int) and delen[-1] < len(cur):
        cur[delen[-1]] = None
    return uit


def valt_onder(blad: str, pad: str) -> bool:
    """Hoort ``blad`` bij ``pad`` (hetzelfde veld of een onderdeel ervan)?"""
    pad = pad.strip()
    return bool(pad) and (blad == pad or blad.startswith(pad + ".") or blad.startswith(pad + "["))


__all__ = ["bladeren", "naar_waarden", "valt_onder", "van_waarden", "verwijder"]
