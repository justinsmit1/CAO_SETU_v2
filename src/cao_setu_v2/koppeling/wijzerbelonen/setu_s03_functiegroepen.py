"""03 · Functiegroepen → SETU (src/definition/03_functiegroepen.tsx).

Een functiegroep wordt een ``positionProfile``. De gekozen salarisschaal (waarde ``"b,s"``) schrijft zelf niets
(setuPath DONT_AUTO_SET), maar voegt een ``positionProfileReference`` toe aan ``remuneration[b].salaryScale[s]``,
als die schaal op dat moment in de SETU staat. Fouten daarbij slikt de webform in (``finally { return null }``).
"""

from collections.abc import Iterator
from typing import Any

from .gedeeld import keuze, tekst
from .motor import DONT_AUTO_SET_SETU_VALUE, Antwoorden, Omzetter, Opbouw, SetuVraag, to_integer


def _code(i: int) -> Omzetter:
    """Zonder code wordt de titel gebruikt (shouldConvertNullSetuValue)."""

    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        return waarde if waarde else opbouw.antwoorden.get(["functie-groepen", i, "titel"])

    return omzetten


def _salarisschaal(i: int) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if not isinstance(waarde, str):
            return None
        delen = [to_integer(d) for d in waarde.split(",")]
        if len(delen) < 2 or delen[0] is None or delen[1] is None:
            return None
        b, s = delen[0], delen[1]
        schaal = _element(_element(opbouw.data.get("remuneration"), b, "salaryScale"), s)
        if schaal is None:
            return None
        a = opbouw.antwoorden
        code = a.get(["functie-groepen", i, "id"])
        if schaal.get("positionProfileReference") is None:  # ??= []
            schaal["positionProfileReference"] = []
        schaal["positionProfileReference"].append(
            {"positionId": {"value": code if code is not None else a.get(["functie-groepen", i, "titel"])}}
        )
        return None

    return omzetten


def _element(lijst: Any, index: int, sleutel: str | None = None) -> Any:
    """``lijst?.[index]`` (en daarna ``?.[sleutel]``) zoals JavaScript: None bij een ongeldige index."""
    if not isinstance(lijst, list) or not 0 <= index < len(lijst):
        return None
    item = lijst[index]
    if sleutel is None:
        return item
    return item.get(sleutel) if isinstance(item, dict) else None


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    for i in range(a.rijen("functie-groepen")):
        rij = ["functie-groepen", i]
        yield SetuVraag([*rij, "titel"], ["positionProfile", i, "positionTitle"], tekst(a, [*rij, "titel"]))
        yield SetuVraag(
            [*rij, "id"],
            ["positionProfile", i, "positionId", "value"],
            tekst(a, [*rij, "id"]),
            omzetten=_code(i),
            omzetten_bij_leeg=True,
        )
        yield SetuVraag(
            [*rij, "salarisschalen"], [DONT_AUTO_SET_SETU_VALUE], keuze(a, [*rij, "salarisschalen"]), omzetten=_salarisschaal(i)
        )
