"""11 · Pensioen → SETU (src/definition/11_pensioen.tsx)."""

from collections.abc import Iterator
from typing import Any

from .gedeeld import keuze
from .motor import TODO_REPLACE_WITH_REAL_ORIGIN, Antwoorden, Opbouw, SetuVraag, is_waar, to_float


def _js_to_string(waarde: Any) -> str | None:
    """``waarde?.toString()``."""
    if waarde is None:
        return None
    if isinstance(waarde, bool):
        return "true" if waarde else "false"
    return str(waarde)


def _pensioen(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    regel = {
        "amount": {
            "value": to_float(a.get("pensioenregeling/werkgeverspremie/percentage")),
            "unitCode": "Percentage",
            "baseAmount": {"unitCode": "YearlyRate", "baseType": "Pension"},
        },
        "interval": {"value": 1, "unitCode": "Year"},
        "contributionSource": "Employer",
        "conditions": [],
    }
    naam = _js_to_string(a.get("pensioenregeling/pensioenfonds/naam"))
    pensioen: dict[str, Any] = {
        "name": naam if is_waar(naam) else "Pensioenregeling",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [regel],
    }
    if a.get("pensioenregeling/franchise/van-toepassing") == "ja":
        # Zonder beschrijving blijft een lege franchise over, die clean() weer weghaalt.
        pensioen["franchise"] = {"description": _js_to_string(a.get("pensioenregeling/franchise/namelijk"))}
    return pensioen


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    yield SetuVraag(
        "pensioenregeling/van-toepassing", ["pension", 0], keuze(a, "pensioenregeling/van-toepassing"), omzetten=_pensioen
    )
