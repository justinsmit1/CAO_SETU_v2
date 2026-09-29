"""Formulier → de antwoorden van de wijzerbelonen-webform (``__webform_data__.answers``).

De webform bewaart elk antwoord onder de slug van de vraag. Een slug is een tekst (``"vakantiebijslag/ja-nee"``)
of, bij herhaalbare blokken, een pad (``["beloningen", 0, "salarisschalen", 1, "naam"]``). De antwoorden vormen
één geneste structuur: ``{"vakantiebijslag/ja-nee": "ja", "beloningen": [{"naam": ..., "salarisschalen": [...]}]}``.

Elk veld van het formuliermodel kent zijn slug (``veld(slug, ...)``). Die slugs zijn sjablonen:
- ``[i]``, ``[j]``, ``[k]``, ``[r]``: de rij-index in een herhaalbaar blok;
- ``<p>``, ``<r>``, ``<toeslag>``, ...: het pad van het bovenliggende veld;
- bij een veld per sleutel (``mapping=True``) staat de laatste ``<...>`` voor de sleutel;
- ``…``: het veld zelf heeft geen eigen slugdeel (de Bedragregel van een toeslagvariatie staat direct in de rij).

Waarden krijgen het formaat dat de webform zelf opslaat: tekst en getallen als tekst (``"8.5"``), datums als
milliseconden sinds 1970 (lokale middernacht), tijden als ``"HH:MM"``, aangevinkte checkboxes als ``true``.
"""

import datetime as dt
import re
import time
from enum import Enum
from typing import Any

from pydantic import BaseModel

from ..formulier import Formulier
from ..formulier.formulier import WEBFORM_APP_VERSION

LOCAL_STORAGE_DATA_VERSION = 4

# De beginwaarden van een nieuw formulier (Store-constructor en ensureAnswerIsArray in de definities).
# De webform verwacht deze lijsten; zonder bijv. "overige-regelingen" loopt de import vast.
STANDAARD_ANTWOORDEN: dict[str, Any] = {
    "functie-groepen": [],
    "overige-regelingen": [],
    "beloningen": [{"naam": "Standaard salaristabel", "salarisschalen": [{"stappen": [{}]}]}],
    "loondoorbetaling-bij-ziekte": [{}],
    "reiskostenvergoeding-eigen-vervoer": [{}],
    "reiskostenvergoeding-zakelijke-kilometers": [{}],
    "contactpersonen": [{}],
}

Pad = list[str | int]
_PLAATSHOUDER = re.compile(r"<[^<>]+>")
_INDEX = re.compile(r"\[[a-z]\]")


def naar_antwoorden(formulier: Formulier, met_standaard: bool = True) -> dict[str, Any]:
    """De antwoorden zoals de webform ze opslaat. ``met_standaard``: vul ontbrekende standaardlijsten aan."""
    antwoorden: dict[str, Any] = {}
    _model(formulier, [], None, antwoorden)
    if met_standaard:
        for sleutel, waarde in STANDAARD_ANTWOORDEN.items():
            if sleutel not in antwoorden:
                antwoorden[sleutel] = _kopie(waarde)
    return antwoorden


def webform_data(formulier: Formulier, moment: dt.datetime | None = None) -> dict[str, Any]:
    """Het ``__webform_data__``-blok van een export (``toLocalStorage()`` + versie), zoals de import het leest."""
    moment = moment or dt.datetime.now()
    return {
        "appVersion": WEBFORM_APP_VERSION,
        "note": f"Generated with Wijzerbelonen UGB webformulier v{WEBFORM_APP_VERSION}. Powered by SETU",
        "localStorageDataVersion": LOCAL_STORAGE_DATA_VERSION,
        "date": int(moment.timestamp() * 1000),
        "activeSectionIndex": 0,
        "activeSubSectionIndex": 0,
        "answers": naar_antwoorden(formulier),
    }


# --- waarden
def antwoord_waarde(waarde: Any) -> Any:
    """Een Python-waarde in het formaat van de webform."""
    if isinstance(waarde, Enum):
        return waarde.value
    if isinstance(waarde, bool):
        return True if waarde else None  # een uitgevinkte checkbox wordt verwijderd (answer = null)
    if isinstance(waarde, int):
        return str(waarde)
    if isinstance(waarde, float):
        return str(int(waarde)) if waarde.is_integer() else repr(waarde)
    if isinstance(waarde, dt.datetime):
        return int(waarde.timestamp() * 1000)
    if isinstance(waarde, dt.date):
        return datum_naar_ms(waarde)
    if isinstance(waarde, dt.time):
        return waarde.strftime("%H:%M")
    return waarde


def datum_naar_ms(datum: dt.date) -> int:
    """Lokale middernacht in milliseconden, zoals de datumkiezer van de webform (``date.getTime()``)."""
    return int(time.mktime((datum.year, datum.month, datum.day, 0, 0, 0, 0, 0, -1)) * 1000)


# --- de structuur doorlopen
def _model(model: BaseModel, pad: Pad, sjabloon: str | None, uit: dict) -> None:
    for naam, info in type(model).model_fields.items():
        waarde = getattr(model, naam)
        if waarde is None or waarde == [] or waarde == {}:
            continue
        extra = info.json_schema_extra if isinstance(info.json_schema_extra, dict) else {}
        veld_sjabloon = extra.get("slug")
        if veld_sjabloon is None:
            # Submodel zonder eigen slug (bijv. een subsectie): zelfde pad en sjabloon als de ouder.
            if isinstance(waarde, BaseModel):
                _model(waarde, pad, sjabloon, uit)
                continue
            raise ValueError(f"{type(model).__name__}.{naam} heeft geen slug")
        _veld(waarde, veld_sjabloon, pad, sjabloon, uit, f"{type(model).__name__}.{naam}", extra.get("lijst", False))


def _veld(waarde: Any, veld_sjabloon: str, pad: Pad, ouder_sjabloon: str | None, uit: dict, naam: str, lijst: bool) -> None:
    if isinstance(waarde, dict):
        for sleutel, item in waarde.items():
            item_pad = sleutel_pad(veld_sjabloon, pad, ouder_sjabloon, antwoord_waarde(sleutel))
            if isinstance(item, BaseModel):
                _model(item, item_pad, veld_sjabloon, uit)
            else:
                _zet(uit, item_pad, antwoord_waarde(item), naam)
        return
    veld_pad = veld_pad_van(veld_sjabloon, pad, ouder_sjabloon, lijst=isinstance(waarde, list))
    if isinstance(waarde, list):
        if not veld_pad or not isinstance(veld_pad[-1], str):
            raise ValueError(f"{naam}: lijst zonder naam ({veld_sjabloon!r})")
        _zorg_lijst(uit, veld_pad)
        for index, item in enumerate(waarde):
            rij_pad = [*veld_pad, index]
            _zorg_rij(uit, rij_pad)
            if isinstance(item, BaseModel):
                _model(item, rij_pad, veld_sjabloon, uit)
            else:
                _zet(uit, rij_pad, antwoord_waarde(item), naam)
        return
    if isinstance(waarde, BaseModel):
        _model(waarde, veld_pad, veld_sjabloon, uit)
        return
    _zet(uit, veld_pad, antwoord_waarde(waarde), naam)


def veld_pad_van(veld_sjabloon: str, ouder_pad: Pad, ouder_sjabloon: str | None, lijst: bool = False) -> Pad:
    achtervoegsel = _relatief(veld_sjabloon, ouder_sjabloon, is_rij=bool(ouder_pad) and isinstance(ouder_pad[-1], int))
    if lijst:
        achtervoegsel = re.sub(r"\[[a-z]\]$", "", achtervoegsel)
    return _plak(ouder_pad, achtervoegsel)


def sleutel_pad(veld_sjabloon: str, ouder_pad: Pad, ouder_sjabloon: str | None, sleutel: str) -> Pad:
    """Pad van één sleutel bij een veld per sleutel: de laatste ``<...>`` in het sjabloon is de sleutel."""
    treffers = list(_PLAATSHOUDER.finditer(veld_sjabloon))
    if not treffers:
        raise ValueError(f"veld per sleutel zonder <...> in {veld_sjabloon!r}")
    laatste = treffers[-1]
    voor, na = veld_sjabloon[: laatste.start()], veld_sjabloon[laatste.end() :]
    is_rij = bool(ouder_pad) and isinstance(ouder_pad[-1], int)
    basis = _plak(ouder_pad, _relatief(voor, ouder_sjabloon, is_rij)) if voor else list(ouder_pad)
    return _plak_tekst(basis, f"{sleutel}{na}")


def _relatief(sjabloon: str, ouder_sjabloon: str | None, is_rij: bool) -> str:
    """Het deel van het sjabloon dat na het pad van de ouder komt."""
    sjabloon = sjabloon.replace("…", "").rstrip("/") if sjabloon.endswith("…") else sjabloon.replace("…", "")
    ouder = ouder_sjabloon.replace("…", "").rstrip("/") if ouder_sjabloon is not None else None
    # 1. Het sjabloon herhaalt dat van de ouder (bijv. "<p>/percentage/basis" onder "<p>/percentage").
    if ouder and sjabloon.startswith(ouder):
        return sjabloon[len(ouder) :]
    # 2. Het sjabloon begint met een plaatshouder voor het pad van de ouder (bijv. "<p>/amount-type").
    treffer = _PLAATSHOUDER.search(sjabloon)
    if treffer:
        rest = sjabloon[treffer.end() :]
        if is_rij:
            rest = re.sub(r"^(\[[a-z]\])+", "", rest)
        return rest
    # 3. Een veld op het hoogste niveau van een sectie.
    if ouder is None:
        return sjabloon
    raise ValueError(f"slug {sjabloon!r} begint niet met die van de ouder ({ouder_sjabloon!r})")


def _plak(pad: Pad, achtervoegsel: str) -> Pad:
    """Plakt een slugdeel aan een pad: na een tekst wordt het aan die tekst vastgeplakt (de webform gebruikt
    ``"a/b"`` als één sleutel), na een index of aan het begin wordt het een nieuwe sleutel."""
    uit = list(pad)
    if not achtervoegsel:
        return uit
    if _INDEX.search(achtervoegsel):
        raise ValueError(f"onverwachte rij-index in slugdeel {achtervoegsel!r} (pad {pad})")
    return _plak_tekst(uit, achtervoegsel)


def _plak_tekst(pad: Pad, tekst: str) -> Pad:
    uit = list(pad)
    if uit and isinstance(uit[-1], str):
        uit[-1] = uit[-1] + tekst
    else:
        # Eén scheidingsteken weghalen; een tweede slash hoort bij de sleutel (bijv. "/voorwaarden" in 06).
        uit.append(tekst[1:] if tekst.startswith("/") else tekst)
    return uit


# --- schrijven in de geneste structuur (Store.setAnswer)
def _zet(uit: dict, pad: Pad, waarde: Any, naam: str) -> None:
    if waarde is None or waarde == "":
        return
    cur = _ga_naar(uit, pad[:-1], naam)
    if not isinstance(cur, dict) or not isinstance(pad[-1], str):
        raise ValueError(f"{naam}: ongeldig antwoordpad {pad}")
    cur[pad[-1]] = waarde


def _ga_naar(uit: dict, pad: Pad, naam: str) -> Any:
    cur: Any = uit
    for i in range(0, len(pad), 2):
        sleutel = pad[i]
        index = pad[i + 1] if i + 1 < len(pad) else None
        if not isinstance(sleutel, str) or (index is not None and not isinstance(index, int)):
            raise ValueError(f"{naam}: ongeldig antwoordpad {pad} (verwacht tekst, index, tekst, ...)")
        lijst = cur.setdefault(sleutel, [])
        if index is None:
            return lijst
        while len(lijst) <= index:
            lijst.append({})
        cur = lijst[index]
    return cur


def _zorg_lijst(uit: dict, pad: Pad) -> None:
    _ga_naar(uit, pad, "lijst")


def _zorg_rij(uit: dict, pad: Pad) -> None:
    _ga_naar(uit, pad, "rij")


def _kopie(waarde: Any) -> Any:
    import copy

    return copy.deepcopy(waarde)
