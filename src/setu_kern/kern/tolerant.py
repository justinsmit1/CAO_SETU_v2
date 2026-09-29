"""Tolerant inlezen: bekende afwijkingen van het schema rechtzetten, met een melding per aanpassing.

De regels zijn gebaseerd op het officiële voorbeeld, de losse SETU-documentatie en de wijzerbelonen-webform.
Voeg nieuwe regels toe zodra echte bestanden (van wijzerbelonen, inlenersbeloning, ...) andere afwijkingen tonen.
"""

import datetime as dt
import re
from typing import Any

# Oude/afwijkende sleutelnamen → naam in het schema.
SLEUTELS = {
    "occurenceType": "occurrenceType",
    "intervalCode": "interval",
    "individualSalaryIncreaseRate": "individualSalaryIncrease",
    "generalSalaryIncreaseRate": "generalSalaryIncrease",
    "other": "otherArrangement",
    "supplementaryArrangements": "supplementaryArrangement",
    "additional parental leave": "additionalParentalLeave",
    "type_code": "typeCode",
}

# Afwijkende waarden → waarde in het schema (per sleutel).
WAARDEN = {
    "occurrenceType": {"Recuring": "Recurring", "Occurence": "Occurrence"},
    "conditionType": {"Occurence": "Occurrence", ".Text": "Text"},
    "unitCode": {"Days": "Day", "Hours": "Hour", "hour": "Hour", "day": "Day", "fixed": "Fixed", "euro": "Euro"},
}

REGELINGEN = (
    "allowance holidayAllowance sickPay leave individualChoiceBudget pension sustainableEmployability "
    "supplementaryArrangement otherArrangement positionProfile remuneration"
).split()

GETAL_SLEUTELS = {"value", "minValue", "maxValue", "valuePerWeek", "age", "hourlyWageFactor", "hourlyWagePercentage"}


def normaliseer(data: Any, pad: str = "") -> tuple[Any, list[str]]:
    """Geeft een genormaliseerde kopie van ``data`` en de lijst meldingen terug."""
    meldingen: list[str] = []
    return _loop(data, pad, meldingen), meldingen


def _loop(data: Any, pad: str, meldingen: list[str]) -> Any:
    if isinstance(data, list):
        uit = []
        for i, item in enumerate(data):
            if _is_plaatshouder(item):
                meldingen.append(f"{pad}[{i}]: plaatshouder {item!r} weggelaten")
                continue
            uit.append(_loop(item, f"{pad}[{i}]", meldingen))
        return uit
    if not isinstance(data, dict):
        return data

    uit: dict[str, Any] = {}
    for sleutel, waarde in data.items():
        nieuw = SLEUTELS.get(sleutel, sleutel)
        if nieuw != sleutel:
            meldingen.append(f"{pad}.{sleutel}: hernoemd naar '{nieuw}'")
        hier = f"{pad}.{nieuw}"

        if nieuw in WAARDEN and isinstance(waarde, str) and waarde in WAARDEN[nieuw]:
            meldingen.append(f"{hier}: '{waarde}' → '{WAARDEN[nieuw][waarde]}'")
            waarde = WAARDEN[nieuw][waarde]
        if nieuw == "typeCode" and isinstance(waarde, dict) and set(waarde) == {"value"}:
            meldingen.append(f"{hier}: {{'value': ...}} → tekst")
            waarde = waarde["value"]
        # 'value' is alleen een getal naast een unitCode (Interval, Amount); bij een Id is het tekst.
        getal = nieuw in GETAL_SLEUTELS and (nieuw != "value" or "unitCode" in data)
        if getal and isinstance(waarde, str) and re.fullmatch(r"-?\d+(\.\d+)?", waarde.strip()):
            meldingen.append(f"{hier}: tekst '{waarde}' → getal")
            waarde = float(waarde)
        if nieuw == "weekday" and isinstance(waarde, list) and any(isinstance(w, str) for w in waarde):
            meldingen.append(f"{hier}: weekdagen als tekst → {{'value': ...}}")
            waarde = [{"value": w} if isinstance(w, str) else w for w in waarde]
        uit[nieuw] = _loop(waarde, hier, meldingen)

    # Regeling zonder (verplichte) origin → Unknown, zoals de wijzerbelonen-webform ook doet
    if re.fullmatch(r"\.(%s)\[\d+\]" % "|".join(REGELINGEN), pad) and "origin" not in uit:
        meldingen.append(f"{pad}: origin ontbreekt → 'Unknown'")
        uit["origin"] = {"type": "Unknown"}

    # Single met een losse datum: het schema eist een datum mét tijd. Middernacht in de lokale tijd, zoals de
    # webform elders zelf schrijft (toDateTimeString): "2026-12-15" → "2026-12-15T00:00:00+01:00".
    datum = uit.get("date")
    if uit.get("occurrenceType") == "Single" and isinstance(datum, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", datum):
        moment = dt.datetime.fromisoformat(datum).astimezone()
        zone = moment.strftime("%z")
        uit["date"] = f"{datum}T00:00:00{zone[:3]}:{zone[3:]}"
        meldingen.append(f"{pad}: Single.date '{datum}' zonder tijd → '{uit['date']}'")

    # Recurring met 'date' i.p.v. (recurring)interval. Een losse datum wordt een jaarlijkse reeks, zoals de
    # webform zelf een peildatum schrijft: "2026-06-02" → "R/2026-06-02/P1Y".
    if uit.get("occurrenceType") == "Recurring" and "date" in uit and not ({"interval", "recurringInterval"} & set(uit)):
        datum = uit.pop("date")
        reeks = f"R/{datum}/P1Y" if isinstance(datum, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", datum) else datum
        meldingen.append(f"{pad}: Recurring.date '{datum}' → recurringInterval '{reeks}'")
        uit["recurringInterval"] = reeks
    return uit


def _is_plaatshouder(item: Any) -> bool:
    """Voorbeeld-plaatshouders zoals ``{"conditionType": "..."}``."""
    return isinstance(item, dict) and any(isinstance(v, str) and v.strip(".") == "" and v for v in item.values()) and len(item) == 1


def verwijder_op_pad(data: Any, loc: tuple) -> str | None:
    """Verwijdert het diepste lijst-element op ``loc`` (Pydantic-foutlocatie). Geeft het pad terug of None."""
    laatste_lijst = None
    obj = data
    for i, deel in enumerate(loc):
        if isinstance(obj, list) and isinstance(deel, int) and deel < len(obj):
            laatste_lijst = (obj, deel, loc[: i + 1])
            obj = obj[deel]
        elif isinstance(obj, dict) and deel in obj:
            obj = obj[deel]
        else:
            break
    if laatste_lijst is None:
        return None
    lijst, index, pad = laatste_lijst
    del lijst[index]
    return ".".join(str(p) for p in pad)
