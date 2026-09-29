"""09 · Verlof → SETU (src/definition/09_verlof.tsx).

Bekende bugs van de webform die hier bewust worden nagedaan (zie docs/formulier/09_verlof.md):
- ADV "anders": het tekstveld heet ``adv-aanvullende-anders-namelijk``, de conversie leest
  ``adv-aanvullende-anders_namelijk``; de naam eindigt dus altijd op ``null``;
- extra vakantiedagen per duur dienstverband: ``age: …?.valueOf`` (zonder haakjes) is een functie en valt bij
  JSON-serialisatie weg; bij leeftijd blijft ``age`` de tekst van het antwoord (geen getal);
- lege antwoorden in samengestelde teksten worden ``null`` (JavaScript-template met Store.getAnswer = null).
"""

from collections.abc import Iterator
from typing import Any

from .gedeeld import (
    ALLOWANCE_TIJD_VOOR_TIJD,
    LEAVE_ADV,
    LEAVE_ADV_AANVULLING_ANDERS,
    LEAVE_ADV_AANVULLING_DUUR_DIENSTVERBAND,
    LEAVE_ADV_AANVULLING_OUDEREN,
    LEAVE_FEESTDAGEN,
    LEAVE_PERSOONLIJKE_FEESTDAGEN,
    LEAVE_VAKANTIE,
    LEAVE_VERPLICHT,
    LEAVE_WAARDE_VERLOFDAG,
    LEAVE_WAZO_ANDERS,
    LEAVE_WAZO_BETAALD_OUDERSCHAPSVERLOF,
    LEAVE_WAZO_GEBOORTEVERLOF,
    LEAVE_WAZO_KORTDUREND_ZORGVERLOF,
    LEAVE_WAZO_LANGDUREND_ZORGVERLOF,
    LEAVE_WAZO_LANGE_VERLOFDUUR,
    LEAVE_WAZO_ONBETAALD_OUDERSCHAPSVERLOF,
    base_amount_unit_code_to_interval,
    keuze,
    tekst,
)
from .motor import (
    CHECKED,
    DONT_AUTO_SET_SETU_VALUE,
    TODO_REPLACE_WITH_REAL_ORIGIN,
    Antwoorden,
    Opbouw,
    SetuVraag,
    extra_lijst,
    is_waar,
    to_float,
    vinkje_waarde,
)

_ORIGIN = {"type": TODO_REPLACE_WITH_REAL_ORIGIN}


def _js(waarde: Any) -> str:
    """Een waarde in een JavaScript-template (``${...}``). Store.getAnswer geeft ``null`` bij een leeg antwoord."""
    if waarde is None:
        return "null"
    if isinstance(waarde, bool):
        return "true" if waarde else "false"
    return str(waarde)


def _origin() -> dict:
    return dict(_ORIGIN)


# --- ADV / ATV
def _setu_adv(a: Antwoorden, prefix: str) -> dict:
    """setuAdv: één WorkingHoursReduction uit een toekenningsblok (makeAdvToegekend)."""
    adv: dict[str, Any] = {}
    soort = a.get(f"{prefix}/toekenning")
    if soort == "tijd-dagen":
        adv["amount"] = {
            "value": to_float(a.get(f"{prefix}/toekenning/tijd-dagen/aantal")),
            "unitCode": "Day",
            "baseAmount": {"unitCode": "Fixed"},
        }
        adv["interval"] = {"value": 1, "unitCode": a.get(f"{prefix}/toekenning/tijd-dagen/tijdvak")}
    elif soort == "tijd-uren":
        adv["amount"] = {
            "value": to_float(a.get(f"{prefix}/toekenning/tijd-uren/aantal")),
            "unitCode": "Hour",
            "baseAmount": {"unitCode": "Fixed"},
        }
        adv["interval"] = {"value": 1, "unitCode": a.get(f"{prefix}/toekenning/tijd-uren/tijdvak")}
    elif soort == "geld":
        van = a.get(f"{prefix}/toekenning/geld/van")
        adv["amount"] = {
            "value": to_float(a.get(f"{prefix}/toekenning/geld/percentage")),
            "unitCode": "Percentage",
            "baseAmount": {"unitCode": van},
        }
        adv["interval"] = {"value": 1, "unitCode": base_amount_unit_code_to_interval(van)}
        if van == "percentageFixedAmount":  # komt in het formulier niet voor (geen optie)
            adv["amount"]["baseAmount"]["value"] = to_float(a.get(f"{prefix}/toekenning/geld/van/percentage/amount"))
            adv["interval"]["unitCode"] = a.get(f"{prefix}/toekenning/geld/van/percentage/tijdvak")
    return adv


def _adv_regeling(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    return {
        "name": f"ADV / ATV regeling: {_js(a.get('adv-regeling_ja_namelijk'))}",
        "origin": _origin(),
        "workingHoursReduction": [_setu_adv(a, "adv-regeling")],
    }


def _adv_aanvulling(prefix: str, omschrijving: str, namelijk_slug: str):
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde is not CHECKED:
            return None
        a = opbouw.antwoorden
        return {
            "name": f"Aanvullende ADV / ATV regeling voor {omschrijving}: {_js(a.get(namelijk_slug))}",
            "origin": _origin(),
            "workingHoursReduction": [_setu_adv(a, prefix)],
        }

    return omzetten


_ADV_AANVULLINGEN = [
    ("adv-aanvullende-ouderen", LEAVE_ADV_AANVULLING_OUDEREN, "ouderen", "adv-aanvullende-ouderen_namelijk"),
    (
        "adv-aanvullende-duur-dienstverband",
        LEAVE_ADV_AANVULLING_DUUR_DIENSTVERBAND,
        "duur dienstverband",
        "adv-aanvullende-duur-dienstverband_namelijk",
    ),
    # bug: het tekstveld heet "adv-aanvullende-anders-namelijk"
    ("adv-aanvullende-anders", LEAVE_ADV_AANVULLING_ANDERS, "anders", "adv-aanvullende-anders_namelijk"),
]


# --- vakantiedagen
def _vakantiedagen(waarde: Any, opbouw: Opbouw) -> Any:
    a = opbouw.antwoorden
    tijdvak = a.get("vakantiedagen/tijdvak")
    betaald: list[dict] = [
        {
            "amount": {
                "value": to_float(a.get("vakantiedagen/aantal")),
                "unitCode": a.get("vakantiedagen/type"),
                "baseAmount": {"unitCode": "Fixed"},
            },
            "interval": {"value": 1, "unitCode": tijdvak},
            "conditions": [],
        }
    ]
    if a.get("extra-vakantiedagen-specifiek/dagen-leeftijd") == CHECKED:
        for i in range(a.rijen("extra-vakantiedagen/leeftijd")):
            rij = ["extra-vakantiedagen/leeftijd", i]
            betaald.append(
                {
                    "amount": {"value": to_float(a.get([*rij, "dagen"])), "unitCode": "Day", "baseAmount": {"unitCode": "Fixed"}},
                    "interval": {"value": 1, "unitCode": tijdvak},
                    # valueOf() op het tekstantwoord: de leeftijd blijft tekst
                    "conditions": [{"conditionType": "Age", "operator": "gte", "age": a.get([*rij, "leeftijd"])}],
                }
            )
    if a.get("extra-vakantiedagen-specifiek/duur-dienstverband") == CHECKED:
        for i in range(a.rijen("extra-vakantiedagen/duur-dienstverband")):
            rij = ["extra-vakantiedagen/duur-dienstverband", i]
            betaald.append(
                {
                    "amount": {"value": to_float(a.get([*rij, "dagen"])), "unitCode": "Day", "baseAmount": {"unitCode": "Fixed"}},
                    "interval": {"value": 1, "unitCode": tijdvak},
                    # bug: ``age: …?.valueOf`` is een functie en valt bij JSON.stringify weg
                    "conditions": [{"conditionType": "EmploymentDuration", "operator": "gte"}],
                }
            )
    if a.get("extra-vakantiedagen-specifiek/anders") == CHECKED:
        for i in range(a.rijen("extra-vakantiedagen/anders")):
            rij = ["extra-vakantiedagen/anders", i]
            betaald.append(
                {
                    "amount": {
                        "value": to_float(a.get([*rij, "dagen"])),
                        "unitCode": a.get("vakantiedagen/type"),
                        "baseAmount": {"unitCode": "Fixed"},
                    },
                    "interval": {"value": 1, "unitCode": tijdvak},
                    "conditions": [
                        {
                            "conditionType": "Text",
                            "description": f"Totaal extra aantal vakantiedagen voor: {_js(a.get([*rij, 'namelijk']))}",
                        }
                    ],
                }
            )
    return {"name": "Vakantiedagen", "origin": _origin(), "paidLeave": betaald}


# --- bijzonder verlof
_HOEVEEL = {"Day": "dagen", "Week": "weken", "Month": "maanden", "Year": "jaren", "Hour": "uren"}


def _bijzonder_verlof(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    for i in range(a.rijen("bijzonder-verlof")):
        rij = ["bijzonder-verlof", i]
        wat = a.get([*rij, "wat"])
        hoeveel = _HOEVEEL.get(wat, "dagen") if isinstance(wat, str) else "dagen"
        voorwaarden = _js(a.get([*rij, "voorwaarden"]))
        verlof = {
            "name": f"Bijzonder verlof: {_js(a.get([*rij, 'hoeveel']))} {hoeveel} in het geval van: {voorwaarden}",
            "origin": _origin(),
            "specialLeave": [
                {
                    "amount": {
                        "value": to_float(a.get([*rij, "hoeveel"])),
                        "unitCode": "Hour" if wat == "Hour" else "Day",
                        "baseAmount": {"unitCode": "Fixed"},
                    },
                    "interval": {"value": 1, "unitCode": wat},
                    "conditions": [{"conditionType": "Text", "description": voorwaarden}],
                }
            ],
        }
        extra_lijst(opbouw, "leave_EXTRA_LEAVES").append(verlof)
    return DONT_AUTO_SET_SETU_VALUE


# --- tijd voor tijd
def _tijd_voor_tijd(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    return {
        "name": "Tijd voor tijd regeling: " + _js(opbouw.antwoorden.get("tijd-voor-tijd/ja/namelijk")),
        "typeCode": "HT500",
        "origin": _origin(),
    }


# --- Wazo
_WAZO_RIJEN = [
    ("Een aanvulling op het betaalde ouderschapsverlof van", "wazo/betaald-ouderschapsverlof", LEAVE_WAZO_BETAALD_OUDERSCHAPSVERLOF),
    (
        "Een aanvulling op het onbetaalde ouderschapsverlof van",
        "wazo/onbetaald-ouderschapsverlof",
        LEAVE_WAZO_ONBETAALD_OUDERSCHAPSVERLOF,
    ),
    ("Een aanvulling op het aanvullend geboorteverlof", "wazo/geboorteverlof", LEAVE_WAZO_GEBOORTEVERLOF),
    ("Een aanvulling op het kortdurend zorgverlof", "wazo/kortdurend-zorgverlof", LEAVE_WAZO_KORTDUREND_ZORGVERLOF),
    ("Een tegemoetkoming bij langdurend zorgverlof", "wazo/langdurend-zorgverlof", LEAVE_WAZO_LANGDUREND_ZORGVERLOF),
    ("Een langere verlofduur:", "wazo/langere-verlofduur", LEAVE_WAZO_LANGE_VERLOFDUUR),
    ("Anders, namelijk:", "wazo/anders", LEAVE_WAZO_ANDERS),
]


def _wazo(label: str, slug: str):
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde is not CHECKED:
            return None
        return {
            "name": f"Wazo aanvulling: {label}",
            "origin": _origin(),
            "additionalParentalLeave": [
                {
                    "amount": {"value": 0, "unitCode": "Day", "baseAmount": {"unitCode": "Fixed"}},
                    "interval": {"value": 1, "unitCode": "Year"},
                    "name": f"Namelijk: {_js(opbouw.antwoorden.get(slug + '/namelijk'))}",
                }
            ],
        }

    return omzetten


# --- verplichte aanwending
def _verplicht(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    return {
        "name": "Verplichte aanwending verlof",
        "origin": _origin(),
        "mandatoryLeaveAllocation": {
            "description": "Periode/dagen/uren:"
            + _js(a.get("verplichte-aanwending-verlof/ja/periode-dagen-uren"))
            + "\n\nWelk verlof:"
            + _js(a.get("verplichte-aanwending-verlof_welk-verlof"))
        },
    }


# --- feestdagen
def _namenlijst(welke: str) -> str:
    """``welke.trim().split("\\n").map(item => item.trim()).join(", ")``."""
    return ", ".join(regel.strip() for regel in welke.strip().split("\n"))


def _feestdagen(waarde: Any, opbouw: Opbouw) -> Any:
    a = opbouw.antwoorden
    feestdag: dict[str, Any] = {
        "amount": {"value": to_float(waarde), "unitCode": "Day", "baseAmount": {"unitCode": "Fixed"}},
        "interval": {"value": 1, "unitCode": "Year"},
        "conditions": [],
    }
    verlof = {"name": "Feestdagen", "origin": _origin(), "holidays": [feestdag]}
    welke = a.get("welke-feestdagen")
    if isinstance(welke, str):
        feestdag["name"] = _namenlijst(welke)
    if is_waar(a.get("voorwaarden-feestdagen")):
        feestdag["conditions"].append(
            {
                "conditionType": "Text",
                "description": f"Voorwaarden voor het genieten van een feestdag: {_js(a.get('voorwaarden-feestdagen'))}",
            }
        )
    if a.get("feestdagen-niet-elk-jaar") == "ja":
        feestdag["conditions"].append(
            {
                "conditionType": "Text",
                "description": "Feestdagen die niet elk jaar worden toegekend, en hun voorwaarden: "
                + _js(a.get("feestdagen-niet-elk-jaar_voorwaarden")),
            }
        )
    return verlof


def _persoonlijke_feestdagen(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    feestdag: dict[str, Any] = {
        "amount": {
            "value": to_float(a.get("persoonlijke-feestdagen/aantal")),
            "unitCode": "Day",
            "baseAmount": {"unitCode": "Fixed"},
        },
        "interval": {"value": 1, "unitCode": "Year"},
        "conditions": [],
    }
    verlof = {"name": "Persoonlijke feestdagen", "origin": _origin(), "holidays": [feestdag]}
    welke = a.get("persoonlijke-feestdagen/namelijk")
    if isinstance(welke, str):
        feestdag["name"] = _namenlijst(welke)
    if is_waar(a.get("persoonlijke-feestdagen/voorwaarden")):
        feestdag["conditions"].append(
            {
                "conditionType": "Text",
                "description": "Voorwaarden voor het genieten van een persoonlijke feestdag: "
                + _js(a.get("persoonlijke-feestdagen/voorwaarden")),
            }
        )
    return verlof


# --- waarde verlofdag
def _waarde_verlofdag(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    return {
        "name": "Waarde van een (verlof)dag",
        "origin": _origin(),
        "paidLeave": [
            {
                "amount": {"value": 0, "unitCode": "Day", "baseAmount": {"unitCode": "Fixed"}},
                "interval": {"value": 1, "unitCode": "Year"},
                "leaveDayValue": {
                    "value": to_float(opbouw.antwoorden.get("waarde-verlofdag_ja_percentage")),
                    "unitCode": "Percentage",
                    "baseAmount": {"unitCode": "DailyRate"},
                },
            }
        ],
    }


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    # ADV of ATV in tijd of in geld
    yield SetuVraag("adv-regeling", ["leave", LEAVE_ADV], keuze(a, "adv-regeling"), omzetten=_adv_regeling)
    aanvullend = a.heeft("adv-aanvullende-regeling", "ja")
    for slug, index, omschrijving, namelijk in _ADV_AANVULLINGEN:
        yield SetuVraag(
            slug,
            ["leave", index],
            vinkje_waarde(a.get(slug)),
            omzetten=_adv_aanvulling(slug, omschrijving, namelijk),
            zichtbaar=aanvullend,
        )

    # Vakantiedagen
    yield SetuVraag("vakantiedagen/aantal", ["leave", LEAVE_VAKANTIE], tekst(a, "vakantiedagen/aantal", "float"), omzetten=_vakantiedagen)

    # Bijzonder verlof (rijen gaan naar leave_EXTRA_LEAVES)
    yield SetuVraag(
        "bijzonder-verlof-aanwezig", [DONT_AUTO_SET_SETU_VALUE], keuze(a, "bijzonder-verlof-aanwezig"), omzetten=_bijzonder_verlof
    )

    # Tijd voor tijd
    yield SetuVraag("tijd-voor-tijd", ["allowance", ALLOWANCE_TIJD_VOOR_TIJD], keuze(a, "tijd-voor-tijd"), omzetten=_tijd_voor_tijd)

    # Aanvulling Wazo
    wazo = a.heeft("wazo-aanvulling", "ja")
    for label, slug, index in _WAZO_RIJEN:
        yield SetuVraag(slug, ["leave", index], vinkje_waarde(a.get(slug)), omzetten=_wazo(label, slug), zichtbaar=wazo)

    # Verplichte aanwending verlof
    yield SetuVraag(
        "verplichte-aanwending-verlof", ["leave", LEAVE_VERPLICHT], keuze(a, "verplichte-aanwending-verlof"), omzetten=_verplicht
    )

    # Feestdagen
    yield SetuVraag("aantal-feestdagen", ["leave", LEAVE_FEESTDAGEN], tekst(a, "aantal-feestdagen", "float"), omzetten=_feestdagen)
    yield SetuVraag(
        "persoonlijke-feestdagen",
        ["leave", LEAVE_PERSOONLIJKE_FEESTDAGEN],
        keuze(a, "persoonlijke-feestdagen"),
        omzetten=_persoonlijke_feestdagen,
    )

    # Waarde van een (verlof)dag
    yield SetuVraag("waarde-verlofdag", ["leave", LEAVE_WAARDE_VERLOFDAG], keuze(a, "waarde-verlofdag"), omzetten=_waarde_verlofdag)
