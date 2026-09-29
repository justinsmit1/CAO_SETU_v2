"""13 · Aanvullende regelingen → SETU (src/definition/13_aanvullende-regelingen.tsx)."""

from collections.abc import Iterator
from dataclasses import dataclass
from functools import partial
from typing import Any

from .gedeeld import (
    OTHER_ACCIDENT_BENEFIT,
    OTHER_PAWW,
    OTHER_PAZW,
    OTHER_RVU_REGELING,
    OTHER_WGA_HIAAT,
    get_line_amount_answer,
    keuze,
    tekst,
)
from .motor import DONT_AUTO_SET_SETU_VALUE, TODO_REPLACE_WITH_REAL_ORIGIN, Antwoorden, Opbouw, SetuVraag, extra_lijst


@dataclass(frozen=True)
class Regeling:
    """Eén rij uit ``makeAanvullendeRegelingenRows`` (ook gebruikt door 15 Grondslagen)."""

    slug: str
    setu_naam: str
    type_code: str
    index: int


# In dezelfde volgorde als makeAanvullendeRegelingenRows.
REGELINGEN = [
    Regeling("aanvullende-sociale-zekerheidsregelingen/paww", "PAWW regeling", "PAWW", OTHER_PAWW),
    Regeling("aanvullende-sociale-zekerheidsregelingen/pazw", "PAZW regeling", "PAZW", OTHER_PAZW),
    Regeling(
        "aanvullende-sociale-zekerheidsregelingen/rvu-regeling",
        "RVU regeling, generatiepact of regeling om minder te gaan werken richting het pensioen",
        "RVU",
        OTHER_RVU_REGELING,
    ),
    Regeling("aanvullende-sociale-zekerheidsregelingen/wga-hiaat", "WGA-Hiaat regeling", "WGA", OTHER_WGA_HIAAT),
    Regeling(
        "aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering",
        "Ongevallenverzekering",
        "AccidentBenefit",
        OTHER_ACCIDENT_BENEFIT,
    ),
]


def js_tekst(waarde: Any) -> str | None:
    """``waarde?.toString()``: None blijft None, true wordt "true", 8.0 wordt "8"."""
    if waarde is None:
        return None
    if isinstance(waarde, bool):
        return "true" if waarde else "false"
    if isinstance(waarde, float) and waarde.is_integer():
        return str(int(waarde))
    return str(waarde)


def _regeling(regeling: Regeling, waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    omschrijving = js_tekst(a.get(f"{regeling.slug}/omschrijving"))
    # Ook bij RVU wordt de dekkingswaarde gelezen (er is dan alleen geen vraag voor).
    return {
        "name": regeling.setu_naam,
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "description": omschrijving if omschrijving is not None else "",
        "typeCode": regeling.type_code,
        "line": [
            {**get_line_amount_answer(a, f"{regeling.slug}/werkgeverspremie"), "contributionSource": "Employer"},
            {**get_line_amount_answer(a, f"{regeling.slug}/werknemerspremie"), "contributionSource": "Employee"},
        ],
        "coverage": get_line_amount_answer(a, f"{regeling.slug}/dekkingswaarde").get("amount"),
    }


def _andere_regeling(i: int, waarde: Any, opbouw: Opbouw) -> Any:
    a = opbouw.antwoorden
    rij = ["andere-sociale-regelingen", i]
    extra_lijst(opbouw, "other_EXTRA_OTHERS").append(
        {
            "name": "Andere aanvullende sociale zekerheidsregeling",
            "description": js_tekst(waarde),
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [
                {**get_line_amount_answer(a, [*rij, "werkgeverspremie", 0]), "contributionSource": "Employer"},
                {**get_line_amount_answer(a, [*rij, "werknemerspremie", 0]), "contributionSource": "Employee"},
            ],
        }
    )
    return DONT_AUTO_SET_SETU_VALUE


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    for regeling in REGELINGEN:
        yield SetuVraag(
            regeling.slug,
            ["supplementaryArrangement", regeling.index],
            keuze(a, regeling.slug),
            omzetten=partial(_regeling, regeling),
        )

    # Anders: de rijen hebben geen showIf, dus ze gaan ook mee bij "andere-sociale-regelingen/ja-nee" = nee.
    for i in range(a.rijen("andere-sociale-regelingen")):
        slug = ["andere-sociale-regelingen", i, "omschrijving"]
        yield SetuVraag(slug, [DONT_AUTO_SET_SETU_VALUE], tekst(a, slug), omzetten=partial(_andere_regeling, i))
