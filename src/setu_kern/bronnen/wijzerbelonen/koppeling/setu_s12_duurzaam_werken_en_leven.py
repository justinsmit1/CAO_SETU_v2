"""12 · Duurzaam werken en leven → SETU (src/definition/12_duurzaam-werken-en-leven.tsx).

Elke regeling (duurzame inzetbaarheid en vitaliteit/gezondheid) is een checkbox met een ``setuPath`` op een
vaste positie in ``sustainableEmployability``; de vervolgvragen worden in ``convertSetuValue`` gelezen.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from .gedeeld import (
    SUSTAINABLE_EMPLOYABILITY_ANDERS,
    SUSTAINABLE_EMPLOYABILITY_DUURZAME_SAMENLEVING,
    SUSTAINABLE_EMPLOYABILITY_FINANCIELE_GEZONDHEID,
    SUSTAINABLE_EMPLOYABILITY_FYSIEKE_GEZONDHEID,
    SUSTAINABLE_EMPLOYABILITY_LOOPBAANCOACHING,
    SUSTAINABLE_EMPLOYABILITY_MENTALE_GEZONDHEID,
    SUSTAINABLE_EMPLOYABILITY_OPLEIDINGEN,
    SUSTAINABLE_EMPLOYABILITY_OUTPLACEMENTTRAJECTEN,
    SUSTAINABLE_EMPLOYABILITY_SCHOLING_NEDERLAND,
    SUSTAINABLE_EMPLOYABILITY_SOCIALE_BEGELEIDING_NEDERLAND,
    SUSTAINABLE_EMPLOYABILITY_VERPLICHTE_SCHOLING,
    SUSTAINABLE_EMPLOYABILITY_VITALITEIT_ANDERS,
    SUSTAINABLE_EMPLOYABILITY_VITALITEITSBUDGET,
    SUSTAINABLE_EMPLOYABILITY_VOORLICHTING_NEDERLAND,
    keuze,
)
from .motor import TODO_REPLACE_WITH_REAL_ORIGIN, Antwoorden, Opbouw, SetuVraag, is_waar, to_float, vinkje_waarde
from .setu_s10_individueel_keuzebudget import js_tekst

_NL = "met betrekking tot het in Nederland werken en verblijven van de niet permanent in Nederland woonachtige werknemer"


@dataclass(frozen=True)
class Regeling:
    slug: str
    label: str
    index: int
    type_code: str
    namelijk: bool = False  # andersHelp: de regeling heeft een namelijk-veld dat in de naam komt


REGELINGEN = [
    # Duurzame inzetbaarheid
    Regeling("duurzame-inzetbaarheid-regelingen/opleidingen", "Opleidingen", SUSTAINABLE_EMPLOYABILITY_OPLEIDINGEN, "Education"),
    Regeling(
        "duurzame-inzetbaarheid-regelingen/loopbaancoaching",
        "Loopbaancoaching",
        SUSTAINABLE_EMPLOYABILITY_LOOPBAANCOACHING,
        "CareerCoaching",
    ),
    Regeling(
        "duurzame-inzetbaarheid-regelingen/outplacementtrajecten",
        "Outplacementtrajecten",
        SUSTAINABLE_EMPLOYABILITY_OUTPLACEMENTTRAJECTEN,
        "OutplacementPrograms",
    ),
    Regeling(
        "duurzame-inzetbaarheid-regelingen/voorlichting-nederland",
        f"Voorlichting {_NL}",
        SUSTAINABLE_EMPLOYABILITY_VOORLICHTING_NEDERLAND,
        "InformationProvision",
    ),
    Regeling(
        "duurzame-inzetbaarheid-regelingen/scholing-nederland",
        f"Scholing {_NL}",
        SUSTAINABLE_EMPLOYABILITY_SCHOLING_NEDERLAND,
        "Education",
    ),
    Regeling(
        "duurzame-inzetbaarheid-regelingen/sociale-begeleiding-nederland",
        f"Sociale begeleiding {_NL}",
        SUSTAINABLE_EMPLOYABILITY_SOCIALE_BEGELEIDING_NEDERLAND,
        "SocialSupport",
    ),
    Regeling("duurzame-inzetbaarheid-regelingen/anders", "Anders, namelijk:", SUSTAINABLE_EMPLOYABILITY_ANDERS, "Other", True),
    # Vitaliteit en gezondheid
    Regeling(
        "vitaliteit-gezondheid-regelingen/fysieke-gezondheid",
        "Regeling ter bevordering van de fysieke gezondheid, namelijk:",
        SUSTAINABLE_EMPLOYABILITY_FYSIEKE_GEZONDHEID,
        "ArrangementForHealth",
        True,
    ),
    Regeling(
        "vitaliteit-gezondheid-regelingen/mentale-gezondheid",
        "Regeling ter bevordering van de mentale gezondheid, namelijk:",
        SUSTAINABLE_EMPLOYABILITY_MENTALE_GEZONDHEID,
        "ArrangementForMentalHealth",
        True,
    ),
    Regeling(
        "vitaliteit-gezondheid-regelingen/financiele-gezondheid",
        "Regeling ter bevordering van de financiële gezondheid, namelijk:",
        SUSTAINABLE_EMPLOYABILITY_FINANCIELE_GEZONDHEID,
        "ArrangementForFinancialHealth",
        True,
    ),
    Regeling(
        "vitaliteit-gezondheid-regelingen/vitaliteitsbudget",
        "Vitaliteitsbudget",
        SUSTAINABLE_EMPLOYABILITY_VITALITEITSBUDGET,
        "VitalityBudget",
    ),
    Regeling(
        "vitaliteit-gezondheid-regelingen/anders", "Anders, namelijk:", SUSTAINABLE_EMPLOYABILITY_VITALITEIT_ANDERS, "Other", True
    ),
]


def _to_string(waarde: Any) -> str | None:
    """toString2 (src/util/cast.ts)."""
    return None if waarde is None else js_tekst(waarde)


def _eerste_regel(regels: list, eigenschap: str) -> dict:
    """``line[0].<eigenschap>``: zonder regel loopt de webform vast (TypeError), en daarmee de hele export."""
    if not regels:
        raise TypeError(f"Cannot read properties of undefined (reading '{eigenschap}')")
    return regels[0]


def _vaste_regel(bedrag: Any, eenheid: str, per: Any) -> dict:
    return {
        "amount": {"value": to_float(bedrag), "unitCode": eenheid, "baseAmount": {"unitCode": "Fixed"}},
        "interval": {"value": 1, "unitCode": per},
        "conditions": [],
    }


# --- regelingen (makeBlockItems)
def _regeling_omzetter(r: Regeling):
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if not is_waar(waarde):
            return None
        a = opbouw.antwoorden
        s = r.slug
        naam = f"{r.label} {js_tekst(a.get(f'{s}/namelijk'))}" if r.namelijk else r.label
        item: dict[str, Any] = {
            "name": naam,
            "typeCode": r.type_code,
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [],
        }
        regels = item["line"]
        # Let op: de vervolgvragen worden gelezen zonder te kijken of ze zichtbaar zijn (zoals de webform).
        budget = a.get(f"{s}/budget")
        if budget == "ja":
            soort = a.get(f"{s}/budget/type")
            if soort == "percentage":
                regels.append(
                    {
                        "amount": {
                            "value": to_float(a.get(f"{s}/budget/percentage/percentage")),
                            "unitCode": "Percentage",
                            "baseAmount": {"unitCode": a.get(f"{s}/budget/percentage/van")},
                        },
                        "interval": {"value": 1, "unitCode": a.get(f"{s}/budget/percentage/tijdvak")},
                        "conditions": [],
                    }
                )
            elif soort == "vast-bedrag":
                regels.append(
                    _vaste_regel(a.get(f"{s}/budget/vast-bedrag/bedrag"), "Euro", a.get(f"{s}/budget/vast-bedrag/tijdvak"))
                )
            elif soort == "aantal-dagen-per-jaar":
                regels.append(_vaste_regel(a.get(f"{s}/budget/aantal-dagen-per-jaar/aantal"), "Day", "Year"))
        elif budget == "nee-gemiddeld":
            regels.append(
                _vaste_regel(a.get(f"{s}/gemiddeld/vast-bedrag/bedrag"), "Euro", a.get(f"{s}/gemiddeld/vast-bedrag/tijdvak"))
            )
        if a.get(f"{s}/naar-rato") == "ja" and _eerste_regel(regels, "amount").get("amount"):
            regels[0]["amount"]["proportional"] = {"partTimePercentage": True, "employmentDuration": True}
        if a.get(f"{s}/uitgekeerd") == "ja":
            _eerste_regel(regels, "conditions")["conditions"].append(
                {
                    "conditionType": "Text",
                    "description": "Dit budget wordt uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt, "
                    f"onder de volgende voorwaarden: {js_tekst(a.get(f'{s}/uitgekeerd/ja/namelijk'))}",
                }
            )
        if a.get(f"{s}/uitgekeerd") == "nee":
            _eerste_regel(regels, "conditions")["conditions"].append(
                {
                    "conditionType": "Text",
                    "description": "Dit bedrag wordt NIET uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt.",
                }
            )
        if a.get(f"{s}/voorwaarden") == "ja":
            voorwaarden = a.get(f"{s}/voorwaarden/ja/namelijk")
            if is_waar(voorwaarden):
                _eerste_regel(regels, "conditions")["conditions"].append(
                    {"conditionType": "Text", "description": _to_string(voorwaarden)}
                )
        return item

    return omzetten


# --- verplichte scholing
def _verplichte_scholing(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    item = {
        "name": f"Verplichte scholing: {js_tekst(a.get('verplichte-scholing/ja/namelijk'))}",
        "typeCode": "Other",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [
            {
                "amount": {
                    "value": to_float(a.get("verplichte-scholing-tijd")),
                    "unitCode": a.get("verplichte-scholing-tijd-type"),
                    "baseAmount": {"unitCode": "Fixed"},
                },
                "interval": {"value": 1, "unitCode": "Item"},
                "conditions": [],
            },
            {
                "amount": {
                    "value": to_float(a.get("verplichte-scholing-kosten")),
                    "unitCode": "Euro",
                    "baseAmount": {"unitCode": "Fixed"},
                },
                "interval": {"value": 1, "unitCode": "Item"},
            },
        ],
    }
    # Let op: zonder antwoord op "wanneer" kiest de webform ook "Op een ander moment".
    if a.get("verplichte-scholing-wanneer") == "tijdens-werktijd":
        tekst = f"Tijdens werktijd, namelijk: {js_tekst(a.get('verplichte-scholing-wanneer/tijdens-werktijd/namelijk'))}"
    else:
        tekst = f"Op een ander moment, namelijk: {js_tekst(a.get('verplichte-scholing-wanneer/ander-moment/namelijk'))}"
    item["line"][0]["conditions"].append({"conditionType": "Text", "description": tekst})
    return item


# --- duurzame samenleving
def _duurzame_samenleving(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    h = "duurzame-samenleving-budget-hoogte"
    regel: dict[str, Any] = {
        "amount": {"value": 0, "unitCode": "Euro", "baseAmount": {"unitCode": "Fixed"}},
        "interval": {"value": 1, "unitCode": "Year"},
        "conditions": [],
    }
    of_jaar = lambda w: w if is_waar(w) else "Year"  # noqa: E731
    soort = a.get(h)
    if soort == "percentage":
        regel["amount"] = {
            "value": to_float(a.get(f"{h}/percentage/percentage")),
            "unitCode": "Percentage",
            "baseAmount": {"unitCode": a.get(f"{h}/percentage/van")},
        }
        regel["interval"] = {"value": 1, "unitCode": of_jaar(a.get(f"{h}/percentage/tijdvak"))}
    elif soort == "vast-bedrag":
        regel["amount"] = {
            "value": to_float(a.get(f"{h}/vast-bedrag/bedrag")),
            "unitCode": "Euro",
            "baseAmount": {"unitCode": "Fixed"},
        }
        regel["interval"] = {"value": 1, "unitCode": of_jaar(a.get(f"{h}/vast-bedrag/tijdvak"))}
    elif soort == "uren-of-dagen":
        regel["amount"] = {
            "value": to_float(a.get(f"{h}/uren-of-dagen/aantal")),
            "unitCode": a.get(f"{h}/uren-of-dagen/type"),
            "baseAmount": {"unitCode": "Fixed"},
        }
        regel["interval"] = {"value": 1, "unitCode": of_jaar(a.get(f"{h}/dagen-per/per"))}
    if a.get("duurzame-samenleving-budget-naar-rato") == "ja":
        regel["amount"]["proportional"] = {"partTimePercentage": True, "employmentDuration": True}
    uitgekeerd = a.get("duurzame-samenleving-budget-uitgekeerd")
    if uitgekeerd == "ja":
        voorwaarden = a.get("duurzame-samenleving-budget-uitgekeerd/ja/voorwaarden")
        if is_waar(voorwaarden):
            tekst = (
                "Dit budget wordt uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt, "
                f"onder de volgende voorwaarden: {js_tekst(voorwaarden)}"
            )
        else:
            tekst = "Dit budget wordt uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt."
        regel["conditions"].append({"conditionType": "Text", "description": tekst})
    elif uitgekeerd == "nee":
        regel["conditions"].append(
            {
                "conditionType": "Text",
                "description": "Dit budget wordt NIET uitgekeerd als er geen of niet geheel gebruik van wordt gemaakt.",
            }
        )
    if a.get("duurzame-samenleving-budget-voorwaarden") == "ja":
        voorwaarden = a.get("duurzame-samenleving-budget-voorwaarden/ja/namelijk")
        if is_waar(voorwaarden):
            regel["conditions"].append({"conditionType": "Text", "description": _to_string(voorwaarden)})
    return {
        "name": "Duurzame samenleving",
        "typeCode": "SustainableSociety",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [regel],
    }


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    for r in REGELINGEN:
        yield SetuVraag(r.slug, ["sustainableEmployability", r.index], vinkje_waarde(a.get(r.slug)), omzetten=_regeling_omzetter(r))
    yield SetuVraag(
        "verplichte-scholing",
        ["sustainableEmployability", SUSTAINABLE_EMPLOYABILITY_VERPLICHTE_SCHOLING],
        keuze(a, "verplichte-scholing"),
        omzetten=_verplichte_scholing,
    )
    yield SetuVraag(
        "duurzame-samenleving-budget",
        ["sustainableEmployability", SUSTAINABLE_EMPLOYABILITY_DUURZAME_SAMENLEVING],
        keuze(a, "duurzame-samenleving-budget"),
        omzetten=_duurzame_samenleving,
        zichtbaar=a.heeft("duurzame-samenleving-regeling", "ja"),
    )
