"""04 Toeslagen: formulier → antwoorden → SETU, vergeleken met de webform."""

import datetime as dt

import pytest

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage, Tijd, VastBedrag
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Grondslag, Interval, JaNee, Loonbasis
from setu_kern.bronnen.wijzerbelonen.formulier.s04_toeslagen import (
    Cumulatief,
    Toepassingsperiode,
    ToepassingsperiodesType,
    ToeslagSoort,
    ToeslagVariatie,
)
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import datum_naar_ms, naar_antwoorden
from referentie_kern.controle import antwoord_problemen, vergelijk_setu


def _percentage(p: float, grondslag: Grondslag | None = None) -> Bedragregel:
    return Bedragregel(
        soort=BedragSoort.PERCENTAGE,
        percentage=Percentage(percentage=p, basis=Loonbasis.UURLOON, per=Interval.UUR, grondslag=grondslag),
    )


def _rijk() -> Formulier:
    """Alle soorten aangevinkt, met variaties, periodes (tijden, weekdagen, datums), cumulatief en compounding."""
    f = Formulier()
    t = f.toeslagen
    for naam in type(t).model_fields:
        if naam.endswith("_aan"):
            setattr(t, naam, True)
    t.onregelmatigheids_toeslagen = [
        ToeslagVariatie(
            omschrijving="Avond en nacht",
            bedrag=_percentage(25),
            voorwaarden="Buiten het dagvenster",
            cumulatief=Cumulatief.JA_CUMULATIEF,
            cumulatief_toelichting="Opgeteld bij overwerk",
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[
                Toepassingsperiode(starttijd=dt.time(20), eindtijd=dt.time(6), maandag=True, dinsdag=True, vrijdag=True),
                Toepassingsperiode(zaterdag=True, zondag=True),
                Toepassingsperiode(starttijd=dt.time(18, 30)),
            ],
        ),
        ToeslagVariatie(
            omschrijving="Feestdagen",
            bedrag=_percentage(100.5),
            cumulatief=Cumulatief.JA_COMPOUNDING,
            compounding={ToeslagSoort.PLOEGENTOESLAGEN: True, ToeslagSoort.OVERWERK: True, ToeslagSoort.ANDERS: True},
            toepassingsperiodes_type=ToepassingsperiodesType.ALTIJD,
        ),
    ]
    t.ploegentoeslagen = [
        ToeslagVariatie(
            bedrag=Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=12.5, per=Interval.DIENST)),
            voorwaarden="3-ploegendienst, 5 dagen per week",
            cumulatief=Cumulatief.NEE,
            afbouwregeling=JaNee.JA,
            afbouwregeling_namelijk="Afbouw in 3 jaar",
        )
    ]
    t.toeslagen_verschoven_diensten = [
        ToeslagVariatie(
            bedrag=_percentage(10),
            cumulatief=Cumulatief.JA_COMPOUNDING,
            compounding={ToeslagSoort.ONREGELMATIGHEIDSTOESLAGEN: True},
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[Toepassingsperiode(starttijd=dt.time(5), eindtijd=dt.time(7), woensdag=True, donderdag=True)],
        )
    ]
    t.toeslagen_fysieke_belasting = [
        ToeslagVariatie(bedrag=Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=2, per=Interval.UUR)))
    ]
    t.toeslagen_stand_by = [ToeslagVariatie(bedrag=_percentage(50), cumulatief=Cumulatief.NEE)]
    t.overwerktoeslag = [
        ToeslagVariatie(
            omschrijving="Eerste 2 uur",
            bedrag=Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=1.25, per=Interval.UUR)),
            voorwaarden="Wanneer meer wordt gewerkt dan de overeengekomen arbeidsomvang.",
            cumulatief=Cumulatief.JA_CUMULATIEF,
            toepassingsperiodes_type=ToepassingsperiodesType.ALTIJD,
        ),
        ToeslagVariatie(
            omschrijving="Daarna",
            bedrag=Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=1.5, per=Interval.UUR)),
            cumulatief=Cumulatief.NEE,
        ),
    ]
    t.waarnemingstoeslag = [
        ToeslagVariatie(
            bedrag=Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=150, per=Interval.MAAND)),
            cumulatief=Cumulatief.JA_CUMULATIEF,
            afbouwregeling=JaNee.NEE,
        )
    ]
    t.performancetoeslag = [
        ToeslagVariatie(bedrag=_percentage(3), cumulatief=Cumulatief.NEE, afbouwregeling=JaNee.JA)  # zonder "namelijk"
    ]
    t.anders = [
        ToeslagVariatie(
            naam="BHV-toeslag",
            bedrag=Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=25, per=Interval.JAAR)),
            cumulatief=Cumulatief.JA_COMPOUNDING,
            compounding={ToeslagSoort.WAARNEMINGSTOESLAG: True, ToeslagSoort.PERFORMANCETOESLAG: True},
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[
                Toepassingsperiode(
                    startdatum=dt.date(2026, 1, 1), einddatum=dt.date(2026, 12, 31), starttijd=dt.time(8), maandag=True
                ),
                Toepassingsperiode(startdatum=dt.date(2027, 3, 15)),
            ],
            afbouwregeling=JaNee.JA,
            afbouwregeling_namelijk="Geen",
        ),
        ToeslagVariatie(naam="OR-toeslag", omschrijving="Voor OR-leden", bedrag=_percentage(1.5)),
    ]
    return f


def _half() -> Formulier:
    """Half ingevuld: lege variaties, soort zonder variaties, cumulatief zonder andere toeslagen, lege periode."""
    f = Formulier()
    t = f.toeslagen
    t.onregelmatigheids_toeslagen_aan = True
    t.onregelmatigheids_toeslagen = [ToeslagVariatie()]
    t.ploegentoeslagen_aan = True  # aangevinkt, maar (nog) geen variatie
    t.overwerktoeslag_aan = True
    t.overwerktoeslag = [
        ToeslagVariatie(
            bedrag=Bedragregel(soort=BedragSoort.PERCENTAGE),
            cumulatief=Cumulatief.JA_COMPOUNDING,
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[Toepassingsperiode()],
        ),
        ToeslagVariatie(cumulatief=Cumulatief.JA_CUMULATIEF, cumulatief_toelichting="Samen met ORT"),
    ]
    t.anders_aan = True
    t.anders = [ToeslagVariatie(bedrag=Bedragregel(soort=BedragSoort.VAST_BEDRAG), afbouwregeling=JaNee.JA)]
    return f


def _alleen_een() -> Formulier:
    f = Formulier()
    t = f.toeslagen
    t.toeslagen_stand_by_aan = True
    t.toeslagen_stand_by = [
        ToeslagVariatie(
            bedrag=_percentage(30),
            cumulatief=Cumulatief.JA_CUMULATIEF,  # geen andere toeslagen: geen verwijzingen
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[Toepassingsperiode(eindtijd=dt.time(23, 0), zondag=True)],
        )
    ]
    return f


def _geen() -> Formulier:
    f = Formulier()
    f.toeslagen.geen_toeslagen = True
    return f


def _met_grondslag() -> Formulier:
    f = _alleen_een()
    f.toeslagen.toeslagen_stand_by[0].bedrag = _percentage(30, Grondslag.BASISLOON)
    return f


SCENARIOS = {
    "rijk": _rijk,
    "half": _half,
    "alleen-een": _alleen_een,
    "geen": _geen,
    "met-grondslag": _met_grondslag,
    "leeg": Formulier,
}


@pytest.mark.parametrize("naam", SCENARIOS)
def test_antwoorden_passen_op_de_webform(webform, naam):
    assert antwoord_problemen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


@pytest.mark.parametrize("naam", SCENARIOS)
def test_setu_gelijk_aan_webform(webform, naam):
    antwoorden = naar_antwoorden(SCENARIOS[naam]())
    verschillen = vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))
    # Grondslagen (15) volgt uit de gekozen grondslag; die sectie is apart getest.
    assert [v for v in verschillen if not v.startswith(".baseDefinition")] == []


@pytest.mark.parametrize("bron", ["onze", "webform"])
def test_rijk_levert_alle_variaties(webform, bron):
    antwoorden = naar_antwoorden(_rijk())
    data = naar_setu.setu_json(antwoorden) if bron == "onze" else webform.setu(antwoorden)
    toeslagen = [t for t in data["allowance"] if t.get("typeCode") in {"HT320", "HT300", "HT101", "EA301", "HT602", "HT200", "EA300"}]
    assert len(toeslagen) == 12
    assert toeslagen[-2]["phaseOutScheme"] == "Geen" and toeslagen[-2]["period"][0]["datePeriod"] == [
        {"start": "2026-01-01", "end": "2026-12-31"}
    ]
    ort = toeslagen[0]
    assert ort["name"] == "Onregelmatigheids- toeslagen (waaronder feestdagen)"
    assert ort["period"][0] == {
        "timePeriod": {"start": "20:00:00", "end": "06:00:00"},
        "weekday": [{"value": "Monday"}, {"value": "Tuesday"}, {"value": "Friday"}],
    }
    assert ort["period"][1]["timePeriod"] == {"start": "00:00:00", "end": "23:59:00"}
    assert [r["typeCode"] for r in toeslagen[1]["reference"]] == ["HT300", "HT200", "EA300"]


def test_verborgen_antwoorden_worden_toch_gelezen(webform):
    """Webform-bug: periodes/afbouw/compounding worden gelezen zonder zichtbaarheidscontrole."""
    antwoorden = naar_antwoorden(Formulier())
    antwoorden["ploegentoeslagen/enabled"] = True
    antwoorden["overwerktoeslag/enabled"] = True
    antwoorden["ploegentoeslagen"] = [
        {
            "amount-type": "tijd",
            "tijd/uur": "abc",  # geen getal: NaN → null
            "description": "verborgen bij één variatie",
            "name": "verborgen titel",
            "cumulatief": "ja-compounding",
            "compounding/ploegentoeslagen": True,  # naar zichzelf
            "compounding/overwerktoeslag": True,
            "compounding/anders": True,  # niet aangevinkt
            "toepassingsperiodes-type": "bepaald",  # blok verborgen bij ploegentoeslagen
            "toepassingsperiodes": [{"startdatum": datum_naar_ms(dt.date(2026, 1, 1)), "starttijd": "25:99", "weekdagen/Monday": True}],
            "afbouwregeling": "ja",
        }
    ]
    antwoorden["overwerktoeslag"] = [{"afbouwregeling": "ja", "afbouwregeling/ja-namelijk": "verborgen"}]
    onze = naar_setu.setu_json(antwoorden)
    assert vergelijk_setu(webform, antwoorden, onze) == []
    ploeg, overwerk = [t for t in onze["allowance"] if t.get("typeCode") in ("HT300", "HT200")]
    assert ploeg["name"] == "Ploegentoeslagen" and ploeg["phaseOutScheme"] == ""
    assert [r["typeCode"] for r in ploeg["reference"]] == ["HT300", "HT200"]
    assert ploeg["period"] == [
        {"datePeriod": [{"start": "2026-01-01"}], "timePeriod": {"end": "23:59:00"}, "weekday": [{"value": "Monday"}]}
    ]
    assert overwerk["phaseOutScheme"] == "verborgen"
