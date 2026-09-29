"""Uitgebreid invullen (BLOKKEN_SETU): de SETU-velden die de webform niet kent, getest met een nep-LLM."""

import datetime as dt
import json

from jsonschema import Draft202012Validator
from test_kern_cao_pdf import PARAMETERS, _basis, _onderbouwing

from setu_kern.bronnen.cao_pdf import BLOKKEN_SETU, Fragment, van_cao_pdf, vul_formulier
from setu_kern.bronnen.cao_pdf.invullen.omzetten import naar_waarden
from setu_kern.bronnen.cao_pdf.invullen.schema import antwoord_schema, blok_schema
from setu_kern.bronnen.cao_pdf.invullen.uitgebreid_gedeeld import Vergelijking, Voorwaarde, VoorwaardeSoort
from setu_kern.bronnen.cao_pdf.invullen.uitgebreid_vakantiebijslag import VakantiebijslagRegel, VakantiebijslagSETU, _uitbetaling
from setu_kern.bronnen.cao_pdf.nep import LijstZoeker, NepLLM
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage, VastBedrag
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Grondslag, Interval, JaNee, Loonbasis

NAAM = BLOKKEN_SETU[0].naam
TEKST = (
    "De werknemer ontvangt in mei een vakantiebijslag van 8% van het jaarloon, met een minimum van € 500 "
    "en naar evenredigheid van de arbeidsduur. Werknemers vanaf 21 jaar krijgen dit percentage."
)
FRAGMENTEN = [Fragment("cao_test.pdf", 14, "Artikel 12 - Vakantiebijslag", TEKST)]


def _pct(percentage=8, grondslag=None) -> Bedragregel:
    return Bedragregel(
        soort=BedragSoort.PERCENTAGE,
        percentage=Percentage(percentage=percentage, basis=Loonbasis.JAARLOON, per=Interval.JAAR, grondslag=grondslag),
    )


def _volledig() -> VakantiebijslagSETU:
    return VakantiebijslagSETU(
        ja_nee=JaNee.JA,
        geldig_van=dt.date(2026, 1, 1),
        geldig_tot=dt.date(2026, 12, 31),
        uitbetaling_maand=5,
        toelichting="Uitbetaald in mei.",
        regels=[
            VakantiebijslagRegel(
                bedrag=_pct(),
                minimum_bedrag=500,
                naar_rato_deeltijd=JaNee.JA,
                naar_rato_dienstverband=JaNee.NEE,
                voorwaarden=[Voorwaarde(soort=VoorwaardeSoort.LEEFTIJD, vergelijking=Vergelijking.VANAF, leeftijd=21)],
            ),
            VakantiebijslagRegel(bedrag=Bedragregel(
                soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=250, per=Interval.JAAR)
            )),
        ],
    )


def _antwoord(instantie: VakantiebijslagSETU, paden=("ja_nee", "geldig_van", "geldig_tot", "uitbetaling_maand", "toelichting", "regels")):
    return {
        "waarden": naar_waarden(instantie, VakantiebijslagSETU),
        "onderbouwing": [_onderbouwing(p, TEKST) for p in paden],
        "niet_gevonden": [],
    }


def _vul(antwoord):
    llm = NepLLM({NAAM: antwoord}, BLOKKEN_SETU)
    return van_cao_pdf(llm, LijstZoeker(FRAGMENTEN), PARAMETERS, BLOKKEN_SETU, basis=_basis()), llm


def test_schema_is_strikt_en_kent_de_extra_velden():
    schema = antwoord_schema(blok_schema(VakantiebijslagSETU))
    Draft202012Validator.check_schema(schema)
    tekst = json.dumps(schema, ensure_ascii=False)
    for stuk in ("minimum_bedrag", "naar_rato_deeltijd", "uitbetaling_maand", "geldig_van", "voorwaarden", "loon_maximum"):
        assert stuk in tekst
    regel = schema["properties"]["waarden"]["properties"]["regels"]["items"]
    assert regel["properties"]["bedrag"]["anyOf"][0]["properties"]["soort"]["enum"] and set(
        regel["properties"]["bedrag"]["anyOf"][0]["properties"]["soort"]["enum"]
    ) == {"percentage", "vast-bedrag", None}
    assert list(Draft202012Validator(schema).iter_errors(_antwoord(_volledig()))) == []


def test_volledige_regeling_in_de_kern():
    resultaat, llm = _vul(_antwoord(_volledig()))
    regeling = resultaat.bericht.holiday_allowance[0]
    assert regeling.effective_period.valid_from == dt.date(2026, 1, 1) and regeling.effective_period.valid_to == dt.date(2026, 12, 31)
    assert regeling.pay_date.recurring_interval == "R/2026-05-01/P1Y"
    assert regeling.description == "Uitbetaald in mei."
    assert regeling.id.value == "VAKANTIEBIJSLAG"
    eerste, tweede = regeling.line
    assert eerste.line_id.value == "VAKANTIEBIJSLAG-1" and eerste.interval.unit_code.value == "Year"
    assert eerste.amount.value == 8 and eerste.amount.min_value == 500
    assert eerste.amount.proportional.part_time_percentage and not eerste.amount.proportional.employment_duration
    assert eerste.conditions[0].condition_type == "Age" and eerste.conditions[0].age == 21
    assert tweede.amount.value == 250 and tweede.amount.unit_code.value == "Euro" and tweede.conditions is None
    assert resultaat.bericht.valideer() == []  # volgens het officiële SETU-schema
    assert resultaat.geldig
    # Het Formulier krijgt alleen de webform-vragen: ja/nee en het eerste percentage.
    naam, berichten, schema = llm.aanroepen[0]
    assert TEKST in berichten[1]["content"] and "vakantiebijslag" in berichten[1]["content"].lower()


def test_formulier_blijft_webform_conform():
    llm = NepLLM({NAAM: _antwoord(_volledig())}, BLOKKEN_SETU)
    formulier, rapport = vul_formulier(llm, LijstZoeker(FRAGMENTEN), blokken=BLOKKEN_SETU)
    assert formulier.vakantiebijslag.ja_nee == JaNee.JA
    assert formulier.vakantiebijslag.bedrag.percentage.percentage == 8
    assert set(rapport.uitbreidingen) == {"vakantiebijslag"}
    assert rapport.naar_dict()["uitbreidingen"]["vakantiebijslag"]["uitbetaling_maand"] == 5
    assert "regels[0].minimum_bedrag" in {i.pad for i in rapport.blokken[0].ingevuld}


def test_waarde_zonder_onderbouwing_wordt_weggegooid():
    """Het minimum staat niet in de onderbouwde paden: het mag niet in de kern komen."""
    antwoord = _antwoord(_volledig(), paden=("ja_nee", "regels[0].bedrag", "regels[1]"))
    resultaat, _ = _vul(antwoord)
    regeling = resultaat.bericht.holiday_allowance[0]
    assert regeling.line[0].amount.min_value is None and regeling.pay_date is None and regeling.effective_period is None
    assert any("minimum_bedrag" in m and "geen onderbouwing" in m for m in resultaat.meldingen)


def test_een_beantwoorde_naar_rato_vraag_geeft_een_melding():
    vb = _volledig()
    vb.regels[0].naar_rato_dienstverband = None
    resultaat, _ = _vul(_antwoord(vb))
    proportional = resultaat.bericht.holiday_allowance[0].line[0].amount.proportional
    assert proportional.part_time_percentage and not proportional.employment_duration
    assert any("duur van het dienstverband niet genoemd" in m for m in resultaat.meldingen)


def test_geen_vakantiebijslag_verandert_de_kern_niet():
    resultaat, _ = _vul(_antwoord(VakantiebijslagSETU(ja_nee=JaNee.NEE), paden=("ja_nee",)))
    assert not resultaat.bericht.holiday_allowance


def test_grondslag_zonder_base_definition_geeft_een_melding():
    vb = _volledig()
    # De grondslag van de eerste regel gaat ook langs de webform (sectie 15); een latere regel doet dat niet.
    vb.regels[1].bedrag = _pct(4, grondslag=Grondslag.BRUTO_LOON)
    resultaat, _ = _vul(_antwoord(vb))
    assert any("grondslag 'GrossSalary' heeft nog geen baseDefinition" in m for m in resultaat.meldingen)


def test_onvolledige_voorwaarde_valt_weg_met_melding():
    vb = _volledig()
    vb.regels[0].voorwaarden = [Voorwaarde(soort=VoorwaardeSoort.LEEFTIJD)]
    resultaat, _ = _vul(_antwoord(vb))
    assert resultaat.bericht.holiday_allowance[0].line[0].conditions is None
    assert any("voorwaarde (leeftijd) is onvolledig" in m for m in resultaat.meldingen)


def test_uitbetaling_zonder_jaar_wordt_niet_verzonnen():
    """SETU eist zelf een 'geldig van' in het bericht; de regeling verzint zonder jaar geen datum."""
    meldingen: list[str] = []
    assert _uitbetaling(5, dt.date.min.year, meldingen) is None
    assert meldingen and "geen jaar bekend" in meldingen[0]
    assert _uitbetaling(None, 2026, meldingen) is None
    assert _uitbetaling(12, 2026, meldingen).recurring_interval == "R/2026-12-01/P1Y"
