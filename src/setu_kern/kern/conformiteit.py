"""Vergelijkt het Python-kernmodel structureel met het officiële SETU-schema.

Het schema wordt vanaf de wortel doorlopen, tegelijk met de Pydantic-klassen. Per object wordt gecontroleerd:
- elk veld van het schema bestaat in het model en omgekeerd;
- verplicht/optioneel is gelijk;
- keuzelijsten (enum) hebben dezelfde waarden;
- bij "kies één van" (Occurrence, Condition) bestaat elke variant.

Gebruik: ``verschillen()`` → lijst met afwijkingen (leeg = conform).
"""

import types
import typing
from enum import Enum
from typing import Any, Literal, get_args, get_origin

from pydantic import BaseModel

from .bericht import InquiryPayEquity, officieel_schema

# Afwijkingen die bewust zijn (met reden).
BEWUST = {
    # Het schema vereist 'interval' maar definieert 'recurringInterval'; het model schrijft beide (zie tijd.py).
    "Recurring: verplicht veld 'interval' ontbreekt in model",
    "Recurring.recurringInterval: optioneel in schema, verplicht in model",
}


def verschillen() -> list[str]:
    schema = officieel_schema()
    uit: list[str] = []
    _vergelijk(schema, InquiryPayEquity, schema, uit, "InquiryPayEquity", set())
    return [v for v in uit if v not in BEWUST]


def _los_op(node: dict, root: dict) -> tuple[dict, str | None]:
    naam = None
    while "$ref" in node:
        naam = node["$ref"].rsplit("/", 1)[-1]
        node = {**root["definitions"][naam], **{k: v for k, v in node.items() if k != "$ref"}}
    return node, naam


def _kern_types(annotatie: Any) -> list[Any]:
    """Pakt Optional/Union/Annotated/list uit tot de onderliggende types."""
    herkomst = get_origin(annotatie)
    if herkomst is typing.Annotated:
        return _kern_types(get_args(annotatie)[0])
    if herkomst in (typing.Union, types.UnionType):
        return [t for a in get_args(annotatie) if a is not type(None) for t in _kern_types(a)]
    if herkomst is list:
        return _kern_types(get_args(annotatie)[0])
    return [annotatie]


def _vergelijk(node: dict, annotatie: Any, root: dict, uit: list[str], pad: str, gezien: set) -> None:
    node, naam = _los_op(node, root)
    label = naam or pad

    if node.get("type") == "array":
        _vergelijk(node["items"], annotatie, root, uit, pad + "[]", gezien)
        return

    varianten = node.get("oneOf") or node.get("anyOf")
    if varianten:
        kandidaten = [t for t in _kern_types(annotatie) if isinstance(t, type) and issubclass(t, BaseModel)]
        for variant in varianten:
            v_node, v_naam = _los_op(variant, root)
            passend = _zoek_variant(v_node, kandidaten)
            if passend is None:
                uit.append(f"{label}: variant {v_naam} ontbreekt in model")
            else:
                _vergelijk(variant, passend, root, uit, f"{pad}<{v_naam}>", gezien)
        return

    if "enum" in node:
        enums = [t for t in _kern_types(annotatie) if isinstance(t, type) and issubclass(t, Enum)]
        literals = [a for t in _kern_types(annotatie) if get_origin(t) is Literal for a in get_args(t)]
        waarden = {str(e.value) for e in enums[0]} if enums else {str(a) for a in literals}
        if set(map(str, node["enum"])) != waarden and not (literals and waarden <= set(map(str, node["enum"]))):
            ontbreekt = set(map(str, node["enum"])) - waarden
            teveel = waarden - set(map(str, node["enum"]))
            uit.append(f"{label}: keuzelijst verschilt (ontbreekt {sorted(ontbreekt)}, extra {sorted(teveel)})")
        return

    if node.get("type") != "object" or "properties" not in node:
        return

    modellen = [t for t in _kern_types(annotatie) if isinstance(t, type) and issubclass(t, BaseModel)]
    if not modellen:
        uit.append(f"{label}: schema verwacht een object, model heeft {annotatie!r}")
        return
    model = modellen[0]
    sleutel = (model, naam or pad)
    if sleutel in gezien:
        return
    gezien.add(sleutel)

    velden = {(info.alias or veldnaam): info for veldnaam, info in model.model_fields.items()}
    for prop in node["properties"]:
        if prop not in velden:
            uit.append(f"{label}: veld '{prop}' ontbreekt in model {model.__name__}")
    for prop in velden:
        if prop not in node["properties"]:
            uit.append(f"{label}: model {model.__name__} heeft extra veld '{prop}'")
    verplicht = set(node.get("required", []))
    for prop in verplicht - set(velden):
        uit.append(f"{label}: verplicht veld '{prop}' ontbreekt in model")
    for prop, info in velden.items():
        if prop not in node["properties"]:
            continue
        is_literal = get_origin(info.annotation) is Literal
        if prop in verplicht and not info.is_required() and not is_literal:
            uit.append(f"{label}.{prop}: verplicht in schema, optioneel in model")
        if prop not in verplicht and info.is_required():
            uit.append(f"{label}.{prop}: optioneel in schema, verplicht in model")
        _vergelijk(node["properties"][prop], info.annotation, root, uit, f"{label}.{prop}", gezien)


def _zoek_variant(v_node: dict, kandidaten: list[type[BaseModel]]) -> type[BaseModel] | None:
    """Kiest de modelklasse bij een variant op basis van de vaste waarde van het type-veld."""
    for prop, spec in v_node.get("properties", {}).items():
        vast = spec.get("const") or (spec.get("enum") if len(spec.get("enum", [])) == 1 else None)
        if vast is None:
            continue
        vast = vast[0] if isinstance(vast, list) else vast
        for k in kandidaten:
            for veldnaam, info in k.model_fields.items():
                if (info.alias or veldnaam) == prop and get_origin(info.annotation) is Literal and vast in get_args(info.annotation):
                    return k
    return None
