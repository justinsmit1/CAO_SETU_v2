"""07 · Bijzondere uitkeringen → SETU (src/definition/07_bijzondere-uitkeringen.tsx).

Elke subsectie heeft één ja/nee-vraag met ``setuPath: [DONT_AUTO_SET_SETU_VALUE]``. Bij ``ja`` maakt
``convertSetuValue`` per variatie een allowance en zet die in ``allowance_EXTRA_ALLOWANCES``. De omzetting leest de
antwoorden rechtstreeks (``store.getAnswer``), dus ook antwoorden van vragen die verborgen zijn.

Nagedaan gedrag van de webform (niet verbeterd):
- Een ontbrekende naam wordt ``"null"`` in de naam (``"Eenmalige uitkering: " + null``).
- ``min-max = ja`` zonder bedrag (hoe-toegekend leeg of ``anders``) laat de export vastlopen
  (``line.amount.minValue`` op ``undefined``); hier een ``TypeError``. Geldt voor eenmalige en variabele uitkeringen.
- Eenmalig: de regel (``line``) komt alleen in de allowance als er een voorwaarde of een bedrag is.
- Jubileum ``anders``: de regel wordt vervangen, waardoor de eerder toegevoegde voorwaarden (o.a. de
  dienstverbandduur) wegvallen.
- De opties ``ander-percentage`` en de vragen ``min-max`` (vast) en ``voorwaarden/...`` (jubileum) bestaan niet in
  het formulier; de code ervoor is wel overgenomen.
"""

from collections.abc import Iterator
from typing import Any

from .gedeeld import keuze
from .motor import (
    ANDERS_NAMELIJK,
    DONT_AUTO_SET_SETU_VALUE,
    TODO_REPLACE_WITH_REAL_ORIGIN,
    Antwoorden,
    Opbouw,
    SetuVraag,
    extra_lijst,
    js_getal,
    to_date_string,
    to_float,
)

_DATUM_TEKST = "Afhankelijk van dienstverband op bepaalde datum, namelijk: "


# --- JavaScript-tekstomzetting
def _js(waarde: Any) -> str:
    """``String(waarde)`` zoals in ``"tekst" + waarde`` en template literals: null → "null"."""
    if waarde is None:
        return "null"
    if waarde is True:
        return "true"
    if waarde is False:
        return "false"
    if isinstance(waarde, float):
        getal = js_getal(waarde)
        return "NaN" if getal is None else str(getal)
    return str(waarde)


def _to_string(waarde: Any) -> str | None:
    """``waarde?.toString()``: null blijft undefined (en valt weg)."""
    return None if waarde is None else _js(waarde)


def _tekst_voorwaarde(beschrijving: str | None) -> dict:
    return {"conditionType": "Text", "description": beschrijving}


def _geen_bedrag() -> TypeError:
    return TypeError("Cannot set properties of undefined (setting 'minValue')")


def _min_max(a: Antwoorden, rij: list, line: dict) -> None:
    if a.get([*rij, "min-max"]) == "ja":
        if "amount" not in line:
            raise _geen_bedrag()  # de webform loopt hier vast
        line["amount"]["minValue"] = to_float(a.get([*rij, "min-max/ja/minimum"]))
        line["amount"]["maxValue"] = to_float(a.get([*rij, "min-max/ja/maximum"]))


def _percentage(a: Antwoorden, rij: list) -> dict:
    return {
        "value": to_float(a.get([*rij, "type_ander-percentage_percentage"])),
        "unitCode": "Percentage",
        "baseAmount": {"unitCode": a.get([*rij, "type_ander-percentage_van"])},
    }


def _vast_bedrag(a: Antwoorden, rij: list) -> dict:
    return {"value": to_float(a.get([*rij, "vast-bedrag_namelijk"])), "unitCode": "Euro", "baseAmount": {"unitCode": "Fixed"}}


def _ander_percentage(a: Antwoorden, rij: list) -> dict:
    return {
        "value": to_float(a.get([*rij, "type_ander-percentage_percentage"])),
        "unitCode": "Percentage",
        "baseAmount": {"unitCode": "Fixed"},
    }


def _uitkeringsmoment(a: Antwoorden, rij: list, allowance: dict) -> None:
    if a.get([*rij, "toekenning-datum"]):
        allowance["payDate"] = {"occurrenceType": "Single", "date": to_date_string(a.get([*rij, "toekenning-datum"]))}


# --- Eenmalige uitkeringen
def _eenmalige_uitkeringen(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    for i in range(a.rijen("eenmalige-uitkeringen")):
        rij = ["eenmalige-uitkeringen", i]
        line: dict[str, Any] = {"interval": {"value": 1, "unitCode": "Once"}, "conditions": []}
        allowance: dict[str, Any] = {
            "name": "Eenmalige uitkering: " + _js(a.get([*rij, "namelijk"])),
            "typeCode": "EA801",
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [],
        }

        def neem_op() -> None:  # if (!allowance.line.includes(line)) allowance.line.push(line)
            if not any(r is line for r in allowance["line"]):
                allowance["line"].append(line)

        if a.get([*rij, "voorwaarden/min-duur-dienstverband"]):
            line["conditions"].append(_tekst_voorwaarde(_to_string(a.get([*rij, "voorwaarden_min-duur_namelijk"]))))
            neem_op()
        if a.get([*rij, "voorwaarden/dienstverband-op-datum"]):
            line["conditions"].append(
                _tekst_voorwaarde(_DATUM_TEKST + _js(a.get([*rij, "voorwaarden_dienstverband-datum_namelijk"])))
            )
            neem_op()
        if a.get([*rij, "voorwaarden/anders"]):
            line["conditions"].append(_tekst_voorwaarde(_to_string(a.get([*rij, "voorwaarden_anders_namelijk"]))))
            neem_op()
        _uitkeringsmoment(a, rij, allowance)
        hoe_toegekend = a.get([*rij, "hoe-toegekend"])
        if hoe_toegekend == ANDERS_NAMELIJK:
            allowance["name"] += ": " + _js(a.get([*rij, "anders"]))
        if hoe_toegekend == "percentage-loon":
            line["amount"] = _percentage(a, rij)
            neem_op()
        elif hoe_toegekend == "vast-bedrag":
            line["amount"] = _vast_bedrag(a, rij)
            neem_op()
        deeltijd = a.get([*rij, "naar-rato-deeltijd"]) == "ja"
        duur = a.get([*rij, "naar-rato-duur-dienstverband"]) == "ja"
        if (deeltijd or duur) and "amount" in line:
            line["amount"]["proportional"] = {"partTimePercentage": deeltijd, "employmentDuration": duur}
            neem_op()
        _min_max(a, rij, line)
        extra_lijst(opbouw, "allowance_EXTRA_ALLOWANCES").append(allowance)
    return DONT_AUTO_SET_SETU_VALUE


# --- Vaste (onvoorwaardelijke) uitkeringen
def _vaste_uitkeringen(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    for i in range(a.rijen("vaste-uitkeringen")):
        rij = ["vaste-uitkeringen", i]
        line: dict[str, Any] = {"interval": {"value": 1, "unitCode": "Year"}, "conditions": []}
        allowance: dict[str, Any] = {
            "name": "Vaste uitkering: " + _js(a.get([*rij, "namelijk"])),
            "typeCode": "EA801",
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [line],
        }
        if a.get([*rij, "voorwaarden/min-duur-dienstverband"]):
            line["conditions"].append(_tekst_voorwaarde(_to_string(a.get([*rij, "voorwaarden_min-duur_namelijk"]))))
        if a.get([*rij, "voorwaarden/dienstverband-op-datum"]):
            line["conditions"].append(
                _tekst_voorwaarde(_DATUM_TEKST + _js(a.get([*rij, "voorwaarden_dienstverband-datum_namelijk"])))
            )
        if a.get([*rij, "voorwaarden/anders"]):
            line["conditions"].append(_tekst_voorwaarde(_to_string(a.get([*rij, "voorwaarden_anders_namelijk"]))))
        _uitkeringsmoment(a, rij, allowance)
        hoe_toegekend = a.get([*rij, "hoe-toegekend"])
        if hoe_toegekend == "dertiende-maand":
            line["amount"] = {"value": 100, "unitCode": "Percentage", "baseAmount": {"unitCode": "MonthlyRate"}}
        elif hoe_toegekend == "percentage-loon":
            line["amount"] = _percentage(a, rij)
        elif hoe_toegekend == "vast-bedrag":
            line["amount"] = _vast_bedrag(a, rij)
        elif hoe_toegekend == "ander-percentage":  # geen optie in het formulier
            line["amount"] = _ander_percentage(a, rij)
        elif hoe_toegekend == ANDERS_NAMELIJK:
            allowance["name"] += ": " + _js(a.get([*rij, "anders"]))
        if a.get([*rij, "naar-rato"]) == "ja" and "amount" in line:
            line["amount"]["proportional"] = {"partTimePercentage": True, "employmentDuration": False}
        _min_max(a, rij, line)  # geen vraag in het formulier
        extra_lijst(opbouw, "allowance_EXTRA_ALLOWANCES").append(allowance)
    return DONT_AUTO_SET_SETU_VALUE


# --- Jubileumuitkering
def _jubileumuitkeringen(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    for i in range(a.rijen("jubileumuitkeringen")):
        rij = ["jubileumuitkeringen", i]
        line: dict[str, Any] = {"conditions": []}
        allowance: dict[str, Any] = {
            "name": f"Jubileumuitkering: {_js(a.get([*rij, 'namelijk']))}",
            "typeCode": "EA903",
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [line],
        }
        # Deze twee vragen bestaan niet in de jubileum-subsectie.
        if a.get([*rij, "voorwaarden/min-duur-dienstverband"]):
            line["conditions"].append(_tekst_voorwaarde(_to_string(a.get([*rij, "voorwaarden_min-duur_namelijk"]))))
        if a.get([*rij, "voorwaarden/dienstverband-op-datum"]):
            line["conditions"].append(
                _tekst_voorwaarde(_DATUM_TEKST + _js(a.get([*rij, "voorwaarden_dienstverband-datum_namelijk"])))
            )
        _uitkeringsmoment(a, rij, allowance)
        jaren = to_float(a.get([*rij, "dienstverband-duur/jaren"]))
        maanden = to_float(a.get([*rij, "dienstverband-duur/maanden"]))
        if _waar_getal(jaren) or _waar_getal(maanden):
            duur = "P"
            if _waar_getal(jaren):
                duur += f"{_js(jaren)}Y"
            if _waar_getal(maanden):
                duur += f"{_js(maanden)}M"
            line["conditions"].append(
                {
                    "conditionType": "EmploymentDuration",
                    "operator": "eq",
                    "duration": duur,
                    "referenceDateType": a.get([*rij, "dienstverband-duur/referentiedatum"]),
                }
            )
        hoe_toegekend = a.get([*rij, "hoe-toegekend"])
        if hoe_toegekend == "percentage-loon":
            line["amount"] = _percentage(a, rij)
        elif hoe_toegekend == "vast-bedrag":
            line["amount"] = _vast_bedrag(a, rij)
        elif hoe_toegekend == ANDERS_NAMELIJK:
            # De webform vervangt de regel: de voorwaarden hierboven vallen weg.
            allowance["line"] = [
                {"conditions": [_tekst_voorwaarde(f"Anders toegekend, namelijk: {_js(a.get([*rij, 'anders']))}")]}
            ]
        if a.get([*rij, "naar-rato"]) == "ja" and "amount" in line:
            line["amount"]["proportional"] = {"partTimePercentage": True, "employmentDuration": False}
        if a.get([*rij, "voorwaarden"]):
            allowance["line"][0]["conditions"].append(_tekst_voorwaarde(_to_string(a.get([*rij, "voorwaarden"]))))
        extra_lijst(opbouw, "allowance_EXTRA_ALLOWANCES").append(allowance)
    return DONT_AUTO_SET_SETU_VALUE


def _waar_getal(getal: float | None) -> bool:
    """``if (getal)``: 0, NaN en undefined zijn onwaar."""
    return getal is not None and getal == getal and getal != 0


# --- Variabele (voorwaardelijke) uitkeringen
_VARIABELE_VOORWAARDEN = [
    ("voorwaarden/prestatie", "voorwaarden_prestatie_namelijk", "Bepaalde prestatie (performance), namelijk: "),
    ("voorwaarden/resultaat", "voorwaarden_resultaat_namelijk", "Bepaald resultaat (winst), namelijk: "),
    ("voorwaarden/min-duur-dienstverband", "voorwaarden_min-duur_namelijk", "Afhankelijk minimale duur dienstverband, namelijk: "),
    ("voorwaarden/dienstverband-op-datum", "voorwaarden_dienstverband-datum_namelijk", _DATUM_TEKST),
    ("voorwaarden/anders", "voorwaarden_anders_namelijk", "Anders, namelijk: "),
]


def _variabele_uitkeringen(waarde: Any, opbouw: Opbouw) -> Any:
    if waarde != "ja":
        return None
    a = opbouw.antwoorden
    for i in range(a.rijen("variabele-uitkeringen")):
        rij = ["variabele-uitkeringen", i]
        soort = a.get([*rij, "soort"])
        soort_naam = a.get([*rij, "soort_anders_namelijk"]) if soort == ANDERS_NAMELIJK else soort
        line: dict[str, Any] = {"interval": {"value": 1, "unitCode": "Month"}, "conditions": []}
        allowance: dict[str, Any] = {
            "name": f"Variabele uitkering: {_js(soort_naam)}",
            "typeCode": "EA903",
            "origin": {"type": TODO_REPLACE_WITH_REAL_ORIGIN},
            "line": [line],
        }
        for vinkje, toelichting, tekst in _VARIABELE_VOORWAARDEN:
            if a.get([*rij, vinkje]):
                line["conditions"].append(_tekst_voorwaarde(tekst + _js(a.get([*rij, toelichting]))))
        _uitkeringsmoment(a, rij, allowance)
        hoe_toegekend = a.get([*rij, "hoe-toegekend"])
        if hoe_toegekend == "percentage-loon":
            line["amount"] = _percentage(a, rij)
        elif hoe_toegekend == "vast-bedrag":
            line["amount"] = _vast_bedrag(a, rij)
        elif hoe_toegekend == "ander-percentage":  # geen optie in het formulier
            line["amount"] = _ander_percentage(a, rij)
        elif hoe_toegekend == ANDERS_NAMELIJK:
            allowance["name"] += ": " + _js(a.get([*rij, "anders"]))
        if a.get([*rij, "naar-rato"]) == "ja" and "amount" in line:
            line["amount"]["proportional"] = {"partTimePercentage": True, "employmentDuration": False}
        _min_max(a, rij, line)
        extra_lijst(opbouw, "allowance_EXTRA_ALLOWANCES").append(allowance)
    return DONT_AUTO_SET_SETU_VALUE


def vragen(a: Antwoorden) -> Iterator[SetuVraag]:
    yield SetuVraag(
        "eenmalige-uitkeringen-bekend",
        [DONT_AUTO_SET_SETU_VALUE],
        keuze(a, "eenmalige-uitkeringen-bekend"),
        omzetten=_eenmalige_uitkeringen,
    )
    yield SetuVraag(
        "vaste-uitkering-van-toepassing",
        [DONT_AUTO_SET_SETU_VALUE],
        keuze(a, "vaste-uitkering-van-toepassing"),
        omzetten=_vaste_uitkeringen,
    )
    yield SetuVraag(
        "jubileumuitkering-van-toepassing",
        [DONT_AUTO_SET_SETU_VALUE],
        keuze(a, "jubileumuitkering-van-toepassing"),
        omzetten=_jubileumuitkeringen,
    )
    yield SetuVraag(
        "variabele-uitkering-van-toepassing",
        [DONT_AUTO_SET_SETU_VALUE],
        keuze(a, "variabele-uitkering-van-toepassing"),
        omzetten=_variabele_uitkeringen,
    )
