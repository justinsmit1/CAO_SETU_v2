"""06 Vergoedingen: formulier → antwoorden → SETU, vergeleken met de webform."""

import pytest

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier import s06_vergoedingen as v
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Interval, JaNee, Loonbasis
from setu_kern.bronnen.wijzerbelonen.koppeling import antwoorden as antwoorden_module
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import STANDAARD_ANTWOORDEN, naar_antwoorden
from referentie_kern.controle import antwoord_problemen, vergelijk_setu


def _vol() -> Formulier:
    """Alle takken met een bedrag: drie variaties eigen vervoer, OV, reisuren %, stand-by %, zorg, thuiswerk + internet,
    alle mobiliteitsregelingen (met alternatieven) en alle kostenvergoedingen."""
    f = Formulier()
    ve = f.vergoedingen
    r = ve.reiskosten
    r.kent_eigen_vervoer = r.kent_ov = r.kent_zakelijke_kilometers = r.kent_zakelijke_kilometers_ov = r.kent_andere = True
    r.eigen_vervoer = [
        v.EigenVervoerVariatie(type=v.EigenVervoerType.STANDAARD_TARIEF, voorwaarden="Auto"),
        v.EigenVervoerVariatie(type=v.EigenVervoerType.ANDER_TARIEF_PER_KM, ander_tarief_per_km_bedrag=0.19, voorwaarden="Fiets"),
        v.EigenVervoerVariatie(type=v.EigenVervoerType.PER_TIJDVAK, per_tijdvak_bedrag=25, per_tijdvak_type=v.Tijdvak.MAAND),
    ]
    r.ov = v.OvVergoeding(type=v.OvType.PER_RIT, per_rit_bedrag=3.5, voorwaarden="2e klas")
    r.zakelijke_kilometers = [v.EigenVervoerVariatie(type=v.EigenVervoerType.ANDERS, anders_namelijk="Declaratie", voorwaarden="Bus")]
    r.zakelijke_kilometers_ov = v.OvVergoeding(type=v.OvType.VOLLEDIGE_VERGOEDING)
    r.andere_namelijk = "Parkeerkosten"

    ve.reisuren = v.Reisuren(
        vergoeding=v.ReistijdVergoeding.PERCENTAGE,
        percentage=50,
        percentage_van=Loonbasis.UURLOON,
        percentage_tijdvak=v.Tijdvak.UUR,
        voorwaarden="Boven 1 uur reistijd",
    )
    ve.stand_by = v.StandBy(
        ja_nee=JaNee.JA,
        type=v.StandByType.PERCENTAGE_PER_TIJDVAK,
        percentage=10.5,
        percentage_van=Loonbasis.UURLOON,
        percentage_tijdvak=v.TijdvakStandBy.DIENST,
        voorwaarden="Alleen in het weekend",
    )
    ve.zorgverzekering = v.Zorgverzekering(
        ja_nee=JaNee.JA,
        type=v.ZorgverzekeringType.VERGOEDING_PER_TIJDSEENHEID,
        bedrag=12.5,
        tijdvak=v.Tijdvak.MAAND,
        min_max=JaNee.JA,
        minimum=5,
        maximum=20,
        naar_rato=JaNee.JA,
        voorwaarden="Via collectief",
    )
    ve.thuiswerk = v.Thuiswerk(
        ja_nee=JaNee.JA,
        bedrag=2.35,
        tijdvak=v.Tijdvak.DAG,
        voorwaarden="Per thuiswerkdag",
        naar_rato=JaNee.NEE,
        internet_inbegrepen=JaNee.NEE,
        extra_internet=JaNee.JA,
        internet_bedrag=15,
        internet_tijdvak=v.Tijdvak.MAAND,
        internet_voorwaarden="Met factuur",
        internet_naar_rato=JaNee.JA,
    )
    m = ve.mobiliteit
    m.mobiliteitsvergoeding = v.MobiliteitsRegeling(
        aangevinkt=True, bedrag=100, tijdvak=Interval.MAAND, voorwaarden="Budget", naar_rato=JaNee.JA
    )
    m.regeling_leaseauto = v.MobiliteitsRegelingMetAlternatief(
        aangevinkt=True,
        bedrag=650,
        tijdvak=Interval.MAAND,
        naar_rato=JaNee.NEE,
        alternatief=True,
        alternatief_bedrag=300,
        alternatief_tijdvak=Interval.MAAND,
        alternatief_voorwaarden="Bij afzien van leaseauto",
        alternatief_naar_rato=JaNee.JA,
    )
    m.regeling_leasefiets = v.MobiliteitsRegelingMetAlternatief(aangevinkt=True, bedrag=40, tijdvak=Interval.MAAND, alternatief=True)
    m.regeling_ov_vergoeding = v.MobiliteitsRegelingMetAlternatief(aangevinkt=True, bedrag=1, tijdvak=Interval.KILOMETER)
    m.fietsregeling = v.MobiliteitsRegeling(aangevinkt=True, voorwaarden="Eens per 3 jaar")
    k = ve.kosten
    k.koffiegeld = v.KostenVergoeding(aangevinkt=True, bedrag=1.5, tijdvak=v.TijdvakKosten.DAG, naar_rato=JaNee.NEE)
    k.maaltijdvergoeding = v.KostenVergoeding(aangevinkt=True, bedrag=12, tijdvak=v.TijdvakKosten.ITEM, voorwaarden="Na 19 uur")
    k.wasvergoeding = v.KostenVergoeding(aangevinkt=True, bedrag=5, tijdvak=v.TijdvakKosten.WEEK, naar_rato=JaNee.JA)
    k.bedrijfskleding_schoenen = v.KostenVergoeding(aangevinkt=True, bedrag=150, tijdvak=v.TijdvakKosten.JAAR)
    k.arbo_vergoeding = v.KostenVergoeding(aangevinkt=True)
    k.byod_vergoeding = v.KostenVergoeding(aangevinkt=True, bedrag=20, tijdvak=v.TijdvakKosten.MAAND)
    k.anders = True
    k.anders_namelijk = "Verhuiskosten"
    return f


def _varianten() -> Formulier:
    """De andere keuzes: 'anders' zonder tekst, OV per km/traject, reisuren vast, stand-by vast, zorg anders,
    internet inbegrepen, kosten 'geen'."""
    f = Formulier()
    ve = f.vergoedingen
    r = ve.reiskosten
    r.kent_eigen_vervoer = r.kent_ov = r.kent_zakelijke_kilometers = r.kent_zakelijke_kilometers_ov = True
    r.eigen_vervoer = [v.EigenVervoerVariatie(type=v.EigenVervoerType.ANDERS)]  # naam eindigt op "null"
    r.zakelijke_kilometers = [
        v.EigenVervoerVariatie(type=v.EigenVervoerType.PER_TIJDVAK, per_tijdvak_bedrag=10),
        v.EigenVervoerVariatie(type=v.EigenVervoerType.STANDAARD_TARIEF),
    ]
    r.ov = v.OvVergoeding(type=v.OvType.PER_KILOMETER, per_kilometer_bedrag=0.12)
    r.zakelijke_kilometers_ov = v.OvVergoeding(type=v.OvType.PER_TRAJECT, per_traject_bedrag=4, voorwaarden="Enkele reis")
    ve.reisuren = v.Reisuren(
        vergoeding=v.ReistijdVergoeding.VASTE_VERGOEDING, vaste_vergoeding_bedrag=7.5, vaste_vergoeding_per=v.TijdvakReisuren.ROUTE
    )
    ve.stand_by = v.StandBy(
        ja_nee=JaNee.JA, type=v.StandByType.VERGOEDING_PER_TIJDVAK, vast_bedrag=30, vast_tijdvak=v.TijdvakStandBy.DAG
    )
    ve.zorgverzekering = v.Zorgverzekering(ja_nee=JaNee.JA, type=v.ZorgverzekeringType.ANDERS, anders_namelijk="Collectieve korting")
    ve.thuiswerk = v.Thuiswerk(ja_nee=JaNee.JA, bedrag=2, tijdvak=v.Tijdvak.DAG, naar_rato=JaNee.JA, internet_inbegrepen=JaNee.JA)
    ve.kosten.geen = True
    return f


def _anders() -> Formulier:
    """'Anders' bij reisuren, stand-by, OV en kosten; nee bij zorg en thuiswerk; extra internet nee."""
    f = Formulier()
    ve = f.vergoedingen
    r = ve.reiskosten
    r.kent_ov = r.kent_andere = True
    r.ov = v.OvVergoeding(type=v.OvType.ANDERS, anders_namelijk="NS-Business card", voorwaarden="Op aanvraag")
    ve.reisuren = v.Reisuren(vergoeding=v.ReistijdVergoeding.ANDERS, anders_namelijk="Reistijd is werktijd", voorwaarden="Buiten NL")
    ve.stand_by = v.StandBy(
        ja_nee=JaNee.JA, type=v.StandByType.ANDERS, anders_namelijk="Vast bedrag per week", voorwaarden="gaat verloren"
    )
    ve.zorgverzekering = v.Zorgverzekering(ja_nee=JaNee.NEE)
    ve.thuiswerk = v.Thuiswerk(ja_nee=JaNee.NEE)
    ve.kosten.anders = True
    return f


def _half() -> Formulier:
    """Half ingevuld: vinkjes zonder vervolgantwoorden, 'ja' zonder soort, een lege variatie."""
    f = Formulier()
    ve = f.vergoedingen
    r = ve.reiskosten
    r.kent_eigen_vervoer = r.kent_ov = r.kent_zakelijke_kilometers = r.kent_andere = True
    r.eigen_vervoer = [v.EigenVervoerVariatie(), v.EigenVervoerVariatie(voorwaarden="Alleen voorwaarden")]
    ve.reisuren = v.Reisuren(voorwaarden="Voorwaarden zonder keuze")
    ve.stand_by = v.StandBy(ja_nee=JaNee.JA, voorwaarden="Zonder soort")
    ve.zorgverzekering = v.Zorgverzekering(ja_nee=JaNee.JA)
    ve.thuiswerk = v.Thuiswerk(ja_nee=JaNee.JA, internet_inbegrepen=JaNee.NEE, extra_internet=JaNee.NEE)
    ve.mobiliteit.regeling_leaseauto = v.MobiliteitsRegelingMetAlternatief(aangevinkt=True, alternatief=True)
    ve.mobiliteit.fietsregeling = v.MobiliteitsRegeling(aangevinkt=True)
    ve.kosten.koffiegeld = v.KostenVergoeding(aangevinkt=True)
    return f


SCENARIOS = {"vol": _vol, "varianten": _varianten, "anders": _anders, "half": _half, "leeg": Formulier}


@pytest.mark.parametrize("naam", SCENARIOS)
def test_antwoorden_passen_op_de_webform(webform, naam):
    assert antwoord_problemen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


@pytest.mark.parametrize("naam", SCENARIOS)
def test_setu_gelijk_aan_webform(webform, naam):
    antwoorden = naar_antwoorden(SCENARIOS[naam]())
    verschillen = vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))
    assert [d for d in verschillen if not d.startswith(".baseDefinition")] == []


def test_eigen_vervoer_sleutels_met_voorloop_slash():
    antwoorden = naar_antwoorden(_vol())
    assert antwoorden["reiskostenvergoeding-eigen-vervoer"][1] == {
        "type": "ander-tarief-per-km",
        "/ander-tarief-per-km/bedrag": "0.19",
        "/voorwaarden": "Fiets",
    }


def test_verborgen_antwoorden_tellen_niet_mee(webform):
    """Antwoorden achter een uitgevinkte of 'nee'-keuze (bijv. na terugzetten) komen niet in SETU."""
    antwoorden = {
        **{k: [dict(r) for r in w] if isinstance(w, list) else w for k, w in STANDAARD_ANTWOORDEN.items()},
        "reiskostenvergoeding-ov-type": "volledige-vergoeding",
        "reiskostenvergoeding-eigen-vervoer": [{"type": "standaard-tarief"}],
        "andere-reiskostenvergoeding-namelijk": "verborgen",
        "vergoeding-stand-by-piket-consignatie-bereikbaarheidsdiensten": "nee",
        "type-vergoeding-stand-by": "anders",
        "thuiswerkvergoeding": "ja",
        "thuiswerkvergoeding/ja/internetvergoeding-inbegrepen": "ja",
        "thuiswerkvergoeding/ja/extra-internetvergoeding": "ja",
        # Zichtbaar, maar leest verborgen/verkeerde antwoorden mee (zoals de webform).
        "vergoeding-zorgverzekering": "ja",
        "vergoeding-zorgverzekering-type": "vergoeding-per-tijdseenheid",
        "vergoeding-zorgerzekering-naar-rato": "ja",
        "mobiliteit/mobiliteitsvergoeding": True,
        "mobiliteit/mobiliteitsvergoeding/alternatief": True,
    }
    verschillen = vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))
    assert verschillen == []
