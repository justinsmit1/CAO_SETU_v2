"""14 · Overig → SETU (src/definition/14_overig.tsx)."""

from collections.abc import Iterator
from functools import partial
from typing import Any

from .gedeeld import OTHER_OVERIG_START, get_line_amount_answer, tekst
from .motor import TODO_REPLACE_WITH_REAL_ORIGIN, Antwoorden, Opbouw, SetuVraag
from .setu_s13_aanvullende_regelingen import js_tekst


def _overige_regeling(i: int, waarde: Any, opbouw: Opbouw) -> Any:
    a = opbouw.antwoorden
    regeling = {
        "name": js_tekst(waarde),
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [get_line_amount_answer(a, ["overige-regelingen", i])],
    }
    voorwaarden = a.get(["overige-regelingen", i, "voorwaarden"])
    if voorwaarden:
        regeling["line"][0]["conditions"] = [{"conditionType": "Text", "description": js_tekst(voorwaarden)}]
    return regeling


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    # Het blok met de rijen is alleen zichtbaar bij "ja"; verborgen rijen gaan dus niet mee.
    ja = a.heeft("overige-regelingen-ja-nee", "ja")
    for i in range(a.rijen("overige-regelingen")):
        slug = ["overige-regelingen", i, "naam"]
        yield SetuVraag(
            slug,
            ["otherArrangement", OTHER_OVERIG_START + i],
            tekst(a, slug),
            omzetten=partial(_overige_regeling, i),
            zichtbaar=ja,
        )
