"""10 · Individueel keuzebudget → SETU (src/definition/10_individueel-keuzebudget.tsx)."""

from collections.abc import Iterator
from typing import Any

from .gedeeld import INDIVIDUAL_CHOICE_BUDGET, get_line_amount_answer, keuze
from .motor import CHECKED, TODO_REPLACE_WITH_REAL_ORIGIN, Antwoorden, Opbouw, SetuVraag

_OPGENOMEN = "ikb-opgenomen-arbeidsvoorwaarden"

# (slugdeel, begin van de omschrijving) in de volgorde van de webform.
_ARBEIDSVOORWAARDEN = [
    ("bovenwettelijke-vakantiedagen", "Bovenwettelijke vakantiedagen"),
    ("adv-dagen", "ADV dagen"),
    ("eindejaarsuitkering", "Eindejaarsuitkering"),
    ("vakantiebijslag", "Vakantiebijslag"),
]


def js_tekst(waarde: Any) -> str:
    """Een waarde in een JavaScript-template (`${...}`): null wordt "null", true wordt "true"."""
    if waarde is None:
        return "null"
    if isinstance(waarde, bool):
        return "true" if waarde else "false"
    return str(waarde)


def _budget(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    budget: dict[str, Any] = {
        "name": "Individueel keuze budget",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [get_line_amount_answer(a, "individueel-keuzebudget")],
    }
    # Let op: de opgenomen arbeidsvoorwaarden worden gelezen zonder te kijken of ze zichtbaar zijn
    # (net als in de webform); een ontbrekend percentage of "van" komt als "null" in de tekst.
    if a.get("ikb-arbeidsvoorwaarden-opgenomen") == "ja":
        opties = []
        for deel, naam in _ARBEIDSVOORWAARDEN:
            slug = f"{_OPGENOMEN}/{deel}"
            if a.get(slug) == CHECKED:
                opties.append(
                    {"description": f"{naam} voor {js_tekst(a.get(f'{slug}/percentage'))}% van {js_tekst(a.get(f'{slug}/van'))}"}
                )
        if a.get(f"{_OPGENOMEN}/anders") == CHECKED:
            opties.append({"description": f"Anders: {js_tekst(a.get(f'{_OPGENOMEN}/anders/namelijk'))}"})
        budget["option"] = opties
    return budget


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    yield SetuVraag(
        "individueel-keuzebudget",
        ["individualChoiceBudget", INDIVIDUAL_CHOICE_BUDGET],
        keuze(a, "individueel-keuzebudget"),
        omzetten=_budget,
    )
