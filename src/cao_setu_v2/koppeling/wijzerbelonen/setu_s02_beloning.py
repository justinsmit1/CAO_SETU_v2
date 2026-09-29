"""02 · Beloning → SETU (src/definition/02_beloning.tsx).

Per salaristabel ``beloningen[bi]`` één ``remuneration[bi]``. Let op de volgorde: de afwijkende roosters
(laatste subsectie van een salaristabel) kopiëren ``remuneration[bi]`` zoals die op dat moment is; wat later
nog wordt toegevoegd (functiegroepen in sectie 03) komt dus niet in de kopieën terecht.

Nagedane eigenaardigheden van de webform:
- een ontbrekende toelichting wordt de tekst ``"null"`` (``getAnswer(...) + ""``), bij betaalde pauzes en bij
  "Wanneer wordt de verhoging toegekend: anders";
- werkervaring bij de inschaling zonder dat er al iets van deze salaristabel in de SETU staat, laat de export
  van de webform vastlopen (``setuData.remuneration[bi]`` is dan ``undefined``); hier een ``TypeError``.
  Hetzelfde geldt voor afwijkende roosters als er nog helemaal geen ``remuneration`` is.
"""

import json
from collections.abc import Iterator
from typing import Any

from .gedeeld import (
    ALLOWANCE_PAID_BREAKS,
    BELONING_VOORWAARDE_ANDERS,
    INDIVIDUAL_SALARY_INCREASE_RATE_ANDERS,
    INDIVIDUAL_SALARY_INCREASE_RATE_BEOORDELING_WERKNEMER,
    INDIVIDUAL_SALARY_INCREASE_RATE_DUUR_DIENSTVERBAND,
    INDIVIDUAL_SALARY_INCREASE_RATE_OVERIG,
    keuze,
    tekst,
    work_duration_2_interval,
)
from .motor import (
    ANDERS_NAMELIJK,
    CHECKED,
    DONT_AUTO_SET_SETU_VALUE,
    TODO_REPLACE_WITH_REAL_ORIGIN,
    Antwoorden,
    Omzetter,
    Opbouw,
    SetuVraag,
    datum_waarde,
    to_date_time_string,
    to_float,
    vinkje_waarde,
)

_NORMALE_ARBEIDSDUUR = {ANDERS_NAMELIJK: DONT_AUTO_SET_SETU_VALUE}  # "Anders, namelijk:" heeft setuValue DONT_AUTO_SET

# periodiekeVerhogingenRows: (slug, label, index)
_PERIODIEKE_RIJEN = [
    (
        "periodieke-verhogingen-minimale-duur-dienstverband",
        "Ja, deze zijn afhankelijk van een minimale duur dienstverband",
        INDIVIDUAL_SALARY_INCREASE_RATE_DUUR_DIENSTVERBAND,
    ),
    (
        "periodieke-verhogingen-beoordeling-werknemer",
        "Ja, deze zijn afhankelijk van de beoordeling van de werknemer",
        INDIVIDUAL_SALARY_INCREASE_RATE_BEOORDELING_WERKNEMER,
    ),
    ("periodieke-verhogingen-ja", "Ja", INDIVIDUAL_SALARY_INCREASE_RATE_ANDERS),
    (
        "periodieke-verhogingen-andere-verhogingen",
        "Nee, maar wij geven wel andere verhogingen (niet zijnde initiële / eenmalige verhogingen) aan onze werknemers",
        INDIVIDUAL_SALARY_INCREASE_RATE_OVERIG,
    ),
]

_WERKERVARING = {
    "ja-sector": "Relevante werkervaring in de sector wordt als volgt meegenomen: ",
    "ja-onderneming": "Relevante werkervaring bij onze onderneming wordt als volgt meegenomen: ",
    "ja-functie": "Relevante werkervaring in dezelfde functie (ongeacht de sector) wordt als volgt meegenomen: ",
    "ja-als-volgt": "Relevante werkervaring wordt als volgt meegenomen: ",
}


# --- hulp
def js_tekst(waarde: Any) -> str:
    """``String(waarde)`` in JavaScript (``null`` → ``"null"``)."""
    if waarde is None:
        return "null"
    if isinstance(waarde, bool):
        return "true" if waarde else "false"
    if isinstance(waarde, float) and waarde.is_integer():
        return str(int(waarde))
    return str(waarde)


def json_kopie(waarde: Any) -> Any:
    """``JSON.parse(JSON.stringify(waarde))``: diepe kopie waarin NaN ``null`` wordt."""
    return json.loads(json.dumps(waarde), parse_constant=lambda _: None)



def _remuneration(opbouw: Opbouw, bi: int) -> dict:
    """``setuData.remuneration[bi]``; de webform loopt vast (TypeError) als die er niet is."""
    lijst = opbouw.data.get("remuneration")
    if lijst is None or bi >= len(lijst) or lijst[bi] is None:
        raise TypeError(f"setuData.remuneration[{bi}] bestaat niet (de webform loopt hier ook vast)")
    return lijst[bi]


# --- omzetters (convertSetuValue)
def _betaalde_pauzes(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    return {
        "name": "Betaalde rusttijden en pauzes",
        "typeCode": "HT400",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [
            {
                "interval": {"value": 1, "unitCode": "Hour"},
                "conditions": [
                    {
                        "conditionType": "Text",
                        "description": js_tekst(opbouw.antwoorden.get("betaalde-rusttijden-en-pauzes/ja/namelijk")),
                    }
                ],
            }
        ],
    }


def _voorwaarde(waarde: Any, opbouw: Opbouw) -> Any:
    return {"conditionType": "Text", "description": waarde} if waarde else None


def _werkduur(waarde: Any, opbouw: Opbouw) -> Any:
    if not isinstance(waarde, (int, float)) or isinstance(waarde, bool):
        return None
    return {"valuePerWeek": waarde, "amount": {"value": 1, "unitCode": "Hour"}, "interval": {"value": 1, "unitCode": "Week"}}


def _interval(waarde: Any, opbouw: Opbouw) -> Any:
    return work_duration_2_interval(waarde) if isinstance(waarde, str) else None


def _werkervaring_indicator(bi: int) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        resultaat = None if waarde == "nee" else True
        for schaal in _remuneration(opbouw, bi).get("salaryScale") or []:
            if schaal.get("careerLevel") is None:
                schaal["careerLevel"] = {}
            schaal["careerLevel"]["indicator"] = resultaat
        return resultaat

    return omzetten


def _werkervaring_toelichting(bi: int, voorvoegsel: str) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        resultaat = f"{voorvoegsel}{js_tekst(waarde)}"
        for schaal in _remuneration(opbouw, bi).get("salaryScale") or []:
            schaal["careerLevel"]["description"] = resultaat
        return resultaat

    return omzetten


def _periodieke_verhoging(bi: int, rij: str, label: str) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde != CHECKED:
            return None
        a = opbouw.antwoorden
        p = lambda achter: ["beloningen", bi, f"{rij}/{achter}"]  # noqa: E731
        anders = a.get(p("berekening/anders/namelijk")) if a.get(p("berekening")) == "anders" else None
        line: dict[str, Any] = {
            "interval": {"value": 1, "unitCode": "Year"},
            "conditions": [{"conditionType": "Text", "description": f"{label}: {js_tekst(anders)}" if anders else label}],
        }
        resultaat: dict[str, Any] = {"line": line}
        hoe = a.get(p("berekening"))
        if hoe == "vast-percentage":
            waarde = tekst(a, p("berekening/vast-percentage/namelijk"), "float")
            line["amount"] = {"value": waarde, "unitCode": "Percentage", "baseAmount": {"unitCode": "YearlyRate"}}
        elif hoe == "vast-bedrag":
            waarde = tekst(a, p("berekening/vast-bedrag/namelijk"), "float")
            line["amount"] = {"value": waarde, "unitCode": "Euro", "baseAmount": {"unitCode": "Fixed"}}
        elif hoe == "treden":
            waarde = tekst(a, p("berekening/treden/namelijk"), "float")
            line["amount"] = {"value": waarde, "unitCode": "SalaryStep", "baseAmount": {"unitCode": "Fixed"}}
        wanneer = a.get(p("wanneer"))
        if wanneer == "vast-moment":
            resultaat["effectiveDate"] = {
                "occurrenceType": "Single",
                "date": to_date_time_string(a.get(p("wanneer/vast-moment/namelijk"))),
            }
        elif wanneer == "gewerkt-jaar":
            line["conditions"].append(
                {"conditionType": "Text", "description": "Wanneer wordt de verhoging toegekend: per gewerkt jaar"}
            )
        elif wanneer == "anders":
            line["conditions"].append(
                {
                    "conditionType": "Text",
                    "description": "Wanneer wordt de verhoging toegekend: " + js_tekst(a.get(p("wanneer/anders/namelijk"))),
                }
            )
        return resultaat

    return omzetten


def _eenmalige_verhoging(bi: int) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde != "ja":
            return None
        a = opbouw.antwoorden
        p = lambda achter: ["beloningen", bi, f"initiele-eenmalige-verhogingen/ja/{achter}"]  # noqa: E731
        soort = a.get(p("type"))
        # getQuestion(".../ja/<soort in kleine letters>"): alleen "euro" en "percentage" bestaan.
        onderdeel = "undefined" if soort is None else js_tekst(soort).lower()
        bedrag = tekst(a, p(onderdeel), "float") if onderdeel in ("euro", "percentage") else None
        beschrijving = a.get(p("beschrijving"))
        return {
            "amount": {"value": bedrag, "unitCode": soort},
            "effectiveDate": {"occurrenceType": "Single", "date": to_date_time_string(a.get(p("geldig-vanaf")))},
            "description": None if beschrijving is None else js_tekst(beschrijving),
        }

    return omzetten


def _afwijkende_roosters(bi: int) -> Omzetter:
    """Elk afwijkend rooster wordt een kopie van ``remuneration[bi]`` in ``remuneration_EXTRA_RENUMERATIONS``."""

    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde == "nee":
            return None
        a = opbouw.antwoorden
        rooster = ["beloningen", bi, "afwijkende-roosters"]
        for r in range(a.rijen(rooster)):
            lijst = opbouw.data.get("remuneration")
            if lijst is None:
                raise TypeError("setuData.remuneration bestaat niet (de webform loopt hier ook vast)")
            if bi >= len(lijst) or lijst[bi] is None:
                return DONT_AUTO_SET_SETU_VALUE
            beloning = json_kopie(lijst[bi])
            if a.get(["beloningen", bi, "afwijkende-arbeidsduur"]) == "ja":
                if beloning.get("workDuration") is not None:
                    uren = to_float(a.get([*rooster, r, "arbeidsduur"]))
                    beloning["workDuration"]["valuePerWeek"] = uren
                    beloning["workDuration"]["amount"]["value"] = uren
                    per = a.get([*rooster, r, "arbeidsduur-per"])
                    if per:
                        beloning["workDuration"]["interval"] = work_duration_2_interval(per)
                if beloning.get("conditions") is None:
                    beloning["conditions"] = []
                situatie = a.get([*rooster, r, "in-situatie"])
                beloning["conditions"].append(
                    {"conditionType": "Text", "description": None if situatie is None else js_tekst(situatie)}
                )
            if a.get([*rooster, r, "uurloon-factor-vastgelegd"]) == "ja":
                if beloning.get("hourlyWageConversion") is None:
                    beloning["hourlyWageConversion"] = {}
                beloning["hourlyWageConversion"]["hourlyWagePercentage"] = to_float(a.get([*rooster, r, "uurloon-factor"]))
            opbouw.data.setdefault("remuneration_EXTRA_RENUMERATIONS", []).append(beloning)
        return DONT_AUTO_SET_SETU_VALUE

    return omzetten


# --- de vragen, in formuliervolgorde
def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    # Betaalde rusttijden en pauzes
    yield SetuVraag(
        "betaalde-rusttijden-en-pauzes",
        ["allowance", ALLOWANCE_PAID_BREAKS],
        keuze(a, "betaalde-rusttijden-en-pauzes"),
        omzetten=_betaalde_pauzes,
    )

    for bi in range(a.rijen("beloningen")):
        yield from _salaristabel(a, bi)


def _salaristabel(a: Antwoorden, bi: int) -> Iterator[SetuVraag]:
    b = ["beloningen", bi]
    r = ["remuneration", bi]

    # Geldende periodeloon in de schalen › Deze salaristabel is geldig
    yield SetuVraag([*b, "geldig-vanaf"], [*r, "effectivePeriod", "validFrom"], datum_waarde(a.get([*b, "geldig-vanaf"])))
    yield SetuVraag([*b, "geldig-per"], [*r, "effectivePeriod", "validTo"], datum_waarde(a.get([*b, "geldig-per"])))
    if bi > 0:
        yield SetuVraag(
            [*b, "voorwaarden"], [*r, "conditions", BELONING_VOORWAARDE_ANDERS], tekst(a, [*b, "voorwaarden"]), omzetten=_voorwaarde
        )

    # Normale arbeidsduur
    yield SetuVraag(
        [*b, "normale-arbeidsduur"],
        [*r, "workDuration"],
        keuze(a, [*b, "normale-arbeidsduur"], _NORMALE_ARBEIDSDUUR),
        omzetten=_werkduur,
    )
    yield SetuVraag(
        [*b, "normale-arbeidsduur-anders-namelijk"],
        [*r, "workDuration"],
        tekst(a, [*b, "normale-arbeidsduur-anders-namelijk"], "float"),
        omzetten=_werkduur,
        zichtbaar=a.heeft([*b, "normale-arbeidsduur"], ANDERS_NAMELIJK),
    )

    # Hoe is de beloning vastgesteld?
    yield SetuVraag([*b, "beloning-vastgesteld"], [*r, "interval"], keuze(a, [*b, "beloning-vastgesteld"]), omzetten=_interval)

    # Uurlonen vastgelegd (blok alleen als de beloning niet per uur is vastgesteld)
    yield SetuVraag(
        [*b, "uurlonen-vastgelegd/ja/namelijk"],
        [*r, "hourlyWageConversion", "hourlyWagePercentage"],
        tekst(a, [*b, "uurlonen-vastgelegd/ja/namelijk"], "float"),
        zichtbaar=a.heeft([*b, "uurlonen-vastgelegd"], "ja") and a.get([*b, "beloning-vastgesteld"]) != "per-uur",
    )

    # Welke salarisschalen kent de onderneming?
    for j in range(a.rijen([*b, "salarisschalen"])):
        s = [*b, "salarisschalen", j]
        sr = [*r, "salaryScale", j]
        yield SetuVraag([*s, "naam"], [*sr, "name"], tekst(a, [*s, "naam"]))
        yield SetuVraag([*s, "minimaal-bedrag"], [*sr, "minValue"], tekst(a, [*s, "minimaal-bedrag"], "float"))
        yield SetuVraag([*s, "maximaal-bedrag"], [*sr, "maxValue"], tekst(a, [*s, "maximaal-bedrag"], "float"))
        for k in range(a.rijen([*s, "stappen"])):
            st = [*s, "stappen", k]
            yield SetuVraag([*st, "naam"], [*sr, "salaryStep", k, "name"], tekst(a, [*st, "naam"]))
            yield SetuVraag([*st, "bedrag"], [*sr, "salaryStep", k, "value"], tekst(a, [*st, "bedrag"], "float"))

    # Inschaling
    werkervaring = [*b, "werkervaring-inschaling"]
    carriere = [*r, "salaryScale", 0, "careerLevel"]
    yield SetuVraag(werkervaring, [*carriere, "indicator"], keuze(a, werkervaring), omzetten=_werkervaring_indicator(bi))
    for optie, voorvoegsel in _WERKERVARING.items():
        slug = [*b, f"werkervaring-inschaling/{optie}/namelijk"]
        yield SetuVraag(
            slug,
            [*carriere, "description"],
            tekst(a, slug),
            omzetten=_werkervaring_toelichting(bi, voorvoegsel),
            zichtbaar=a.heeft(werkervaring, optie),
        )

    # Periodieken
    periodiek = a.heeft([*b, "periodieke-verhogingen"], "ja")
    for rij, label, index in _PERIODIEKE_RIJEN:
        yield SetuVraag(
            [*b, rij],
            [*r, "individualSalaryIncrease", index],
            vinkje_waarde(a.get([*b, rij])),
            omzetten=_periodieke_verhoging(bi, rij, label),
            zichtbaar=periodiek,
        )

    # Initiële / eenmalige verhogingen
    yield SetuVraag(
        [*b, "initiele-eenmalige-verhogingen"],
        [*r, "generalSalaryIncrease", 0],
        keuze(a, [*b, "initiele-eenmalige-verhogingen"]),
        omzetten=_eenmalige_verhoging(bi),
    )

    # Afwijkende roosters (setuPath DONT_AUTO_SET: schrijft alleen via remuneration_EXTRA_RENUMERATIONS)
    yield SetuVraag(
        [*b, "afwijkende-arbeidsduur"],
        [DONT_AUTO_SET_SETU_VALUE],
        keuze(a, [*b, "afwijkende-arbeidsduur"]),
        omzetten=_afwijkende_roosters(bi),
    )


__all__ = ["vragen", "js_tekst", "json_kopie"]
