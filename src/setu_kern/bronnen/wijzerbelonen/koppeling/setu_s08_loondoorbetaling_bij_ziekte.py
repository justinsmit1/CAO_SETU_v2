"""08 · Loondoorbetaling bij ziekte → SETU (src/definition/08_loondoorbetaling-bij-ziekte.tsx).

Bekende bugs van de webform die hier bewust worden nagedaan (zie docs/formulier/08_loondoorbetaling-bij-ziekte.md):
- elke ``line`` krijgt het percentage en de grondslag van rij 0 (``value`` en ``i2`` i.p.v. ``j``);
- ``waitingDays`` wordt gezet zodra ``wachtdagen_ja_namelijk`` een waarde heeft, ook bij ``wachtdagen`` = ``nee``;
- zonder percentage in rij 0 komt er geen ``sickPay`` (en dus ook geen wachtdagen) in SETU.
"""

from collections.abc import Iterator
from typing import Any

from .gedeeld import ALLOWANCE_WACHTDAGCOMPENSATIE, keuze, tekst
from .motor import TODO_REPLACE_WITH_REAL_ORIGIN, Antwoorden, Opbouw, SetuVraag, is_waar, to_float

_RIJEN = "loondoorbetaling-bij-ziekte"


def _req_string(waarde: Any) -> str:
    """reqString: ``String(waarde)``, of een lege tekst bij null/undefined."""
    return "" if waarde is None else str(waarde)


def _sick_pay(i: int):
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        a = opbouw.antwoorden
        if not is_waar(waarde) or i != 0:
            return None
        sick_pay: dict[str, Any] = {"name": "Loondoorbetaling bij ziekte", "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN}}
        regels = []
        for j in range(a.rijen(_RIJEN)):
            regel: dict[str, Any] = {
                "amount": {
                    "value": to_float(waarde),  # bug: het percentage van rij 0
                    "unitCode": "Percentage",
                    "baseAmount": {
                        "unitCode": a.get([_RIJEN, j, "percentage_bedrag"]),
                        "baseType": a.get([_RIJEN, i, "grondslag"]),  # bug: i2 i.p.v. j
                    },
                },
                "interval": {"value": 1, "unitCode": _of(a.get([_RIJEN, j, "percentage_per_tijdvak"]), "Day")},
                "conditions": [],
            }
            if is_waar(a.get([_RIJEN, j, "voorwaarden"])):
                regel["conditions"].append({"conditionType": "Text", "description": _req_string(a.get([_RIJEN, j, "voorwaarden"]))})
            regels.append(regel)
        sick_pay["line"] = regels
        if is_waar(a.get("wachtdagen_ja_namelijk")):
            sick_pay["waitingDays"] = {"value": to_float(a.get("wachtdagen_ja_namelijk")), "unitCode": "Day"}
            if a.get("wachtdagen_voorwaarden") == "ja":
                sick_pay["waitingDays"]["conditions"] = [
                    {"conditionType": "Text", "description": _req_string(a.get("wachtdagen_voorwaarden_ja_namelijk"))}
                ]
        return sick_pay

    return omzetten


def _of(waarde: Any, standaard: Any) -> Any:
    """JavaScript ``waarde ?? standaard``."""
    return standaard if waarde is None else waarde


def _wachtdagcompensatie(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    regel: dict[str, Any] = {"interval": {"value": 1, "unitCode": "Day"}, "conditions": []}
    soort = a.get("wachtdagcompensatie/amount-type")
    if soort == "vast-bedrag":
        regel["amount"] = {
            "value": to_float(a.get("wachtdagcompensatie/amount-type/vast-bedrag/bedrag")),
            "unitCode": "Euro",
            "baseAmount": {"unitCode": "Fixed"},
        }
    elif soort == "percentage":
        regel["amount"] = {
            "value": to_float(a.get("wachtdagcompensatie/amount-type/percentage/percentage")),
            "unitCode": "Percentage",
            "baseAmount": {"unitCode": a.get("wachtdagcompensatie/amount-type/percentage/basis")},
        }
    return {"name": "Wachtdagcompensatie", "typeCode": "EA600", "line": [regel], "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN}}


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    for i in range(a.rijen(_RIJEN)):
        slug = [_RIJEN, i, "percentage"]
        yield SetuVraag(slug, ["sickPay", 0], tekst(a, slug, "float"), omzetten=_sick_pay(i))

    yield SetuVraag(
        "wachtdagcompensatie",
        ["allowance", ALLOWANCE_WACHTDAGCOMPENSATIE],
        keuze(a, "wachtdagcompensatie"),
        omzetten=_wachtdagcompensatie,
        zichtbaar=a.heeft("wachtdagen", "ja"),
    )
