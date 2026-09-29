"""Python-versie van ``Store.toSetuStandard()`` uit de wijzerbelonen-webform (v2.1.0).

De webform loopt alle zichtbare vragen af. Een vraag met een ``setuPath`` zet zijn antwoord (eventueel eerst
omgezet door ``convertSetuValue``) op dat pad in de SETU-JSON. Daarna volgen de extra rijen (``*_EXTRA_*``),
``clean()`` en de vaste standaardwaarden. Dit bestand bevat dat raamwerk; de vragen zelf staan per sectie in
``setu_s01_algemeen.py`` … ``setu_s16_ondertekenen.py``.

Het werkt op de *antwoorden* van de webform (``__webform_data__.answers``), net als de webform zelf. Een
``Formulier`` zet je eerst om met ``antwoorden.naar_antwoorden()``.
"""

import datetime as dt
import math
import uuid
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any

from ...setu.bericht import officieel_schema

DONT_AUTO_SET_SETU_VALUE = "DONT_AUTO_SET_SETU_VALUE"
TODO_REPLACE_WITH_REAL_ORIGIN = "Unknown"
TODO_REPLACE_WITH_REAL_CURRENCY = "EUR"
TODO_REPLACE_WITH_REAL_TYPECODE = "EA100"
CHECKED = True
ANDERS_NAMELIJK = "anders"

Pad = list[str | int]


# --- antwoorden lezen (Store.getAnswer)
class Antwoorden:
    """De antwoorden van de webform, per slug. Een slug is een tekst of een pad zoals ``["beloningen", 0, "naam"]``."""

    def __init__(self, data: dict[str, Any]):
        self.data = data

    def get(self, slug: str | Pad) -> Any:
        """Store.getAnswer: ``None`` als er niets staat."""
        pad = [slug] if isinstance(slug, str) else slug
        cur: Any = self.data
        for deel in pad:
            if isinstance(cur, dict):
                cur = cur.get(deel) if isinstance(deel, str) else None
            elif isinstance(cur, list) and isinstance(deel, int):
                cur = cur[deel] if 0 <= deel < len(cur) else None
            else:
                return None
            if cur is None:
                return None
        return cur

    def heeft(self, slug: str | Pad, antwoord: Any) -> bool:
        return self.get(slug) == antwoord

    def ingevuld(self, slug: str | Pad) -> bool:
        return is_waar(self.get(slug))

    def rijen(self, slug: str | Pad) -> int:
        """Store.countAnswerRows."""
        waarde = self.get(slug)
        return len(waarde) if isinstance(waarde, list) else 0


def is_waar(waarde: Any) -> bool:
    """JavaScript-truthiness (0, "", NaN, null en false zijn onwaar; lege lijsten/objecten zijn waar)."""
    if waarde is None or waarde is False or waarde == "":
        return False
    if isinstance(waarde, bool):
        return waarde
    if isinstance(waarde, (int, float)):
        return waarde != 0 and not (isinstance(waarde, float) and math.isnan(waarde))
    return True


# --- omzetfuncties zoals in de webform (src/definition/util*.ts, cast.ts)
def to_float(waarde: Any) -> float | None:
    """toFloat / parseFloat: leest het getal aan het begin van de tekst; None bij null, NaN als het geen getal is."""
    if waarde is None:
        return None
    return _parse_getal(waarde, float)


def to_integer(waarde: Any) -> int | None:
    if waarde is None:
        return None
    getal = _parse_getal(waarde, int)
    return None if isinstance(getal, float) and math.isnan(getal) else getal


def _parse_getal(waarde: Any, soort: type) -> Any:
    if isinstance(waarde, bool):
        return math.nan
    if isinstance(waarde, (int, float)):
        return soort(waarde) if soort is int else float(waarde)
    import re

    tekst = str(waarde).strip()
    patroon = r"[+-]?\d+" if soort is int else r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?"
    m = re.match(patroon, tekst)
    if not m:
        return math.nan
    return int(m.group(0)) if soort is int else float(m.group(0))


def js_getal(waarde: float | None) -> int | float | None:
    """Een JavaScript-getal: 8.0 wordt 8 (zo schrijft JSON.stringify het ook)."""
    if waarde is None or (isinstance(waarde, float) and math.isnan(waarde)):
        return None
    if isinstance(waarde, float) and waarde.is_integer():
        return int(waarde)
    return waarde


def naar_datum(waarde: Any) -> dt.datetime | None:
    """Een datum-antwoord van de webform (milliseconden sinds 1970, lokale tijd) → datetime."""
    if not waarde:
        return None
    if isinstance(waarde, (int, float)):
        return dt.datetime.fromtimestamp(waarde / 1000).astimezone()
    if isinstance(waarde, str):
        return dt.datetime.fromisoformat(waarde.replace("Z", "+00:00")).astimezone()
    raise TypeError(f"onbekend datumformaat: {waarde!r}")


def to_date_string(waarde: Any) -> str | None:
    """toDateString: ``yyyy-MM-dd``."""
    moment = naar_datum(waarde)
    return moment.strftime("%Y-%m-%d") if moment else None


def to_date_time_string(waarde: Any) -> str | None:
    """toDateTimeString: ``yyyy-MM-dd'T'HH:mm:ssxxx`` (met tijdzone, bijv. ``+02:00``)."""
    moment = naar_datum(waarde)
    if not moment:
        return None
    zone = moment.strftime("%z")
    return moment.strftime("%Y-%m-%dT%H:%M:%S") + f"{zone[:3]}:{zone[3:]}"


def time_to_date_string(waarde: Any) -> str | None:
    return f"1970-01-01T{waarde}:00" if waarde else None


def time_to_time_string(waarde: Any) -> str | None:
    return f"{waarde}:00" if waarde else None


# --- de vragen
Omzetter = Callable[[Any, "Opbouw"], Any]


@dataclass
class SetuVraag:
    """Eén vraag met een ``setuPath`` (in dezelfde volgorde als ``store.allQuestions``).

    - ``waarde``: ``question.getSetuValue()``, dus het antwoord na de standaardomzetting van het vraagtype
      (tekst → getal bij ``restrictTo``, datum → ``yyyy-MM-dd``, radio/checkbox → ``setuValue`` van de optie).
    - ``zichtbaar``: ``question.isShown``; standaard waar. Alleen nodig bij vragen die ook zonder antwoord
      worden omgezet (``omzetten_bij_leeg``) of waarvan het antwoord verborgen kan zijn.
    """

    slug: str | Pad
    setu_pad: Pad
    waarde: Any
    omzetten: Omzetter | None = None
    omzetten_bij_leeg: bool = False  # shouldConvertNullSetuValue
    zichtbaar: bool = True


@dataclass
class Opbouw:
    """Het ``setuData``-object tijdens het opbouwen, plus de antwoorden (``store``)."""

    antwoorden: Antwoorden
    data: dict[str, Any] = field(default_factory=dict)


def zet_op_pad(data: dict, pad: Pad, waarde: Any) -> None:
    """Store.setuSetAtPath: maakt objecten en lijsten aan volgens het SETU-schema en zet de waarde."""
    if waarde == DONT_AUTO_SET_SETU_VALUE:
        return
    if not pad:
        raise ValueError("pad van lengte 0")
    schema = _schema_node(None)
    cur: Any = data
    for sleutel in pad[:-1]:
        if isinstance(sleutel, str):
            if not isinstance(cur, dict) or schema.get("type") != "object":
                raise ValueError(f"ongeldig pad: verwacht een object bij {sleutel!r} in {pad}")
            schema = _schema_node(schema["properties"][sleutel])
            if sleutel not in cur:
                cur[sleutel] = _container(schema, pad)
            cur = cur[sleutel]
        else:
            if not isinstance(cur, list) or schema.get("type") != "array":
                raise ValueError(f"ongeldig pad: verwacht een lijst bij {sleutel} in {pad}")
            schema = _schema_node(schema["items"])
            while len(cur) <= sleutel:
                cur.append(_container(schema, pad))
            if cur[sleutel] is None:
                cur[sleutel] = _container(schema, pad)
            cur = cur[sleutel]
    laatste = pad[-1]
    if isinstance(laatste, str):
        if schema.get("type") != "object" or laatste not in schema.get("properties", {}):
            raise ValueError(f'ongeldig pad: verwacht een object bij de laatste sleutel "{laatste}" in {pad}')
        cur[laatste] = waarde
    else:
        if schema.get("type") != "array":
            raise ValueError(f"ongeldig pad: verwacht een lijst bij de laatste sleutel in {pad}")
        while len(cur) <= laatste:
            cur.append(None)  # JS: een gat in de array (undefined)
        cur[laatste] = waarde


def _schema_node(node: dict | None) -> dict:
    """Lost ``$ref`` op (resolveJsonSchemaRefs); None = de wortel van het schema."""
    root = officieel_schema()
    node = root if node is None else node
    while "$ref" in node:
        naam = node["$ref"].rsplit("/", 1)[-1]
        node = {**root["definitions"][naam], **{k: v for k, v in node.items() if k != "$ref"}}
    return node


def _container(schema: dict, pad: Pad) -> dict | list:
    if schema.get("type") == "object":
        return {}
    if schema.get("type") == "array":
        return []
    raise ValueError(f"onbekend schematype {schema.get('type')!r} bij {pad}")


def is_leeg(item: Any) -> bool:
    """Store.isEmpty: null/undefined, of een object/lijst met alleen lege onderdelen."""
    if item is None:
        return True
    if isinstance(item, dict):
        return all(is_leeg(v) for v in item.values())
    if isinstance(item, list):
        return all(is_leeg(v) for v in item)
    return False


def schoon(obj: Any) -> None:
    """Store.clean: verwijdert lege onderdelen (en daardoor ook de vaste indexen van lege posities)."""
    if isinstance(obj, dict):
        for sleutel in list(obj):
            if is_leeg(obj[sleutel]):
                del obj[sleutel]
            else:
                schoon(obj[sleutel])
    elif isinstance(obj, list):
        for i in range(len(obj) - 1, -1, -1):
            if is_leeg(obj[i]):
                del obj[i]
            else:
                schoon(obj[i])


def extra_lijst(opbouw: Opbouw, naam: str) -> list:
    """``setuData.<naam>_EXTRA_...``: rijen die na de vaste posities worden toegevoegd."""
    return opbouw.data.setdefault(naam, [])


_EXTRA = [
    ("allowance_EXTRA_ALLOWANCES", "allowance"),
    ("remuneration_EXTRA_RENUMERATIONS", "remuneration"),
    ("leave_EXTRA_LEAVES", "leave"),
    ("other_EXTRA_OTHERS", "otherArrangement"),
]


def naar_setu_json(
    antwoorden: dict[str, Any],
    secties: Iterable[Callable[[Antwoorden], Iterator[SetuVraag]]],
    document_id: str | None = None,
    issued: dt.datetime | None = None,
) -> dict[str, Any]:
    """Store.toSetuStandard. ``secties`` levert per sectie de vragen met een setuPath, in formuliervolgorde."""
    opbouw = Opbouw(Antwoorden(antwoorden))
    data = opbouw.data
    data["leave"] = [{}]
    data["documentId"] = {"value": document_id or str(uuid.uuid4()), "schemeAgencyId": "Customer"}
    moment = (issued or dt.datetime.now(dt.UTC)).astimezone(dt.UTC)  # new Date().toISOString()
    data["issued"] = moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    for sectie in secties:
        for vraag in sectie(opbouw.antwoorden):
            if not vraag.zichtbaar:
                continue
            waarde = vraag.waarde
            if vraag.omzetten and (is_waar(waarde) or vraag.omzetten_bij_leeg):
                waarde = vraag.omzetten(waarde, opbouw)
            if waarde is not None and waarde != "" and vraag.setu_pad[0] != DONT_AUTO_SET_SETU_VALUE:
                zet_op_pad(data, vraag.setu_pad, waarde)

    for extra, doel in _EXTRA:
        if extra in data:
            data.setdefault(doel, []).extend(data.pop(extra))
    schoon(data)
    _vul_standaardwaarden(data)
    return als_json(data)


def als_json(obj: Any) -> Any:
    """Zoals JSON.stringify het zou schrijven: 8.0 → 8, NaN → null (en daarna weggelaten waar JS dat ook doet)."""
    if isinstance(obj, dict):
        return {k: als_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [als_json(v) for v in obj]
    if isinstance(obj, float):
        return js_getal(obj)
    return obj


def _vul_standaardwaarden(data: dict) -> None:
    """Store.addMissingDefaults."""
    for beloning in data.get("remuneration", []):
        beloning.setdefault("origin", {"type": TODO_REPLACE_WITH_REAL_ORIGIN})
        for schaal in beloning.get("salaryScale", []):
            schaal.setdefault("currency", TODO_REPLACE_WITH_REAL_CURRENCY)
    for profiel in data.get("positionProfile", []):
        profiel.setdefault("origin", {"type": TODO_REPLACE_WITH_REAL_ORIGIN})


# --- hulp bij het omzetten van vraagtypes (getSetuValue)
def tekst_waarde(antwoord: Any, restrict_to: str | None = None) -> Any:
    """TextQuestion.getSetuValue."""
    if restrict_to == "integer" and antwoord is not None and antwoord != "":
        return to_integer(antwoord)
    if restrict_to == "float" and antwoord is not None and antwoord != "":
        return js_getal(to_float(antwoord))
    if antwoord == "":
        return None
    return antwoord


def datum_waarde(antwoord: Any) -> str | None:
    """DateQuestion.getSetuValue."""
    return to_date_string(antwoord)


def tijd_waarde(antwoord: Any) -> str | None:
    """TimeQuestion.getSetuValue."""
    return time_to_date_string(antwoord)


def keuze_waarde(antwoord: Any, setu_waarden: dict[str, Any] | None = None) -> Any:
    """RadioQuestion.getSetuValue: de ``setuValue`` van de gekozen optie, anders het antwoord zelf."""
    if setu_waarden and antwoord in setu_waarden:
        return setu_waarden[antwoord]
    return antwoord


def vinkje_waarde(antwoord: Any, setu_waarde: Any = None) -> Any:
    """CheckboxQuestion.getSetuValue."""
    return setu_waarde if setu_waarde is not None and is_waar(antwoord) else antwoord
