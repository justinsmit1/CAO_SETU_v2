"""04 · Toeslagen → SETU (src/definition/04_toeslagen.tsx).

Alleen de checkboxes "Welke toeslagen kent jouw organisatie?" (``<toeslag>/enabled``) hebben een setuPath
(``allowance_EXTRA_ALLOWANCES``). Hun ``convertSetuValue`` zet per variatie van die toeslag één ``allowance`` in
de extra rijen en geeft ``DONT_AUTO_SET_SETU_VALUE`` terug. De vragen van de variaties zelf hebben geen setuPath;
die worden alleen daar (rechtstreeks uit de antwoorden, zonder zichtbaarheidscontrole) gelezen.
"""

import datetime as dt
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from .gedeeld import (
    ALLOWANCE_ONREGELMATIGHEIDS_TOESLAGEN,
    ALLOWANCE_OVERWERK_TOESLAG,
    ALLOWANCE_PERFORMANCETOESLAG,
    ALLOWANCE_PLOEGETOESLAGEN,
    ALLOWANCE_TOESLAGEN_ANDERS,
    ALLOWANCE_TOESLAGEN_FYSIEKE_BELAS,
    ALLOWANCE_TOESLAGEN_STANDBY,
    ALLOWANCE_TOESLAGEN_VERSCHOVEN_DIENSTEN,
    ALLOWANCE_WAARNEMINGSTOESLAG,
    get_line_amount_answer,
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
    to_date_string,
    vinkje_waarde,
)


@dataclass(frozen=True)
class _ToeslagRij:
    """Eén rij uit ``makeToeslagRows`` (alleen wat de omzetting nodig heeft)."""

    label: str
    slug: str
    index: int  # staat in de webform, maar wordt niet gebruikt: de toeslagen gaan naar de extra rijen
    type_code: str
    show_name_input: bool = False


_TOESLAG_RIJEN = [
    _ToeslagRij(
        "Onregelmatigheids- toeslagen (waaronder feestdagen)",
        "onregelmatigheids-toeslagen",
        ALLOWANCE_ONREGELMATIGHEIDS_TOESLAGEN,
        "HT320",
    ),
    _ToeslagRij("Ploegentoeslagen", "ploegentoeslagen", ALLOWANCE_PLOEGETOESLAGEN, "HT300"),
    _ToeslagRij(
        "Toeslagen voor verschoven diensten", "toeslagen-verschoven-diensten", ALLOWANCE_TOESLAGEN_VERSCHOVEN_DIENSTEN, "HT101"
    ),
    _ToeslagRij(
        "Toeslagen voor (fysieke) belasting", "toeslagen-fysieke-belasting", ALLOWANCE_TOESLAGEN_FYSIEKE_BELAS, "EA301"
    ),
    _ToeslagRij(
        # Let op: "bereik- baarheidsdiensten" (met spatie) staat zo in de webform en komt zo in ``name``.
        "Toeslagen voor werken tijdens stand-by-, consignatie- of bereik- baarheidsdiensten",
        "toeslagen-stand-by-consignatie-bereikbaarheidsdiensten",
        ALLOWANCE_TOESLAGEN_STANDBY,
        "HT602",
    ),
    _ToeslagRij("Overwerk", "overwerktoeslag", ALLOWANCE_OVERWERK_TOESLAG, "HT200"),
    # Waarnemings-, performance- en overige toeslagen delen typeCode EA300 (zo in de webform).
    _ToeslagRij("Waarnemingstoeslag", "waarnemingstoeslag", ALLOWANCE_WAARNEMINGSTOESLAG, "EA300"),
    _ToeslagRij("Performancetoeslag", "performancetoeslag", ALLOWANCE_PERFORMANCETOESLAG, "EA300"),
    _ToeslagRij("Anders", "anders", ALLOWANCE_TOESLAGEN_ANDERS, "EA300", show_name_input=True),
]

_WEEKDAGEN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# --- hulpfuncties (util.ts)
def _req_string(waarde: Any) -> str:
    """reqString: ``String(waarde)``, of ``""`` bij null."""
    return "" if waarde is None else _js_string(waarde)


def _js_string(waarde: Any) -> str:
    if waarde is True:
        return "true"
    if waarde is False:
        return "false"
    return str(waarde)


def _time_to_time_string(waarde: Any) -> str | None:
    """timeToTimeString: ``"HH:MM"`` → ``"HH:MM:00"``; een ongeldige tijd geeft (net als date-fns) niets."""
    if not waarde:
        return None
    try:
        return dt.datetime.fromisoformat(f"1970-01-01T{waarde}:00").strftime("%H:%M:%S")
    except (TypeError, ValueError):
        return None


# --- de omzetting (convertSetuValue van de checkbox "<toeslag>/enabled")
def _periode(a: Antwoorden, rij: list, j: int) -> dict[str, Any]:
    p = [*rij, "toepassingsperiodes", j]
    starttijd = a.get([*p, "starttijd"])
    eindtijd = a.get([*p, "eindtijd"])
    return {
        "datePeriod": [
            {"start": to_date_string(a.get([*p, "startdatum"])), "end": to_date_string(a.get([*p, "einddatum"]))}
        ],
        "timePeriod": {
            "start": _time_to_time_string("00:00" if starttijd is None else starttijd),
            "end": _time_to_time_string("23:59" if eindtijd is None else eindtijd),
        },
        "weekday": [{"value": dag} for dag in _WEEKDAGEN if a.ingevuld([*p, f"weekdagen/{dag}"])],
    }


def _toeslag(toeslag: _ToeslagRij, a: Antwoorden, i: int) -> dict[str, Any]:
    rij = [toeslag.slug, i]
    line = get_line_amount_answer(a, rij)
    line["conditions"] = []
    omschrijving = a.get([*rij, "description"])
    allowance: dict[str, Any] = {
        "name": _req_string(a.get([*rij, "name"])) if toeslag.show_name_input else toeslag.label,
        "description": None if omschrijving is None else _js_string(omschrijving),
        "typeCode": toeslag.type_code,
        "line": [line],
        "reference": [],
        "period": [],
        "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
    }
    if a.ingevuld([*rij, "voorwaarden"]):
        line["conditions"].append({"conditionType": "Text", "description": _req_string(a.get([*rij, "voorwaarden"]))})

    cumulatief = a.get([*rij, "cumulatief"])
    if cumulatief == "ja-cumulative":
        # Alle andere aangevinkte toeslagen, ongeacht welke; de toelichting komt in elke verwijzing.
        for ander in _TOESLAG_RIJEN:
            if not a.ingevuld(f"{ander.slug}/enabled") or ander.slug == toeslag.slug:
                continue
            toelichting = a.get([*rij, "cumulatief/ja-cumulative/namelijk"])
            allowance["reference"].append(
                {
                    "relationType": "Cumulative",
                    "description": "Deze toeslag wordt opgeteld bij de andere toeslag, zie typeCode."
                    + (f" (Toelichting: {_js_string(toelichting)})" if is_waar(toelichting) else ""),
                    "typeCode": ander.type_code,
                }
            )
    elif cumulatief == "ja-compounding":
        for ander in _TOESLAG_RIJEN:
            if a.ingevuld([*rij, f"compounding/{ander.slug}"]) and a.ingevuld(f"{ander.slug}/enabled"):
                allowance["reference"].append(
                    {
                        "relationType": "Compounding",
                        "description": "Deze toeslag wordt berekend over het resultaat na andere toeslagen, namelijk:",
                        "typeCode": ander.type_code,
                    }
                )

    # Toepassingsperiodes en afbouwregeling worden gelezen zonder te kijken of het blok zichtbaar is.
    if a.get([*rij, "toepassingsperiodes-type"]) == "bepaald":
        for j in range(a.rijen([*rij, "toepassingsperiodes"])):
            allowance["period"].append(_periode(a, rij, j))
    if a.get([*rij, "afbouwregeling"]) == "ja":
        allowance["phaseOutScheme"] = _req_string(a.get([*rij, "afbouwregeling/ja-namelijk"]))
    return allowance


def _omzetter(toeslag: _ToeslagRij):
    def omzetten(waarde: Any, opbouw: Opbouw) -> Any:
        if waarde != CHECKED:  # JS: value != CHECKED
            return None
        for i in range(opbouw.antwoorden.rijen(toeslag.slug)):
            extra_lijst(opbouw, "allowance_EXTRA_ALLOWANCES").append(_toeslag(toeslag, opbouw.antwoorden, i))
        return DONT_AUTO_SET_SETU_VALUE

    return omzetten


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    for toeslag in _TOESLAG_RIJEN:
        slug = f"{toeslag.slug}/enabled"
        yield SetuVraag(slug, ["allowance_EXTRA_ALLOWANCES"], vinkje_waarde(a.get(slug)), omzetten=_omzetter(toeslag))
