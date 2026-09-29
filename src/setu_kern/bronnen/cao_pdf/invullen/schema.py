"""Formuliermodel → een strikt JSON-schema voor het LLM (``response_format`` json_schema, strict).

Regels voor strict mode: elk object heeft ``additionalProperties: false`` en al zijn velden in ``required``; een
leeg antwoord is ``null``. Keuzes zijn een ``enum`` van tekstwaarden, met de labels in de ``description``. Bij een
Bedragregel staan alleen de soorten (en delen) in het schema die de vraag toestaat.
"""

from typing import Any

from pydantic import BaseModel

from .typen import Beperking, Veld, enum_waarde, velden_van


def blok_schema(model: type[BaseModel], velden: Any = None) -> dict[str, Any]:
    """Het schema van (een deel van) een sectie; ``velden`` = de velden op het hoogste niveau van het blok."""
    return _object(model, velden, None)


def antwoord_schema(waarden: dict[str, Any]) -> dict[str, Any]:
    """Het hele antwoord van het LLM: de waarden, de onderbouwing per waarde en wat niet gevonden is."""
    tekst = {"type": "string"}
    return {
        "type": "object",
        "properties": {
            "waarden": waarden,
            "onderbouwing": {
                "type": "array",
                "description": "Per ingevuld veld (of per blok van velden): waar het in de cao staat.",
                "items": {
                    "type": "object",
                    "properties": {
                        "pad": {**tekst, "description": "Pad van het veld in 'waarden', bijv. 'bedrag.percentage.percentage'."},
                        "document": tekst,
                        "pagina": {"type": "integer"},
                        "artikel": {"type": ["string", "null"], "description": "Bijv. 'Artikel 12 lid 1'."},
                        "citaat": {**tekst, "description": "Letterlijk overgenomen uit een van de fragmenten."},
                    },
                    "required": ["pad", "document", "pagina", "artikel", "citaat"],
                    "additionalProperties": False,
                },
            },
            "niet_gevonden": {
                "type": "array",
                "items": tekst,
                "description": "Paden van vragen waarover de fragmenten niets zeggen (dat is iets anders dan 'nee').",
            },
        },
        "required": ["waarden", "onderbouwing", "niet_gevonden"],
        "additionalProperties": False,
    }


def _object(model: type[BaseModel], velden: Any, beperking: Beperking | None) -> dict[str, Any]:
    eigenschappen = {v.naam: _veld(v) for v in velden_van(model, velden, beperking)}
    return {
        "type": "object",
        "properties": eigenschappen,
        "required": list(eigenschappen),
        "additionalProperties": False,
    }


def _veld(v: Veld) -> dict[str, Any]:
    schema = _waarde(v.soort, v, nullable=True)
    beschrijving = beschrijving_van(v)
    if beschrijving:
        schema = {**schema, "description": beschrijving}
    return schema


def _waarde(soort, v: Veld, nullable: bool) -> dict[str, Any]:
    if soort.vorm == "lijst":
        return {"type": "array", "items": _waarde(soort.element, v, nullable=False)}
    if soort.vorm == "mapping":
        eigenschappen = {enum_waarde(k): _waarde(soort.element, v, nullable=True) for k in soort.sleutel}
        return {
            "type": "object",
            "properties": eigenschappen,
            "required": list(eigenschappen),
            "additionalProperties": False,
        }
    if soort.vorm == "model":
        obj = _object(soort.doel, None, v.beperking)
        return {"anyOf": [obj, {"type": "null"}]} if nullable else obj
    if soort.vorm == "enum":
        waarden: list[Any] = [enum_waarde(lid) for lid in v.keuzes or soort.doel]
        return {"type": ["string", "null"], "enum": [*waarden, None]} if nullable else {"type": "string", "enum": waarden}
    json_type = {"bool": "boolean", "int": "integer", "float": "number", "str": "string", "datum": "string", "tijd": "string"}[
        soort.vorm
    ]
    return {"type": [json_type, "null"]} if nullable else {"type": json_type}


def beschrijving_van(v: Veld) -> str:
    """De vraag zoals het LLM hem ziet: vraagtekst, eenheid, formaat, keuzes en voorwaarde."""
    delen = [v.info.description or ""]
    if v.extra.get("eenheid"):
        delen.append(f"Eenheid: {v.extra['eenheid']}.")
    vorm = v.soort.element.vorm if v.soort.vorm in ("lijst", "mapping") else v.soort.vorm
    if vorm == "datum":
        delen.append("Datum als JJJJ-MM-DD.")
    elif vorm == "tijd":
        delen.append("Tijd als UU:MM.")
    elif vorm == "bool":
        delen.append("Aanvinken = true; niet van toepassing = null.")
    if v.keuzes:
        delen.append("Keuzes: " + "; ".join(f"'{enum_waarde(k)}' = {getattr(k, 'label', k.value)}" for k in v.keuzes) + ".")
    if v.soort.vorm == "mapping":
        delen.append("Per sleutel: " + "; ".join(f"'{enum_waarde(k)}' = {getattr(k, 'label', k.value)}" for k in v.soort.sleutel) + ".")
    if v.extra.get("toon_als"):
        delen.append(f"Alleen invullen als: {v.extra['toon_als']}.")
    return " ".join(d for d in delen if d)
