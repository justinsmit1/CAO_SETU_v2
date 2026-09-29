"""Controles tegen de echte webform (zie webform.py)."""

from typing import Any

from .webform import Webform


def bladeren(antwoorden: dict, pad: list | None = None) -> list[tuple[list, Any]]:
    """Alle ingevulde antwoorden als (slug-pad, waarde). Lijsten van objecten zijn herhaalbare blokken."""
    pad = pad or []
    uit = []
    for sleutel, waarde in antwoorden.items():
        if isinstance(waarde, list) and all(isinstance(r, dict) for r in waarde):
            for i, rij in enumerate(waarde):
                uit += bladeren(rij, [*pad, sleutel, i])
        else:
            uit.append(([*pad, sleutel], waarde))
    return uit


def antwoord_problemen(wf: Webform, antwoorden: dict) -> list[str]:
    """Elk antwoord moet bij een bestaande vraag horen, zichtbaar zijn en een geldige waarde hebben."""
    vragen = {tuple(v["slug"]): v for v in wf.vragen(antwoorden)}
    problemen = []
    for pad, waarde in bladeren(antwoorden):
        vraag = vragen.get(tuple(pad))
        if vraag is None:
            problemen.append(f"{pad}: geen vraag met deze slug in de webform")
            continue
        if not vraag["shown"]:
            problemen.append(f"{pad}: vraag is verborgen in de webform")
        soort = vraag["type"]
        if soort == "radio" and waarde not in (vraag["options"] or []):
            problemen.append(f"{pad}: {waarde!r} is geen optie ({vraag['options']})")
        elif soort == "checkbox" and waarde is not True:
            problemen.append(f"{pad}: checkbox moet true zijn, is {waarde!r}")
        elif soort == "date" and not isinstance(waarde, int):
            problemen.append(f"{pad}: datum moet milliseconden zijn, is {waarde!r}")
        elif soort in ("text", "time") and not isinstance(waarde, str):
            problemen.append(f"{pad}: {soort} moet tekst zijn, is {waarde!r}")
    return problemen


def setu_verschillen(verwacht: Any, gekregen: Any, pad: str = "") -> list[str]:
    """Verschillen tussen twee SETU-JSON-structuren (volgorde van sleutels telt niet, van lijsten wel)."""
    if isinstance(verwacht, dict) and isinstance(gekregen, dict):
        uit = []
        for k in verwacht.keys() | gekregen.keys():
            if k not in gekregen:
                uit.append(f"{pad}.{k}: ontbreekt (verwacht {verwacht[k]!r})")
            elif k not in verwacht:
                uit.append(f"{pad}.{k}: extra ({gekregen[k]!r})")
            else:
                uit += setu_verschillen(verwacht[k], gekregen[k], f"{pad}.{k}")
        return uit
    if isinstance(verwacht, list) and isinstance(gekregen, list):
        uit = [] if len(verwacht) == len(gekregen) else [f"{pad}: lengte {len(gekregen)}, verwacht {len(verwacht)}"]
        for i, (a, b) in enumerate(zip(verwacht, gekregen)):
            uit += setu_verschillen(a, b, f"{pad}[{i}]")
        return uit
    getallen = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (verwacht, gekregen))
    gelijk = verwacht == gekregen if getallen else (verwacht == gekregen and type(verwacht) is type(gekregen))
    return [] if gelijk else [f"{pad}: {gekregen!r}, verwacht {verwacht!r}"]


def vergelijk_setu(wf: Webform, antwoorden: dict, onze: dict) -> list[str]:
    """Vergelijkt onze SETU-JSON met die van de webform; ``issued`` en een willekeurig documentId tellen niet mee."""
    referentie = wf.setu(antwoorden)
    onze = {k: v for k, v in onze.items() if k != "issued"}
    if not antwoorden.get("id"):
        referentie.get("documentId", {}).pop("value", None)
        onze = {**onze, "documentId": {k: v for k, v in onze.get("documentId", {}).items() if k != "value"}}
    return setu_verschillen(referentie, onze)
