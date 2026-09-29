"""06 · Vergoedingen → SETU (src/definition/06_vergoedingen_00.tsx en 06_vergoedingen_mobiliteit.tsx).

Volgorde zoals ``makeVergoedingen``: reiskosten (eigen vervoer woon-werk en werk-werk als variaties in
``allowance_EXTRA_ALLOWANCES``, dan OV, dan "andere"), reisuren, stand-by, zorgverzekering, thuiswerk (+ internet),
mobiliteit (``makeMobiliteitsvergoeding``, tussen thuiswerk en kosten) en kostenvergoedingen.

Webform-bugs die bewust worden nagedaan:
- zorgverzekering: ``convertSetuValue`` leest ``vergoeding-zorgerzekering-naar-rato`` (tikfout), dus
  ``proportional`` wordt (vrijwel) nooit gezet;
- "Anders, namelijk:" zonder tekst geeft in de naam de tekst ``null`` (JavaScript-tekstaaneenschakeling);
- stand-by "anders" en OV/eigen vervoer "anders" verliezen bedrag/interval; stand-by "anders" ook de voorwaarden;
- OV "per rit" krijgt interval ``Item`` en "volledige vergoeding" 100 % met ``baseAmount.unitCode: Fixed``.
"""

from collections.abc import Iterator
from typing import Any

from .gedeeld import (
    ALLOWANCE_ARBO_VERGOEDING,
    ALLOWANCE_BYOD_VERGOEDING,
    ALLOWANCE_FIETSREGELING,
    ALLOWANCE_INTERNETVERGOEDING,
    ALLOWANCE_KOFFIEGELD,
    ALLOWANCE_MAALTIJDVERGOEDING,
    ALLOWANCE_MOBILITEITSVERGOEDING,
    ALLOWANCE_REGELING_LEASEAUTO,
    ALLOWANCE_REGELING_LEASEFIETS,
    ALLOWANCE_REGELING_OV_VERGOEDING,
    ALLOWANCE_REISKOSTEN,
    ALLOWANCE_STANDBY,
    ALLOWANCE_THUISWERKVERGOEDING,
    ALLOWANCE_TRAVEL_HOME_WORK_OV,
    ALLOWANCE_TRAVEL_OTHER,
    ALLOWANCE_TRAVEL_WORK_WORK_OV,
    ALLOWANCE_VERGOEDING_ANDERS,
    ALLOWANCE_VERGOEDING_BEDRIJFSKLEDING_SCHOENEN,
    ALLOWANCE_WASVERGOEDING,
    ALLOWANCE_ZORGVERZEKERING,
    keuze,
    tekst,
)
from .motor import (
    ANDERS_NAMELIJK,
    CHECKED,
    DONT_AUTO_SET_SETU_VALUE,
    TODO_REPLACE_WITH_REAL_ORIGIN,
    TODO_REPLACE_WITH_REAL_TYPECODE,
    Antwoorden,
    Opbouw,
    Omzetter,
    SetuVraag,
    extra_lijst,
    is_waar,
    js_getal,
    to_float,
    vinkje_waarde,
)

_WELKE = "welke-reiskostenvergoedingen-kent-jouw-onderneming"


def _js_tekst(waarde: Any) -> str:
    """Zoals JavaScript een waarde in een tekst plakt (``"a" + null`` → ``"anull"``)."""
    if waarde is None:
        return "null"
    if isinstance(waarde, bool):
        return "true" if waarde else "false"
    if isinstance(waarde, float):
        getal = js_getal(waarde)
        return "NaN" if getal is None else str(getal)
    return str(waarde)


def _to_string(waarde: Any) -> str | None:
    """toString2: ``None`` blijft ``None``, al het andere wordt tekst."""
    return None if waarde is None else _js_tekst(waarde)


def _tekst_voorwaarde(beschrijving: Any) -> dict:
    return {"conditionType": "Text", "description": beschrijving}


def _voorwaarden_of_niets(beschrijving: Any) -> list | None:
    """``voorwaarden ? [{conditionType: "Text", description}] : undefined``."""
    return [_tekst_voorwaarde(beschrijving)] if is_waar(beschrijving) else None


# ---------------------------------------------------------------------------
# Reiskostenvergoedingen
# ---------------------------------------------------------------------------

_EIGEN_VERVOER = [
    (
        "Reiskostenvergoeding woon- werk verkeer eigen auto / fiets / bromfiets / anders.",
        f"{_WELKE}/eigen-vervoer",
        "reiskostenvergoeding-eigen-vervoer",
    ),
    (
        "Reiskostenvergoeding zakelijke kilometers (werk – werk) eigen vervoer",
        f"{_WELKE}/zakelijke-kilometers",
        "reiskostenvergoeding-zakelijke-kilometers",
    ),
]

_OV = [
    ("Reiskostenvergoeding woon- werk verkeer OV", f"{_WELKE}/ov", "reiskostenvergoeding-ov", ALLOWANCE_TRAVEL_HOME_WORK_OV),
    (
        "Reiskostenvergoeding werk-werk verkeer OV",
        f"{_WELKE}/zakelijke-kilometers-ov",
        "reiskostenvergoeding-zakelijke-kilometers-ov",
        ALLOWANCE_TRAVEL_WORK_WORK_OV,
    ),
]


def _eigen_vervoer(titel: str, prefix: str, i: int) -> Omzetter:
    """Eén variatie eigen vervoer: wordt achteraan ``allowance`` geplaatst (``allowance_EXTRA_ALLOWANCES``).

    De sub-slugs beginnen in de webform met een slash: ``[prefix, i, "/voorwaarden"]``.
    """

    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        a = opbouw.antwoorden
        soort = a.get([prefix, i, "type"])
        bedrag = None
        interval = {"value": 1, "unitCode": "Kilometer"}
        voorwaarden = _to_string(a.get([prefix, i, "/voorwaarden"]))
        conditions = _voorwaarden_of_niets(voorwaarden)
        if soort == "standaard-tarief":
            bedrag = 0.23
        if soort == "ander-tarief-per-km":
            bedrag = to_float(a.get([prefix, i, "/ander-tarief-per-km/bedrag"]))
        if soort == "per-tijdvak":
            bedrag = to_float(a.get([prefix, i, "/per-tijdvak/bedrag"]))
            interval = {"value": 1, "unitCode": a.get([prefix, i, "/per-tijdvak/type"])}
        regeling = {
            "name": titel,
            "typeCode": "EA103",
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [
                {
                    "amount": {"value": bedrag, "unitCode": "Euro", "baseAmount": {"unitCode": "Fixed"}},
                    "interval": interval,
                    "conditions": conditions,
                }
            ],
        }
        if soort == ANDERS_NAMELIJK:
            regeling = {
                "name": titel + " Anders, namelijk: " + _js_tekst(a.get([prefix, i, "/anders/namelijk"])),
                "typeCode": "EA103",
                "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
                "line": [{"conditions": conditions}],
            }
        extra_lijst(opbouw, "allowance_EXTRA_ALLOWANCES").append(regeling)
        return DONT_AUTO_SET_SETU_VALUE

    return omzetten


def _ov(titel: str, prefix: str) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        a = opbouw.antwoorden
        soort = a.get(f"{prefix}-type")
        bedrag = None
        eenheid = "Euro"
        interval = {"value": 1, "unitCode": "Kilometer"}
        conditions = _voorwaarden_of_niets(_to_string(a.get(f"{prefix}-voorwaarden")))
        if soort == ANDERS_NAMELIJK:
            return {
                "name": titel + " Anders, namelijk: " + _js_tekst(a.get(f"{prefix}-type/anders/namelijk")),
                "typeCode": "EA103",
                "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
                "line": [{"conditions": conditions}],
            }
        if soort == "volledige-vergoeding":
            bedrag = 100
            eenheid = "Percentage"
        if soort == "per-kilometer":
            bedrag = to_float(a.get(f"{prefix}-type/per-kilometer/bedrag"))
        if soort == "per-rit":
            bedrag = to_float(a.get(f"{prefix}-type/per-rit/bedrag"))
            interval = {"value": 1, "unitCode": "Item"}
        if soort == "per-traject":
            bedrag = to_float(a.get(f"{prefix}-type/per-traject/bedrag"))
            interval = {"value": 1, "unitCode": "Route"}
        return {
            "name": titel,
            "typeCode": "EA103",
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [
                {
                    "amount": {"value": bedrag, "unitCode": eenheid, "baseAmount": {"unitCode": "Fixed"}},
                    "interval": interval,
                    "conditions": conditions,
                }
            ],
        }

    return omzetten


def _andere_reiskosten(waarde: Any, opbouw: Opbouw) -> Any:
    return {
        "name": f"Andere reiskostenvergoedingen, namelijk: {_js_tekst(waarde)}",
        "typeCode": "EA103",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
    }


def _reiskosten(a: Antwoorden) -> Iterator[SetuVraag]:
    for titel, vink, prefix in _EIGEN_VERVOER:
        # makeVergoedingen vult een lege of ontbrekende lijst aan tot één lege variatie.
        for i in range(a.rijen(prefix) or 1):
            yield SetuVraag(
                [prefix, i, "type"],
                ["allowance_EXTRA_ALLOWANCES"],
                keuze(a, [prefix, i, "type"]),
                omzetten=_eigen_vervoer(titel, prefix, i),
                zichtbaar=a.heeft(vink, CHECKED),
            )
    for titel, vink, prefix, index in _OV:
        yield SetuVraag(
            f"{prefix}-type",
            ["allowance", index],
            keuze(a, f"{prefix}-type"),
            omzetten=_ov(titel, prefix),
            zichtbaar=a.heeft(vink, CHECKED),
        )
    yield SetuVraag(
        "andere-reiskostenvergoeding-namelijk",
        ["allowance", ALLOWANCE_TRAVEL_OTHER],
        tekst(a, "andere-reiskostenvergoeding-namelijk"),
        omzetten=_andere_reiskosten,
        zichtbaar=a.heeft(f"{_WELKE}/andere-reiskostenvergoeding", CHECKED),
    )


# ---------------------------------------------------------------------------
# Reisuren, stand-by, zorgverzekering
# ---------------------------------------------------------------------------


def _reisuren(waarde: Any, opbouw: Opbouw) -> Any:
    a = opbouw.antwoorden
    voorwaarden = a.get("vergoeding-reistijd_voorwaarden")
    conditions = _voorwaarden_of_niets(voorwaarden)
    basis = {"typeCode": "HT600", "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN}}
    if waarde == "percentage":
        return {
            "name": "Reisuren: percentage",
            **basis,
            "line": [
                {
                    "amount": {
                        "value": to_float(a.get("vergoeding-reistijd/percentage/percentage")),
                        "unitCode": "Percentage",
                        "baseAmount": {"unitCode": a.get("vergoeding-reistijd/percentage/van")},
                    },
                    "interval": {"value": 1, "unitCode": a.get("vergoeding-reistijd/percentage/tijdvak")},
                    "conditions": conditions,
                }
            ],
        }
    if waarde == "vaste-vergoeding":
        return {
            "name": "Reisuren: vaste vergoeding",
            **basis,
            "line": [
                {
                    "amount": {
                        "value": to_float(a.get("vergoeding-reistijd/vaste-vergoeding/value")),
                        "unitCode": "Euro",
                        "baseAmount": {"unitCode": "Fixed"},
                    },
                    "interval": {"value": 1, "unitCode": a.get("vergoeding-reistijd/vaste-vergoeding/per")},
                    "conditions": conditions,
                }
            ],
        }
    if waarde == ANDERS_NAMELIJK:
        return {
            "name": "Reisuren: " + _js_tekst(a.get("vergoeding-reistijd/anders/namelijk")),
            **basis,
            "line": [{"conditions": conditions}],
        }
    return None


_STANDBY_NAAM = "Vergoeding voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten"


def _stand_by(waarde: Any, opbouw: Opbouw) -> Any:
    a = opbouw.antwoorden
    conditions = _voorwaarden_of_niets(a.get("voorwaarden-vergoeding-stand-by"))
    basis = {"typeCode": "HT602", "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN}}
    if waarde == "vergoeding-per-tijdvak":
        return {
            "name": f"{_STANDBY_NAAM}: vergoeding per tijdvak",
            **basis,
            "line": [
                {
                    "amount": {
                        "value": to_float(a.get("type-vergoeding-stand-by/vergoeding-per-tijdvak/bedrag")),
                        "unitCode": "Euro",
                        "baseAmount": {"unitCode": "Fixed"},
                    },
                    "interval": {"value": 1, "unitCode": a.get("type-vergoeding-stand-by/vergoeding-per-tijdvak/tijdvak")},
                    "conditions": conditions,
                }
            ],
        }
    if waarde == "percentage-per-tijdvak":
        return {
            "name": f"{_STANDBY_NAAM}: percentage per tijdvak",
            **basis,
            "line": [
                {
                    "amount": {
                        "value": to_float(a.get("type-vergoeding-stand-by/percentage-per-tijdvak/percentage")),
                        "unitCode": "Percentage",
                        "baseAmount": {"unitCode": a.get("type-vergoeding-stand-by/percentage-per-tijdvak/van")},
                    },
                    "interval": {"value": 1, "unitCode": a.get("type-vergoeding-stand-by/percentage-per-tijdvak/tijdvak")},
                    "conditions": conditions,
                }
            ],
        }
    if waarde == ANDERS_NAMELIJK:
        # Webform: geen line, dus de voorwaarden gaan verloren.
        return {"name": f"{_STANDBY_NAAM}: " + _js_tekst(a.get("type-vergoeding-stand-by/anders/namelijk")), **basis}
    return None


def _zorgverzekering(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    regeling: dict[str, Any] = {
        "name": "Vergoeding voor de (aanvullende) zorgverzekering",
        "typeCode": "EA604",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [],
    }
    soort = a.get("vergoeding-zorgverzekering-type")
    if soort == "vergoeding-per-tijdseenheid":
        regel: dict[str, Any] = {
            "amount": {
                "value": to_float(a.get("vergoeding-zorgverzekering-type/vergoeding-per-tijdseenheid/bedrag")),
                "unitCode": "Euro",
                "baseAmount": {"unitCode": "Fixed"},
            },
            "interval": {"value": 1, "unitCode": a.get("vergoeding-zorgverzekering-type/vergoeding-per-tijdseenheid/tijdvak")},
            "conditions": [],
        }
        if a.get("vergoeding-zorgverzekering-min-max") == "ja":
            regel["amount"]["minValue"] = to_float(a.get("vergoeding-zorgverzekering-min-max/ja/minimum"))
            regel["amount"]["maxValue"] = to_float(a.get("vergoeding-zorgverzekering-min-max/ja/maximum"))
        # Webform-bug: tikfout in de slug ("zorgerzekering"), de vraag heet vergoeding-zorgverzekering-naar-rato.
        if a.get("vergoeding-zorgerzekering-naar-rato") == "ja":
            regel["amount"]["proportional"] = {"partTimePercentage": True, "employmentDuration": False}
        if a.ingevuld("vergoeding-zorgverzekering-voorwaarden"):
            regel["conditions"].append(_tekst_voorwaarde(_to_string(a.get("vergoeding-zorgverzekering-voorwaarden"))))
        regeling["line"].append(regel)
    if soort == ANDERS_NAMELIJK:
        regeling["name"] += " Anders, namelijk: " + _js_tekst(a.get("vergoeding-zorgverzekering-type/anders/namelijk"))
    return regeling


# ---------------------------------------------------------------------------
# Thuiswerk
# ---------------------------------------------------------------------------


def _vaste_regel(a: Antwoorden, bedrag_slug: str, naar_rato_slug: str, tijdvak_slug: str, voorwaarden_slug: str) -> dict:
    """Eén line met vast bedrag, naar rato (partTimePercentage) en tekstvoorwaarden (thuiswerk, mobiliteit, kosten)."""
    conditions = []
    if a.ingevuld(voorwaarden_slug):
        conditions.append(_tekst_voorwaarde(_to_string(a.get(voorwaarden_slug))))
    return {
        "amount": {
            "value": to_float(a.get(bedrag_slug)),
            "unitCode": "Euro",
            "baseAmount": {"unitCode": "Fixed"},
            "proportional": {"partTimePercentage": a.get(naar_rato_slug) == "ja", "employmentDuration": False},
        },
        "interval": {"value": 1, "unitCode": a.get(tijdvak_slug)},
        "conditions": conditions,
    }


def _thuiswerk(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    p = "thuiswerkvergoeding/ja"
    return {
        "name": "Thuiswerkvergoeding",
        "typeCode": "EA607" if a.get(f"{p}/internetvergoeding-inbegrepen") == "ja" else "EA605",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [_vaste_regel(a, f"{p}/vergoeding-tijdseenheid", f"{p}/naar-rato", f"{p}/tijdvak", f"{p}/voorwaarden")],
    }


def _internet(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    p = "thuiswerkvergoeding/ja/extra-internetvergoeding/ja"
    return {
        "name": "Internetvergoeding",
        "typeCode": "EA608",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
        "line": [_vaste_regel(a, f"{p}/vergoeding-tijdseenheid", f"{p}/naar-rato", f"{p}/tijdvak", f"{p}/voorwaarden")],
    }


# ---------------------------------------------------------------------------
# Mobiliteit (makeMobiliteitsvergoeding)
# ---------------------------------------------------------------------------

# (label, slug, alternatief, index); typeCode is overal TODO_REPLACE_WITH_REAL_TYPECODE.
_REGELINGEN = [
    ("Mobiliteitsvergoeding", "mobiliteitsvergoeding", False, ALLOWANCE_MOBILITEITSVERGOEDING),
    ("Regeling leaseauto", "regeling-leaseauto", True, ALLOWANCE_REGELING_LEASEAUTO),
    ("Regeling leasefiets", "regeling-leasefiets", True, ALLOWANCE_REGELING_LEASEFIETS),
    ("Regeling OV vergoeding", "regeling-ov-vergoeding", True, ALLOWANCE_REGELING_OV_VERGOEDING),
    ("Fietsregeling", "fietsregeling", False, ALLOWANCE_FIETSREGELING),
]


def _mobiliteit(label: str, slug: str) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde != CHECKED:
            return None
        a = opbouw.antwoorden
        p = f"mobiliteit/{slug}"
        regels = [_vaste_regel(a, f"{p}/bedrag", f"{p}/naar-rato", f"{p}/tijdvak", f"{p}/voorwaarden")]
        # Het alternatief wordt gelezen ongeacht of de regeling een alternatief kent (net als in de webform).
        if a.get(f"{p}/alternatief") == CHECKED:
            alternatief = _vaste_regel(
                a, f"{p}/alternatief/bedrag", f"{p}/alternatief/naar-rato", f"{p}/alternatief/tijdvak", f"{p}/alternatief/voorwaarden"
            )
            alternatief["conditions"].insert(0, _tekst_voorwaarde("Alternatieve vergoeding voor " + label))
            regels.append(alternatief)
        return {
            "name": label,
            "typeCode": TODO_REPLACE_WITH_REAL_TYPECODE,
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": regels,
        }

    return omzetten


# ---------------------------------------------------------------------------
# Kostenvergoedingen
# ---------------------------------------------------------------------------

_KOSTEN = [
    ("kostenvergoedingen/koffiegeld", "Koffiegeld", ALLOWANCE_KOFFIEGELD),
    ("kostenvergoedingen/maaltijdvergoeding", "Maaltijdvergoeding", ALLOWANCE_MAALTIJDVERGOEDING),
    ("kostenvergoedingen/wasvergoeding", "Wasvergoeding", ALLOWANCE_WASVERGOEDING),
    (
        "kostenvergoedingen/vergoeding-bedrijfskleding-schoenen",
        "Vergoeding voor bedrijfskleding of schoenen",
        ALLOWANCE_VERGOEDING_BEDRIJFSKLEDING_SCHOENEN,
    ),
    ("kostenvergoedingen/arbo-vergoeding", "Arbo-vergoeding", ALLOWANCE_ARBO_VERGOEDING),
    ("kostenvergoedingen/byod-vergoeding", "BYOD (Bring Your Own Device) vergoeding", ALLOWANCE_BYOD_VERGOEDING),
]


def _kosten(slug: str, label: str) -> Omzetter:
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde != CHECKED:
            return None
        a = opbouw.antwoorden
        regel = _vaste_regel(a, f"{slug}/per-tijdvak/bedrag", f"{slug}/naar-rato", f"{slug}/tijdvak", f"{slug}/voorwaarden")
        # Hier zonder toString2: de beschrijving is het antwoord zelf.
        for voorwaarde in regel["conditions"]:
            voorwaarde["description"] = a.get(f"{slug}/voorwaarden")
        return {"name": label, "typeCode": "EA100", "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN}, "line": [regel]}

    return omzetten


def _kosten_anders(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != CHECKED:
        return None
    return {
        "name": "Kostenvergoeding anders: " + _js_tekst(opbouw.antwoorden.get("kostenvergoedingen/anders/namelijk")),
        "typeCode": "EA100",
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
    }


# ---------------------------------------------------------------------------
# Sectie
# ---------------------------------------------------------------------------


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    yield from _reiskosten(a)

    yield SetuVraag(
        "vergoeding-reistijd", ["allowance", ALLOWANCE_REISKOSTEN], keuze(a, "vergoeding-reistijd"), omzetten=_reisuren
    )
    yield SetuVraag(
        "type-vergoeding-stand-by",
        ["allowance", ALLOWANCE_STANDBY],
        keuze(a, "type-vergoeding-stand-by"),
        omzetten=_stand_by,
        zichtbaar=a.heeft("vergoeding-stand-by-piket-consignatie-bereikbaarheidsdiensten", "ja"),
    )
    yield SetuVraag(
        "vergoeding-zorgverzekering",
        ["allowance", ALLOWANCE_ZORGVERZEKERING],
        keuze(a, "vergoeding-zorgverzekering"),
        omzetten=_zorgverzekering,
    )
    yield SetuVraag(
        "thuiswerkvergoeding", ["allowance", ALLOWANCE_THUISWERKVERGOEDING], keuze(a, "thuiswerkvergoeding"), omzetten=_thuiswerk
    )
    yield SetuVraag(
        "thuiswerkvergoeding/ja/extra-internetvergoeding",
        ["allowance", ALLOWANCE_INTERNETVERGOEDING],
        keuze(a, "thuiswerkvergoeding/ja/extra-internetvergoeding"),
        omzetten=_internet,
        zichtbaar=a.heeft("thuiswerkvergoeding", "ja") and a.heeft("thuiswerkvergoeding/ja/internetvergoeding-inbegrepen", "nee"),
    )

    for label, slug, _alternatief, index in _REGELINGEN:
        yield SetuVraag(
            f"mobiliteit/{slug}",
            ["allowance", index],
            vinkje_waarde(a.get(f"mobiliteit/{slug}")),
            omzetten=_mobiliteit(label, slug),
        )

    for slug, label, index in _KOSTEN:
        yield SetuVraag(slug, ["allowance", index], vinkje_waarde(a.get(slug)), omzetten=_kosten(slug, label))
    yield SetuVraag(
        "kostenvergoedingen/anders",
        ["allowance", ALLOWANCE_VERGOEDING_ANDERS],
        vinkje_waarde(a.get("kostenvergoedingen/anders")),
        omzetten=_kosten_anders,
    )
