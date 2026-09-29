"""De Python-annotaties van het formuliermodel ontleden: ``X | None``, ``list[X]``, ``dict[K, X]``, submodel, enum.

Schema (``schema.py``) en omzetting (``omzetten.py``) gebruiken dezelfde ontleding, zodat ze niet uit elkaar lopen.
"""

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel

from ...wijzerbelonen.formulier.bouwstenen import BedragSoort, Bedragregel

# Welk deel van een Bedragregel hoort bij welke soort.
BEDRAGREGEL_DELEN = {
    BedragSoort.VAST_BEDRAG.value: "vast_bedrag",
    BedragSoort.PERCENTAGE.value: "percentage",
    BedragSoort.TIJD.value: "tijd",
}


@dataclass(frozen=True)
class Soort:
    """Eén ontlede annotatie. ``vorm``: model, lijst, mapping, enum, bool, int, float, str, datum, tijd."""

    vorm: str
    doel: Any = None  # het model, de enum of het element-/waardetype
    sleutel: type[Enum] | None = None  # bij een mapping
    element: "Soort | None" = None  # bij een lijst of mapping

    @property
    def is_bedragregel(self) -> bool:
        return self.vorm == "model" and self.doel is Bedragregel


def ontleed(annotatie: Any) -> Soort:
    oorsprong, args = get_origin(annotatie), get_args(annotatie)
    if oorsprong in (Union, UnionType):
        rest = [a for a in args if a is not NoneType]
        if len(rest) != 1:
            raise TypeError(f"annotatie met meerdere types wordt niet ondersteund: {annotatie}")
        return ontleed(rest[0])
    if oorsprong is list:
        return Soort("lijst", args[0], element=ontleed(args[0]))
    if oorsprong is dict:
        sleutel, waarde = args
        if not (isinstance(sleutel, type) and issubclass(sleutel, Enum)):
            raise TypeError(f"mapping zonder enum-sleutel wordt niet ondersteund: {annotatie}")
        return Soort("mapping", waarde, sleutel=sleutel, element=ontleed(waarde))
    if isinstance(annotatie, type):
        if issubclass(annotatie, BaseModel):
            return Soort("model", annotatie)
        if issubclass(annotatie, Enum):
            return Soort("enum", annotatie)
        if annotatie is bool:
            return Soort("bool")
        if annotatie is int:
            return Soort("int")
        if annotatie is float:
            return Soort("float")
        if annotatie is str:
            return Soort("str")
        if annotatie is dt.date:
            return Soort("datum")
        if annotatie is dt.time:
            return Soort("tijd")
    raise TypeError(f"annotatie wordt niet ondersteund: {annotatie}")


def extra(info: Any) -> dict[str, Any]:
    return info.json_schema_extra if isinstance(info.json_schema_extra, dict) else {}


def enum_waarde(lid: Enum) -> str:
    """De waarde van een keuze als tekst (ook bij enums met getallen, zoals ``NormaleArbeidsduur``)."""
    return str(lid.value)


def enum_lid(enum: type[Enum], waarde: Any) -> Enum | Any:
    """Het lid bij een tekstwaarde; onbekend → de waarde zelf (Pydantic geeft dan een duidelijke fout)."""
    for lid in enum:
        if enum_waarde(lid) == str(waarde):
            return lid
    return waarde


@dataclass(frozen=True)
class Beperking:
    """Wat een vraag toestaat bij een Bedragregel (``opties`` en ``zonder_per`` op het veld dat hem gebruikt).
    Geldt voor de Bedragregel zelf en voor zijn delen (vast bedrag, percentage, tijd)."""

    opties: frozenset[str] | None = None
    zonder_per: bool = False


@dataclass(frozen=True)
class Veld:
    naam: str
    info: Any
    soort: Soort
    extra: dict[str, Any]
    keuzes: list[Enum] | None  # bij een enum (of lijst/mapping van enums): de toegestane leden
    beperking: Beperking | None  # door te geven aan een submodel


def velden_van(model: type[BaseModel], velden: Any = None, beperking: Beperking | None = None) -> list[Veld]:
    """De velden van een model zoals het LLM ze ziet: gefilterd op ``velden`` (een blok) en op de beperking van
    een Bedragregel. Schema en omzetting gebruiken allebei deze functie."""
    uit = []
    for naam, info in model.model_fields.items():
        if velden is not None and naam not in velden:
            continue
        if beperking and model is Bedragregel and naam in BEDRAGREGEL_DELEN.values() and beperking.opties:
            if _soort_van(naam) not in beperking.opties:
                continue
        if beperking and beperking.zonder_per and model is not Bedragregel and naam == "per":
            continue
        e = extra(info)
        soort = ontleed(info.annotation)
        if soort.is_bedragregel:
            kind = Beperking(frozenset(e["opties"]) if e.get("opties") else None, bool(e.get("zonder_per")))
        elif model is Bedragregel and beperking:
            kind = beperking
        else:
            kind = None
        uit.append(Veld(naam, info, soort, e, _keuzes(soort, e, model, naam, beperking), kind))
    return uit


def _keuzes(soort: Soort, e: dict, model: type, naam: str, beperking: Beperking | None) -> list[Enum] | None:
    enum = soort.doel if soort.vorm == "enum" else soort.element.doel if soort.element and soort.element.vorm == "enum" else None
    if enum is None:
        return None
    leden = list(enum)
    toegestaan = e.get("opties")
    if model is Bedragregel and naam == "soort" and beperking and beperking.opties:
        toegestaan = beperking.opties
    if toegestaan and not soort.is_bedragregel:
        leden = [lid for lid in leden if enum_waarde(lid) in set(toegestaan)]
    return leden


def _soort_van(deel: str) -> str:
    return next(s for s, d in BEDRAGREGEL_DELEN.items() if d == deel)
