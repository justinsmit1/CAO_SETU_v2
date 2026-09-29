"""07 Bijzondere uitkeringen: formulier → antwoorden → SETU, vergeleken met de webform."""

import datetime as dt

import pytest

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.codes import JaNee, Loonbasis, Peildatum
from setu_kern.bronnen.wijzerbelonen.formulier.s07_bijzondere_uitkeringen import (
    EenmaligeUitkering,
    HoeToegekend,
    HoeToegekendVast,
    Jubileumuitkering,
    SoortVariabeleUitkering,
    VariabeleUitkering,
    VasteUitkering,
)
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import naar_antwoorden
from referentie_kern.controle import antwoord_problemen, vergelijk_setu


def _rijk() -> Formulier:
    """Alle takken: elke manier van toekennen, alle voorwaarden, naar rato, min/max, meerdere variaties."""
    f = Formulier()
    b = f.bijzondere_uitkeringen
    b.eenmalige_uitkeringen_bekend = JaNee.JA
    b.eenmalige_uitkeringen = [
        EenmaligeUitkering(
            naam="Energietoeslag",
            min_duur_dienstverband=True,
            min_duur_namelijk="6 maanden",
            dienstverband_op_datum=True,
            dienstverband_datum_namelijk="1 december",
            voorwaarde_anders=True,
            voorwaarde_anders_namelijk="Geen ontslag aangezegd",
            toekenning_datum=dt.date(2026, 12, 1),
            hoe_toegekend=HoeToegekend.VAST_BEDRAG,
            vast_bedrag=750.5,
            naar_rato_deeltijd=JaNee.JA,
            naar_rato_duur_dienstverband=JaNee.NEE,
            min_max=JaNee.JA,
            minimum=100,
            maximum=750.5,
        ),
        EenmaligeUitkering(
            naam="Koopkracht",
            toekenning_datum=dt.date(2026, 6, 30),
            hoe_toegekend=HoeToegekend.PERCENTAGE_LOON,
            percentage=1.5,
            percentage_van=Loonbasis.JAARLOON,
            min_max=JaNee.JA,
            maximum=500,
        ),
        EenmaligeUitkering(naam="Iets anders", hoe_toegekend=HoeToegekend.ANDERS, anders="Waardebon", min_max=JaNee.NEE),
        EenmaligeUitkering(
            naam="Deeltijd en duur", hoe_toegekend=HoeToegekend.VAST_BEDRAG, vast_bedrag=200,
            naar_rato_deeltijd=JaNee.NEE, naar_rato_duur_dienstverband=JaNee.JA,
        ),
        EenmaligeUitkering(naam="Alleen naam"),
    ]
    b.vaste_uitkering_van_toepassing = JaNee.JA
    b.vaste_uitkeringen = [
        VasteUitkering(
            naam="Dertiende maand",
            min_duur_dienstverband=True,
            min_duur_namelijk="1 jaar",
            toekenning_datum=dt.date(2026, 12, 15),
            hoe_toegekend=HoeToegekendVast.DERTIENDE_MAAND,
        ),
        VasteUitkering(
            naam="Eindejaarsuitkering",
            dienstverband_op_datum=True,
            dienstverband_datum_namelijk="31 december",
            voorwaarde_anders=True,
            voorwaarde_anders_namelijk="In dienst",
            hoe_toegekend=HoeToegekendVast.PERCENTAGE_LOON,
            percentage=8.33,
            percentage_van=Loonbasis.MAANDLOON,
        ),
        VasteUitkering(naam="Vast", hoe_toegekend=HoeToegekendVast.VAST_BEDRAG, vast_bedrag=1200, naar_rato=JaNee.JA),
        VasteUitkering(naam="Vast zonder rato", hoe_toegekend=HoeToegekendVast.VAST_BEDRAG, vast_bedrag=300, naar_rato=JaNee.NEE),
        VasteUitkering(naam="Anders", hoe_toegekend=HoeToegekendVast.ANDERS, anders="Kerstpakket"),
    ]
    b.jubileumuitkering_van_toepassing = JaNee.JA
    b.jubileumuitkeringen = [
        Jubileumuitkering(
            naam="12,5 jaar",
            hoe_toegekend=HoeToegekend.PERCENTAGE_LOON,
            percentage=50,
            percentage_van=Loonbasis.MAANDLOON,
            dienstverband_jaren=12,
            dienstverband_maanden=6,
            referentiedatum=Peildatum.DATUM_INDIENSTTREDING,
            toekenning_datum=dt.date(2026, 3, 1),
            voorwaarden="Arbeidsverleden in de holding telt mee",
        ),
        Jubileumuitkering(
            naam="25 jaar",
            hoe_toegekend=HoeToegekend.VAST_BEDRAG,
            vast_bedrag=1000,
            naar_rato=JaNee.JA,
            dienstverband_jaren=25,
            referentiedatum=Peildatum.ANCIENNITEITSDATUM,
        ),
        Jubileumuitkering(
            naam="40 jaar",
            hoe_toegekend=HoeToegekend.ANDERS,
            anders="Een reis",
            dienstverband_jaren=40,
            referentiedatum=Peildatum.STARTDATUM_CONTRACT,
            voorwaarden="Alleen bij volledig dienstverband",
        ),
        Jubileumuitkering(naam="Alleen maanden", dienstverband_maanden=18, hoe_toegekend=HoeToegekend.VAST_BEDRAG, vast_bedrag=50,
                          naar_rato=JaNee.NEE),
    ]
    b.variabele_uitkering_van_toepassing = JaNee.JA
    b.variabele_uitkeringen = [
        VariabeleUitkering(
            soort=SoortVariabeleUitkering.BONUS,
            prestatie=True,
            prestatie_namelijk="Targets gehaald",
            resultaat=True,
            resultaat_namelijk="Winst > 1 mln",
            min_duur_dienstverband=True,
            min_duur_namelijk="1 jaar",
            dienstverband_op_datum=True,
            dienstverband_datum_namelijk="1 januari",
            voorwaarde_anders=True,
            voorwaarde_anders_namelijk="Goede beoordeling",
            toekenning_datum=dt.date(2026, 4, 1),
            hoe_toegekend=HoeToegekend.PERCENTAGE_LOON,
            percentage=10,
            percentage_van=Loonbasis.JAARLOON,
            min_max=JaNee.JA,
            minimum=0.5,
            maximum=5000,
        ),
        VariabeleUitkering(
            soort=SoortVariabeleUitkering.ANDERS,
            soort_anders_namelijk="Innovatiepremie",
            hoe_toegekend=HoeToegekend.VAST_BEDRAG,
            vast_bedrag=250,
            naar_rato=JaNee.JA,
            min_max=JaNee.NEE,
        ),
        VariabeleUitkering(soort=SoortVariabeleUitkering.WINST, hoe_toegekend=HoeToegekend.ANDERS, anders="Winstdeling"),
        VariabeleUitkering(soort=SoortVariabeleUitkering.PERFORMANCE),
    ]
    return f


def _half() -> Formulier:
    """Half ingevuld: ja zonder variaties, lege variaties, ontbrekende namen en bedragen."""
    f = Formulier()
    b = f.bijzondere_uitkeringen
    b.eenmalige_uitkeringen_bekend = JaNee.JA
    b.eenmalige_uitkeringen = [EenmaligeUitkering(), EenmaligeUitkering(hoe_toegekend=HoeToegekend.VAST_BEDRAG)]
    b.vaste_uitkering_van_toepassing = JaNee.JA  # zonder variaties
    b.jubileumuitkering_van_toepassing = JaNee.JA
    b.jubileumuitkeringen = [Jubileumuitkering(), Jubileumuitkering(hoe_toegekend=HoeToegekend.ANDERS)]
    b.variabele_uitkering_van_toepassing = JaNee.JA
    b.variabele_uitkeringen = [VariabeleUitkering(), VariabeleUitkering(soort=SoortVariabeleUitkering.ANDERS)]
    return f


def _nee() -> Formulier:
    f = Formulier()
    b = f.bijzondere_uitkeringen
    b.eenmalige_uitkeringen_bekend = JaNee.NEE
    b.vaste_uitkering_van_toepassing = JaNee.NEE
    b.jubileumuitkering_van_toepassing = JaNee.NEE
    b.variabele_uitkering_van_toepassing = JaNee.NEE
    return f


def _alleen_vast() -> Formulier:
    f = Formulier()
    b = f.bijzondere_uitkeringen
    b.vaste_uitkering_van_toepassing = JaNee.JA
    b.vaste_uitkeringen = [VasteUitkering(naam="13e maand", hoe_toegekend=HoeToegekendVast.DERTIENDE_MAAND)]
    b.jubileumuitkering_van_toepassing = JaNee.NEE
    return f


SCENARIOS = {"rijk": _rijk, "half": _half, "nee": _nee, "alleen-vast": _alleen_vast, "leeg": Formulier}


def _verschillen(webform, antwoorden: dict) -> list[str]:
    verschillen = vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))
    return [v for v in verschillen if not v.startswith(".baseDefinition")]


@pytest.mark.parametrize("naam", SCENARIOS)
def test_antwoorden_passen_op_de_webform(webform, naam):
    assert antwoord_problemen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


@pytest.mark.parametrize("naam", SCENARIOS)
def test_setu_gelijk_aan_webform(webform, naam):
    antwoorden = naar_antwoorden(SCENARIOS[naam]())
    assert _verschillen(webform, antwoorden) == []


def test_rijk_levert_alle_uitkeringen(webform):
    data = naar_setu.setu_json(_rijk())
    namen = [a["name"] for a in data["allowance"]]
    assert "Eenmalige uitkering: Iets anders: Waardebon" in namen
    assert "Variabele uitkering: Innovatiepremie" in namen
    assert len([n for n in namen if n.startswith(("Eenmalige", "Vaste", "Jubileum", "Variabele"))]) == 18


def test_verborgen_antwoorden_worden_ook_gelezen(webform):
    """De omzetting leest de antwoorden rechtstreeks, ook van verborgen vragen; bij 'nee' telt niets."""
    antwoorden = naar_antwoorden(Formulier())
    antwoorden.update(
        {
            "eenmalige-uitkeringen-bekend": "ja",
            "eenmalige-uitkeringen": [
                {"namelijk": "x", "hoe-toegekend": "vast-bedrag", "vast-bedrag_namelijk": "12,5", "anders": "verborgen",
                 "type_ander-percentage_percentage": "3", "voorwaarden_anders_namelijk": "zonder vinkje"},
            ],
            "vaste-uitkering-van-toepassing": "ja",
            "vaste-uitkeringen": [{"namelijk": "y", "hoe-toegekend": "ander-percentage", "type_ander-percentage_percentage": "abc",
                                   "min-max": "ja", "min-max/ja/minimum": "1"}],
            "jubileumuitkering-van-toepassing": "ja",
            "jubileumuitkeringen": [{"voorwaarden/min-duur-dienstverband": True, "voorwaarden/dienstverband-op-datum": True,
                                     "dienstverband-duur/jaren": "0", "dienstverband-duur/maanden": "2.5"}],
            "variabele-uitkering-van-toepassing": "nee",
            "variabele-uitkeringen": [{"soort": "bonus", "min-max": "ja"}],
        }
    )
    assert _verschillen(webform, antwoorden) == []


@pytest.mark.parametrize(
    "slug, rij",
    [
        ("eenmalige-uitkeringen", {"hoe-toegekend": "anders", "min-max": "ja"}),
        ("variabele-uitkeringen", {"min-max": "ja", "min-max/ja/minimum": "5"}),
    ],
)
def test_min_max_zonder_bedrag_loopt_vast(webform, slug, rij):
    """Webform-bug: min-max = ja zonder bedrag laat toSetuStandard vastlopen; wij doen dat na."""
    vraag = {"eenmalige-uitkeringen": "eenmalige-uitkeringen-bekend", "variabele-uitkeringen": "variabele-uitkering-van-toepassing"}
    antwoorden = {**naar_antwoorden(Formulier()), vraag[slug]: "ja", slug: [rij]}
    with pytest.raises(Exception, match="minValue"):
        webform.setu(antwoorden)
    with pytest.raises(TypeError):
        naar_setu.setu_json(antwoorden)
