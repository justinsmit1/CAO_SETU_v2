"""05 · Vakantiebijslag → SETU (src/definition/05_vakantiebijslag.tsx)."""

from collections.abc import Iterator
from typing import Any

from .gedeeld import HOLIDAY_ALLOWANCE_PERCENTAGE_PERIOD, get_line_amount_answer, keuze
from .motor import TODO_REPLACE_WITH_REAL_ORIGIN, Antwoorden, Opbouw, SetuVraag


def _vakantiebijslag(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    return {
        "name": "Vakantiebijslag",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [get_line_amount_answer(opbouw.antwoorden, "vakantiebijslag")],
    }


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    yield SetuVraag(
        "vakantiebijslag/ja-nee",
        ["holidayAllowance", HOLIDAY_ALLOWANCE_PERCENTAGE_PERIOD],
        keuze(a, "vakantiebijslag/ja-nee"),
        omzetten=_vakantiebijslag,
    )
