"""Adapter wijzerbelonen ↔ kern.

    van_formulier(formulier)      Formulier (in Python ingevuld)        → Resultaat
    van_export("download.json")   download van wijzerbelonen.nl         → Resultaat
    schrijf_upload(formulier, p)  Formulier → bestand om te importeren op wijzerbelonen.nl

Een download bevat de SETU-JSON én ``__webform_data__`` (de antwoorden). Net als de import van de tool zelf gaan we uit
van de antwoorden: daaruit maakt de gekopieerde webformlogica opnieuw de SETU, zodat een download en een Formulier met
dezelfde antwoorden hetzelfde bericht opleveren. Een bestand met alleen SETU wordt rechtstreeks (tolerant) ingelezen.

Op weg naar de kern vult de adapter aan wat SETU verplicht stelt, telkens met een melding:
- geen contactpersoon met naam → ``STANDAARD_CONTACTPERSOON``;
- extra vakantiedagen per duur dienstverband: de webform laat ``duration`` en ``referenceDateType`` weg (bug). De duur
  komt uit het antwoord (``jaar`` → ``P10Y``); de referentiedatum vraagt het formulier niet →
  ``STANDAARD_REFERENTIEDATUM``.
De gekopieerde webformlogica zelf blijft ongewijzigd (die bootst de tool exact na, ook voor het uploadbestand).
"""

import copy
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ...kern import InquiryPayEquity
from ...kern.codes import ReferenceDateType
from .. import Resultaat
from .formulier import Formulier
from .formulier.formulier import WEBFORM_APP_VERSION
from .koppeling import naar_setu
from .koppeling.antwoorden import LOCAL_STORAGE_DATA_VERSION, naar_antwoorden

BRON_FORMULIER = "wijzerbelonen:formulier"
BRON_EXPORT = "wijzerbelonen:export"
BRON_SETU = "wijzerbelonen:setu"

STANDAARD_CONTACTPERSOON = "John Doe"
STANDAARD_REFERENTIEDATUM = ReferenceDateType.HIRE_DATE

_DUUR_DIENSTVERBAND = "extra-vakantiedagen/duur-dienstverband"


def van_formulier(formulier: Formulier) -> Resultaat:
    """Het kernmodel van een ingevuld Formulier (``ValueError`` als SETU-verplichte onderdelen ontbreken)."""
    bericht, meldingen = _kernmodel(naar_antwoorden(formulier))
    return Resultaat(bericht, meldingen, BRON_FORMULIER)


def van_export(bron: str | Path | dict[str, Any]) -> Resultaat:
    """Het kernmodel van een download van wijzerbelonen.nl (pad, JSON-tekst of dict)."""
    data = _laad(bron)
    webform_data = data.get("__webform_data__")
    if isinstance(webform_data, dict) and isinstance(webform_data.get("answers"), dict):
        meldingen = _versie_meldingen(webform_data)
        bericht, omzet_meldingen = _kernmodel(webform_data["answers"])
        return Resultaat(bericht, meldingen + omzet_meldingen, BRON_EXPORT)
    bericht, meldingen = InquiryPayEquity.lees_tolerant(data)
    meldingen.insert(0, "geen __webform_data__ in het bestand: alleen het SETU-deel is ingelezen")
    return Resultaat(bericht, meldingen, BRON_SETU)


def schrijf_upload(formulier: Formulier, pad: str | Path) -> list[str]:
    """Schrijft het uploadbestand voor wijzerbelonen.nl; geeft de SETU-problemen terug (de upload werkt ook met fouten)."""
    return naar_setu.schrijf_export(formulier, pad)


def _kernmodel(antwoorden: dict[str, Any]) -> tuple[InquiryPayEquity, list[str]]:
    """Antwoorden → webform-SETU → aanvullen → kern (streng, anders tolerant). Zoals ``naar_setu.kernmodel``, plus
    het aanvullen, en bij een fout eerst wat het tegenhoudt."""
    antwoorden = copy.deepcopy(antwoorden)
    meldingen = _vul_contactpersoon_aan(antwoorden)
    data = naar_setu.setu_json(antwoorden)
    meldingen += _herstel_duur_dienstverband(data, antwoorden)
    try:
        return InquiryPayEquity.lees(data), meldingen
    except ValidationError:
        pass
    try:
        bericht, tolerant = InquiryPayEquity.lees_tolerant(data)
    except ValidationError as fout:
        raise ValueError(_verplicht_fout(fout)) from fout
    return bericht, meldingen + tolerant


def _vul_contactpersoon_aan(antwoorden: dict[str, Any]) -> list[str]:
    contactpersonen = antwoorden.get("contactpersonen") or []
    if any(isinstance(c, dict) and c.get("naam") for c in contactpersonen):
        return []
    antwoorden["contactpersonen"] = [{"naam": STANDAARD_CONTACTPERSOON}]
    return [f"geen contactpersoon met naam (Ondertekenen): '{STANDAARD_CONTACTPERSOON}' ingevuld"]


def _herstel_duur_dienstverband(data: dict[str, Any], antwoorden: dict[str, Any]) -> list[str]:
    """Vult de lege EmploymentDuration-condities van de extra vakantiedagen aan, in de volgorde van de antwoordrijen."""
    rijen = antwoorden.get(_DUUR_DIENSTVERBAND) or []
    kapot = [
        (f"leave.{i}.paidLeave.{j}.conditions.{k}", conditie)
        for i, verlof in enumerate(data.get("leave") or [])
        for j, regel in enumerate(verlof.get("paidLeave") or [])
        for k, conditie in enumerate(regel.get("conditions") or [])
        if conditie.get("conditionType") == "EmploymentDuration" and "duration" not in conditie
    ]
    meldingen = []
    for (pad, conditie), rij in zip(kapot, rijen):
        jaar = rij.get("jaar") if isinstance(rij, dict) else None
        try:
            jaren = float(jaar)
        except (TypeError, ValueError):
            continue  # geen bruikbare duur: de conditie blijft ongeldig en valt tolerant weg, met een melding
        conditie["duration"] = f"P{int(jaren) if jaren.is_integer() else jaren}Y"
        conditie.setdefault("referenceDateType", STANDAARD_REFERENTIEDATUM.value)
        meldingen.append(
            f"{pad}: duur dienstverband '{conditie['duration']}' uit de antwoorden (ontbreekt in de webform-SETU); "
            f"referenceDateType '{conditie['referenceDateType']}' aangenomen (vraagt het formulier niet)"
        )
    return meldingen


def _verplicht_fout(fout: ValidationError) -> str:
    """Eerst de SETU-verplichte onderdelen die het bericht tegenhouden, daarna wat verder niet klopt."""
    blokkeert, verder = set(), set()
    for e in fout.errors():
        pad = ".".join(str(d) for d in e["loc"] if not isinstance(d, int))
        verplicht = any(pad == s or pad.startswith(s + ".") for s in naar_setu.VERPLICHT_VOOR_SETU)
        (blokkeert if verplicht else verder).add(naar_setu._verplicht_label(e["loc"]))
    tekst = "Het SETU-kernmodel kan niet gemaakt worden; SETU vereist nog:\n" + "\n".join(
        f"- {o}" for o in sorted(blokkeert)
    )
    if verder:
        tekst += "\nVerder klopt nog niet (valt bij tolerant inlezen weg, met een melding):\n" + "\n".join(
            f"- {o}" for o in sorted(verder)
        )
    return tekst


def _versie_meldingen(webform_data: dict[str, Any]) -> list[str]:
    meldingen = []
    versie = webform_data.get("localStorageDataVersion")
    if versie != LOCAL_STORAGE_DATA_VERSION:
        meldingen.append(
            f"__webform_data__.localStorageDataVersion is {versie!r}, verwacht {LOCAL_STORAGE_DATA_VERSION}: "
            "de antwoorden kunnen anders zijn opgebouwd"
        )
    app = webform_data.get("appVersion")
    if app != WEBFORM_APP_VERSION:
        meldingen.append(f"export van webform-versie {app!r}; deze koppeling volgt versie {WEBFORM_APP_VERSION}")
    return meldingen


def _laad(bron: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(bron, dict):
        return copy.deepcopy(bron)
    if isinstance(bron, Path) or not bron.lstrip().startswith("{"):
        return json.loads(Path(bron).read_text(encoding="utf-8"))
    return json.loads(bron)
