"""Vragen van het formuliermodel opvragen: type, opties, voorwaarden — rechtstreeks uit de code.

Voorbeeld::

    from setu_kern.bronnen.wijzerbelonen.formulier import Formulier, vragen
    for v in vragen(Formulier):
        print(v.pad, v.vraagtype, v.opties)
"""

import datetime as dt
from dataclasses import dataclass, field, replace
from enum import Enum
from types import NoneType
from typing import get_args, get_origin

from pydantic import BaseModel

from ._basis import Keuze, Vraagtype


@dataclass(frozen=True)
class Vraag:
    pad: str  # Python-pad, bijv. "vakantiebijslag.bedrag.percentage.basis"; "[]" = herhaalbaar, "{}" = per sleutel
    slug: str
    vraag: str
    vraagtype: Vraagtype
    opties: list[tuple[str, str]] = field(default_factory=list)  # (waarde, label), al gefilterd op toegestane opties
    eenheid: str | None = None
    toon_als: str | None = None
    optioneel: bool = False
    herhaalbaar: bool = False


def _kern(annotatie: object) -> tuple[object, str]:
    """Haalt ``X`` uit ``X | None``, ``list[X]`` en ``dict[K, X]``; geeft ook het pad-achtervoegsel terug."""
    achtervoegsel = ""
    while True:
        oorsprong, args = get_origin(annotatie), get_args(annotatie)
        if oorsprong is list:
            annotatie, achtervoegsel = args[0], achtervoegsel + "[]"
        elif oorsprong is dict:
            annotatie, achtervoegsel = args[1], achtervoegsel + "{}"
        elif args and NoneType in args:
            annotatie = next(a for a in args if a is not NoneType)
        else:
            return annotatie, achtervoegsel


def _afgeleid_type(t: object) -> Vraagtype:
    if isinstance(t, type):
        if issubclass(t, Enum):
            return Vraagtype.RADIO
        if t is bool:
            return Vraagtype.CHECKBOX
        if t is dt.date:
            return Vraagtype.DATUM
        if t is dt.time:
            return Vraagtype.TIJD
        if t in (int, float):
            return Vraagtype.GETAL
    return Vraagtype.TEKST


def vragen(model: type[BaseModel], pad: str = "", herhaalbaar: bool = False) -> list[Vraag]:
    """Alle vragen in een (sub)model, in formuliervolgorde. Bedragregels worden uitgevouwen."""
    from .bouwstenen import Bedragregel

    resultaat: list[Vraag] = []
    for naam, info in model.model_fields.items():
        extra = info.json_schema_extra or {}
        t, achtervoegsel = _kern(info.annotation)
        veldpad = f"{pad}.{naam}" if pad else naam
        rij = herhaalbaar or bool(achtervoegsel)

        if isinstance(t, type) and issubclass(t, BaseModel):
            onder = vragen(t, veldpad + achtervoegsel, rij)
            if t is Bedragregel:
                resultaat.append(_vraag(veldpad, extra, info.description, Vraagtype.BEDRAGREGEL, rij, extra.get("opties")))
                onder = _beperk_bedragregel(onder, veldpad + achtervoegsel, extra)
            resultaat += onder
            continue

        vraagtype = Vraagtype(extra["vraagtype"]) if "vraagtype" in extra else _afgeleid_type(t)
        opties = None
        if isinstance(t, type) and issubclass(t, Enum):
            opties = [(e.value, getattr(e, "label", e.value)) for e in t]
        resultaat.append(_vraag(veldpad + achtervoegsel, extra, info.description, vraagtype, rij, extra.get("opties"), opties))
    return resultaat


def _beperk_bedragregel(onder: list[Vraag], pad: str, extra: dict) -> list[Vraag]:
    """Laat alleen de delen van een Bedragregel zien die deze vraag toestaat."""
    toegestaan = extra.get("opties")
    delen = {"vast-bedrag": ".vast_bedrag.", "percentage": ".percentage.", "tijd": ".tijd."}
    resultaat = []
    for v in onder:
        rest = v.pad[len(pad):]
        if toegestaan and any(rest.startswith(p) for s, p in delen.items() if s not in toegestaan):
            continue
        if extra.get("zonder_per") and rest.endswith(".per"):
            continue
        if rest == ".soort" and toegestaan:
            v = replace(v, opties=[o for o in v.opties if o[0] in toegestaan])
        resultaat.append(v)
    return resultaat


def _vraag(pad, extra, beschrijving, vraagtype, herhaalbaar, toegestaan, opties=None) -> Vraag:
    if vraagtype == Vraagtype.BEDRAGREGEL:
        from .bouwstenen import BedragSoort

        opties = [(e.value, e.label) for e in BedragSoort]
    if toegestaan and opties:
        opties = [o for o in opties if o[0] in toegestaan]
    return Vraag(
        pad=pad,
        slug=extra.get("slug", ""),
        vraag=beschrijving or "",
        vraagtype=vraagtype,
        opties=opties or [],
        eenheid=extra.get("eenheid"),
        toon_als=extra.get("toon_als"),
        optioneel=bool(extra.get("optioneel")),
        herhaalbaar=herhaalbaar,
    )


def overzicht(model: type[BaseModel], max_opties: int = 4) -> str:
    """Leesbaar overzicht van alle vragen in een model (handig om rond te kijken)."""
    regels = []
    for v in vragen(model):
        opties = ""
        if v.opties:
            labels = [label for _, label in v.opties]
            opties = " | " + " · ".join(labels[:max_opties]) + (f" (+{len(labels) - max_opties})" if len(labels) > max_opties else "")
        eenheid = f" [{v.eenheid}]" if v.eenheid else ""
        regels.append(f"{v.pad:60} {v.vraagtype.value:11}{eenheid}{opties}")
    return "\n".join(regels)


__all__ = ["Keuze", "Vraag", "Vraagtype", "overzicht", "vragen"]
