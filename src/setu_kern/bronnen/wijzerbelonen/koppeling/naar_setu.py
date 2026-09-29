"""Formulier → SETU-JSON en een uploadbestand voor wijzerbelonen.nl.

    from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu

    data = naar_setu.setu_json(formulier)            # SETU-JSON, precies zoals de webform hem exporteert
    fouten = naar_setu.valideer(data)                # [] = geldig volgens het officiële SETU-schema
    bericht = naar_setu.setu_bericht(formulier)      # als InquiryPayEquity (SETU-kernmodel), alleen als geldig
    bericht, meldingen = naar_setu.kernmodel(formulier)  # altijd een InquiryPayEquity (zo nodig tolerant)
    naar_setu.schrijf_export(formulier, "upload.json")   # SETU-JSON + __webform_data__: te importeren in de tool

Let op: de import van wijzerbelonen leest alléén ``__webform_data__`` (de antwoorden); de SETU-inhoud van het
bestand wordt bij importeren genegeerd. Het SETU-deel is voor andere afnemers (bijv. het uitzendbureau).
"""

import datetime as dt
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ..formulier import Formulier
from ....kern import InquiryPayEquity, valideer_json
from . import (
    setu_s01_algemeen,
    setu_s02_beloning,
    setu_s03_functiegroepen,
    setu_s04_toeslagen,
    setu_s05_vakantiebijslag,
    setu_s06_vergoedingen,
    setu_s07_bijzondere_uitkeringen,
    setu_s08_loondoorbetaling_bij_ziekte,
    setu_s09_verlof,
    setu_s10_individueel_keuzebudget,
    setu_s11_pensioen,
    setu_s12_duurzaam_werken_en_leven,
    setu_s13_aanvullende_regelingen,
    setu_s14_overig,
    setu_s15_grondslagen,
    setu_s16_ondertekenen,
)
from .antwoorden import naar_antwoorden, webform_data
from .motor import naar_setu_json

# Dezelfde volgorde als makeSectionDefs in de webform.
SECTIES = [
    setu_s01_algemeen.vragen,
    setu_s02_beloning.vragen,
    setu_s03_functiegroepen.vragen,
    setu_s04_toeslagen.vragen,
    setu_s05_vakantiebijslag.vragen,
    setu_s06_vergoedingen.vragen,
    setu_s07_bijzondere_uitkeringen.vragen,
    setu_s08_loondoorbetaling_bij_ziekte.vragen,
    setu_s09_verlof.vragen,
    setu_s10_individueel_keuzebudget.vragen,
    setu_s11_pensioen.vragen,
    setu_s12_duurzaam_werken_en_leven.vragen,
    setu_s13_aanvullende_regelingen.vragen,
    setu_s14_overig.vragen,
    setu_s15_grondslagen.vragen,
    setu_s16_ondertekenen.vragen,
]


def setu_json(bron: Formulier | dict[str, Any], issued: dt.datetime | None = None) -> dict[str, Any]:
    """De SETU-JSON zoals de webform hem van deze antwoorden zou maken.

    ``bron`` is een ``Formulier`` of de antwoorden van de webform zelf (``__webform_data__["answers"]``).
    Zonder naam/nummer van de regeling (Algemeen) krijgt ``documentId`` een willekeurige uuid, net als in de tool.
    """
    antwoorden = naar_antwoorden(bron) if isinstance(bron, Formulier) else bron
    return naar_setu_json(antwoorden, SECTIES, issued=issued)


def valideer(data: dict[str, Any]) -> list[str]:
    """Fouten ten opzichte van het officiële SETU-schema (lege lijst = geldig)."""
    return valideer_json({k: v for k, v in data.items() if k != "__webform_data__"})


def setu_bericht(bron: Formulier | dict[str, Any]) -> InquiryPayEquity:
    """Als SETU-kernmodel. Geeft een ValidationError als de SETU-JSON niet aan het schema voldoet."""
    return InquiryPayEquity.lees(setu_json(bron))


def kernmodel(bron: Formulier | dict[str, Any]) -> tuple[InquiryPayEquity, list[str]]:
    """Het SETU-kernmodel van dit formulier, plus meldingen.

    Voldoet de SETU-JSON van de webform aan het schema, dan wordt hij streng ingelezen en is de lijst meldingen
    leeg. Anders wordt hij tolerant ingelezen: bekende afwijkingen worden rechtgezet en ongeldige onderdelen
    weggelaten, met een melding per aanpassing. Het resultaat is een ``InquiryPayEquity``, bijvoorbeeld om te
    vergelijken met SETU uit andere formulieren.

    Zonder de onderdelen die SETU verplicht stelt (zie ``VERPLICHT_VOOR_SETU``) kan er geen kernmodel bestaan; dan
    volgt een ``ValueError`` met de formuliervragen die nog ingevuld moeten worden.
    """
    data = setu_json(bron)
    try:
        return InquiryPayEquity.lees(data), []
    except ValidationError:
        pass
    try:
        return InquiryPayEquity.lees_tolerant(data)
    except ValidationError as fout:
        ontbreekt = sorted({_verplicht_label(e["loc"]) for e in fout.errors()})
        raise ValueError(
            "Het SETU-kernmodel kan niet gemaakt worden; SETU vereist nog:\n" + "\n".join(f"- {o}" for o in ontbreekt)
        ) from fout


# Onderdelen die het SETU-schema verplicht stelt, met de formuliervraag die ze vult.
VERPLICHT_VOOR_SETU = {
    "effectivePeriod": "Algemeen › Geldig van",
    "customer": "Algemeen › Naam onderneming",
    "customer.legalId": "Algemeen › KvK- of ander identificatienummer, met het type",
    "customer.personContacts": "Ondertekenen › een contactpersoon met naam",
    "remuneration": "Beloning › een salaristabel met de normale arbeidsduur en hoe de beloning is vastgesteld",
}


def _verplicht_label(loc: tuple) -> str:
    pad = ".".join(str(d) for d in loc if not isinstance(d, int))
    for sleutel in sorted(VERPLICHT_VOOR_SETU, key=len, reverse=True):
        if pad == sleutel or pad.startswith(sleutel + "."):
            return VERPLICHT_VOOR_SETU[sleutel]
    return pad


def export(formulier: Formulier, moment: dt.datetime | None = None) -> dict[str, Any]:
    """Het complete exportbestand: SETU-JSON plus ``__webform_data__`` (zoals ``downloadSetuJson()``).

    In een paar gevallen loopt ook de echte webform vast bij het maken van de SETU-JSON (bijv. een min/max zonder
    bedrag bij een eenmalige uitkering). Dan bevat het bestand alleen ``__webform_data__`` en een ``error`` (zoals
    ``store.setuStandard`` in de tool); importeren in wijzerbelonen werkt dan nog steeds.
    """
    moment = moment or dt.datetime.now().astimezone()
    try:
        data = setu_json(formulier, issued=moment)
    except (TypeError, ValueError, KeyError, AttributeError) as fout:
        data = {"error": f"SETU-JSON kon niet worden gemaakt: {fout}"}
    data["__webform_data__"] = webform_data(formulier, moment)
    return data


def schrijf_export(formulier: Formulier, pad: str | Path, moment: dt.datetime | None = None) -> list[str]:
    """Schrijft het exportbestand en geeft de SETU-problemen terug (ter informatie; de upload werkt ook met fouten)."""
    data = export(formulier, moment)
    Path(pad).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if "error" in data:
        return [data["error"]]
    return valideer(data)
