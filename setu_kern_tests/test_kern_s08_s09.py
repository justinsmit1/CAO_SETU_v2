"""08 Loondoorbetaling bij ziekte en 09 Verlof: formulier → antwoorden → SETU, vergeleken met de webform."""

import pytest

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Grondslag, JaNee, Loonbasis
from setu_kern.bronnen.wijzerbelonen.formulier.s08_loondoorbetaling_bij_ziekte import LoondoorbetalingRegel, TijdvakZiekte, WachtdagcompensatieSoort
from setu_kern.bronnen.wijzerbelonen.formulier.s09_verlof import (
    AdvToekenning,
    AdvToekenningSoort,
    BijzonderVerlofEenheid,
    BijzonderVerlofVariatie,
    ExtraDagenAnders,
    ExtraDagenDuurDienstverband,
    ExtraDagenLeeftijd,
    Tijdvak,
    VakantiedagenType,
    WazoRegel,
)
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import naar_antwoorden
from referentie_kern.controle import antwoord_problemen, vergelijk_setu


# --- 08 Loondoorbetaling bij ziekte
def _ziekte_rijk() -> Formulier:
    f = Formulier()
    z = f.loondoorbetaling_bij_ziekte
    z.regels = [
        LoondoorbetalingRegel(
            percentage=100, van=Loonbasis.MAANDLOON, grondslag=Grondslag.BRUTO_LOON, per_tijdvak=TijdvakZiekte.MAAND,
            voorwaarden="Eerste jaar",
        ),
        LoondoorbetalingRegel(
            percentage=70, van=Loonbasis.DAGLOON, grondslag=Grondslag.BASISLOON, per_tijdvak=TijdvakZiekte.WEEK,
            voorwaarden="Tweede jaar",
        ),
        LoondoorbetalingRegel(percentage=50.5),  # zonder tijdvak: "Day"
    ]
    z.wachtdagen = JaNee.JA
    z.wachtdagen_aantal = 2
    z.wachtdagen_voorwaarden = JaNee.JA
    z.wachtdagen_voorwaarden_namelijk = "Vanaf de derde ziekmelding per jaar"
    z.wachtdagcompensatie = JaNee.JA
    z.compensatie_soort = WachtdagcompensatieSoort.PERCENTAGE
    z.compensatie_percentage = 80
    z.compensatie_basis = Loonbasis.UURLOON
    return f


def _ziekte_vast_bedrag() -> Formulier:
    f = Formulier()
    z = f.loondoorbetaling_bij_ziekte
    z.regels = [LoondoorbetalingRegel(percentage=90, van=Loonbasis.JAARLOON)]
    z.wachtdagen = JaNee.JA
    z.wachtdagen_aantal = 1
    z.wachtdagen_voorwaarden = JaNee.NEE
    z.wachtdagcompensatie = JaNee.JA
    z.compensatie_soort = WachtdagcompensatieSoort.VAST_BEDRAG
    z.compensatie_bedrag = 25.5
    return f


def _ziekte_half() -> Formulier:
    """Rij 0 zonder percentage (dan géén sickPay), compensatie ja zonder soort, voorwaarden ja zonder tekst."""
    f = Formulier()
    z = f.loondoorbetaling_bij_ziekte
    z.regels = [LoondoorbetalingRegel(van=Loonbasis.MAANDLOON), LoondoorbetalingRegel(percentage=80)]
    z.wachtdagen = JaNee.JA
    z.wachtdagen_voorwaarden = JaNee.JA
    z.wachtdagcompensatie = JaNee.JA
    return f


def _ziekte_wachtdagen_zonder_voorwaardetekst() -> Formulier:
    f = Formulier()
    z = f.loondoorbetaling_bij_ziekte
    z.regels = [LoondoorbetalingRegel(percentage=100)]
    z.wachtdagen = JaNee.JA
    z.wachtdagen_aantal = 3
    z.wachtdagen_voorwaarden = JaNee.JA
    z.wachtdagcompensatie = JaNee.NEE
    return f


def _ziekte_geen_wachtdagen() -> Formulier:
    f = Formulier()
    f.loondoorbetaling_bij_ziekte.regels = [LoondoorbetalingRegel(percentage=100, per_tijdvak=TijdvakZiekte.JAAR)]
    f.loondoorbetaling_bij_ziekte.wachtdagen = JaNee.NEE
    return f


# --- 09 Verlof
def _verlof_rijk() -> Formulier:
    f = Formulier()
    v = f.verlof
    adv = v.adv_atv
    adv.adv_regeling = JaNee.JA
    adv.namelijk = "ATV bouw"
    adv.toekenning = AdvToekenning(
        toekenning=AdvToekenningSoort.GELD, geld_percentage=4.5, geld_van=Loonbasis.VIERWEKENLOON  # geen interval in B9
    )
    adv.aanvullende_regeling = JaNee.JA
    adv.ouderen = True
    adv.ouderen_namelijk = "vanaf 60 jaar"
    adv.toekenning_ouderen = AdvToekenning(
        toekenning=AdvToekenningSoort.TIJD_DAGEN, dagen_aantal=3, dagen_tijdvak=Tijdvak.JAAR
    )
    adv.duur_dienstverband = True
    adv.duur_dienstverband_namelijk = "na 10 jaar"
    adv.toekenning_duur_dienstverband = AdvToekenning(
        toekenning=AdvToekenningSoort.TIJD_UREN, uren_aantal=1.5, uren_tijdvak=Tijdvak.WEEK
    )
    adv.anders = True
    adv.anders_namelijk = "ploegendienst"  # bug: komt niet in SETU
    adv.toekenning_anders = AdvToekenning(
        toekenning=AdvToekenningSoort.GELD, geld_percentage=2, geld_van=Loonbasis.MAANDLOON
    )

    vak = v.vakantiedagen
    vak.aantal = 25
    vak.type = VakantiedagenType.UREN
    vak.tijdvak = Tijdvak.JAAR
    vak.dagen_leeftijd = True
    vak.leeftijd = [ExtraDagenLeeftijd(leeftijd=45, dagen=1), ExtraDagenLeeftijd(leeftijd=55, dagen=2.5)]
    vak.dagen_duur_dienstverband = True
    vak.duur_dienstverband = [ExtraDagenDuurDienstverband(jaar=10, dagen=1)]
    vak.dagen_anders = True
    vak.anders = [ExtraDagenAnders(dagen=2, namelijk="mantelzorgers"), ExtraDagenAnders(dagen=1)]

    bv = v.bijzonder_verlof
    bv.aanwezig = JaNee.JA
    bv.variaties = [
        BijzonderVerlofVariatie(hoeveel=1, wat=BijzonderVerlofEenheid.DAGEN, voorwaarden="Huwelijk"),
        BijzonderVerlofVariatie(hoeveel=8, wat=BijzonderVerlofEenheid.UUR, voorwaarden="Verhuizing"),
        BijzonderVerlofVariatie(hoeveel=2, wat=BijzonderVerlofEenheid.WEKEN),
        BijzonderVerlofVariatie(),
    ]

    v.tijd_voor_tijd.tijd_voor_tijd = JaNee.JA
    v.tijd_voor_tijd.namelijk = "Overuren worden 1:1 omgezet in verlof"

    wazo = v.aanvulling_wazo
    wazo.wazo_aanvulling = JaNee.JA
    wazo.betaald_ouderschapsverlof = WazoRegel(aangevinkt=True, namelijk="aanvulling tot 100%")
    wazo.onbetaald_ouderschapsverlof = WazoRegel(aangevinkt=True, namelijk="aanvulling 25%")
    wazo.geboorteverlof = WazoRegel(aangevinkt=True)
    wazo.kortdurend_zorgverlof = WazoRegel(aangevinkt=True, namelijk="100% doorbetaling")
    wazo.langdurend_zorgverlof = WazoRegel(aangevinkt=True, namelijk="50%")
    wazo.langere_verlofduur = WazoRegel(aangevinkt=True, namelijk="2 weken extra")
    wazo.anders = WazoRegel(aangevinkt=True, namelijk="adoptieverlof")

    va = v.verplichte_aanwending
    va.verplichte_aanwending = JaNee.JA
    va.periode_dagen_uren = "Brugdag na Hemelvaart\nBouwvak"
    va.welk_verlof = "Vakantiedagen"

    fd = v.feestdagen
    fd.aantal = 8
    fd.welke = "  Nieuwjaarsdag \nTweede Paasdag\n Koningsdag\n5 mei  \n"
    fd.voorwaarden = "Alleen als de feestdag op een werkdag valt"
    fd.niet_elk_jaar = JaNee.JA
    fd.niet_elk_jaar_voorwaarden = "5 mei, eens per 5 jaar"
    fd.persoonlijke_feestdagen = JaNee.JA
    fd.persoonlijk_aantal = 1
    fd.persoonlijk_namelijk = "Suikerfeest\nDiwali"
    fd.persoonlijk_voorwaarden = "In overleg"

    v.waarde_verlofdag.waarde_verlofdag = JaNee.JA
    v.waarde_verlofdag.percentage = 0.4
    return f


def _verlof_half() -> Formulier:
    """Veel "ja" zonder de bijbehorende details: namen met ``null``, lege toekenningen, lege rijen."""
    f = Formulier()
    v = f.verlof
    v.adv_atv.adv_regeling = JaNee.JA
    v.adv_atv.aanvullende_regeling = JaNee.JA
    v.adv_atv.anders = True
    v.adv_atv.duur_dienstverband = True
    v.adv_atv.toekenning_duur_dienstverband = AdvToekenning(toekenning=AdvToekenningSoort.TIJD_DAGEN)
    v.vakantiedagen.aantal = 20
    v.vakantiedagen.dagen_leeftijd = True
    v.vakantiedagen.leeftijd = [ExtraDagenLeeftijd()]
    v.bijzonder_verlof.aanwezig = JaNee.JA
    v.bijzonder_verlof.variaties = [BijzonderVerlofVariatie()]
    v.tijd_voor_tijd.tijd_voor_tijd = JaNee.JA
    v.aanvulling_wazo.wazo_aanvulling = JaNee.JA
    v.aanvulling_wazo.anders = WazoRegel(aangevinkt=True)
    v.verplichte_aanwending.verplichte_aanwending = JaNee.JA
    v.feestdagen.aantal = 7
    v.feestdagen.niet_elk_jaar = JaNee.JA
    v.feestdagen.persoonlijke_feestdagen = JaNee.JA
    v.waarde_verlofdag.waarde_verlofdag = JaNee.JA
    return f


def _verlof_nee() -> Formulier:
    """Overal "nee", en details zonder hoofdvraag (feestdagen zonder aantal, extra dagen zonder aantal)."""
    f = Formulier()
    v = f.verlof
    v.adv_atv.adv_regeling = JaNee.NEE
    v.vakantiedagen.type = VakantiedagenType.DAGEN
    v.vakantiedagen.dagen_anders = True
    v.vakantiedagen.anders = [ExtraDagenAnders(dagen=3, namelijk="jubileum")]
    v.bijzonder_verlof.aanwezig = JaNee.NEE
    v.tijd_voor_tijd.tijd_voor_tijd = JaNee.NEE
    v.aanvulling_wazo.wazo_aanvulling = JaNee.NEE
    v.verplichte_aanwending.verplichte_aanwending = JaNee.NEE
    v.feestdagen.welke = "Kerst"
    v.feestdagen.niet_elk_jaar = JaNee.NEE
    v.feestdagen.persoonlijke_feestdagen = JaNee.NEE
    v.waarde_verlofdag.waarde_verlofdag = JaNee.NEE
    return f


def _nulwaarden() -> Formulier:
    """Een 0 is onwaar in JavaScript: dan wordt niet omgezet en komt de 0 zelf op het setuPath."""
    f = Formulier()
    f.loondoorbetaling_bij_ziekte.regels = [LoondoorbetalingRegel(percentage=0), LoondoorbetalingRegel(percentage=70)]
    f.verlof.vakantiedagen.aantal = 0
    f.verlof.feestdagen.aantal = 0
    f.verlof.feestdagen.welke = "Kerst"
    return f


def _alles() -> Formulier:
    f = _verlof_rijk()
    f.loondoorbetaling_bij_ziekte = _ziekte_rijk().loondoorbetaling_bij_ziekte
    return f


SCENARIOS = {
    "ziekte_rijk": _ziekte_rijk,
    "ziekte_vast_bedrag": _ziekte_vast_bedrag,
    "ziekte_half": _ziekte_half,
    "ziekte_wachtdagen_zonder_voorwaardetekst": _ziekte_wachtdagen_zonder_voorwaardetekst,
    "ziekte_geen_wachtdagen": _ziekte_geen_wachtdagen,
    "verlof_rijk": _verlof_rijk,
    "verlof_half": _verlof_half,
    "verlof_nee": _verlof_nee,
    "nulwaarden": _nulwaarden,
    "alles": _alles,
    "leeg": Formulier,
}


@pytest.mark.parametrize("naam", SCENARIOS)
def test_antwoorden_passen_op_de_webform(webform, naam):
    assert antwoord_problemen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


@pytest.mark.parametrize("naam", SCENARIOS)
def test_setu_gelijk_aan_webform(webform, naam):
    antwoorden = naar_antwoorden(SCENARIOS[naam]())
    verschillen = vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))
    # Grondslagen (15) volgt uit de gekozen grondslag bij de loondoorbetaling; die sectie is apart getest.
    assert [v for v in verschillen if not v.startswith(".baseDefinition")] == []


def test_bekende_bugs_nagedaan():
    data = naar_setu.setu_json(_alles())
    regels = data["sickPay"][0]["line"]
    assert [r["amount"]["value"] for r in regels] == [100, 100, 100]  # percentage van rij 0
    assert {r["amount"]["baseAmount"]["baseType"] for r in regels} == {"GrossSalary"}  # grondslag van rij 0
    namen = [verlof["name"] for verlof in data["leave"]]
    assert "Aanvullende ADV / ATV regeling voor anders: null" in namen
    vakantie = next(verlof for verlof in data["leave"] if verlof["name"] == "Vakantiedagen")
    duur = [p for p in vakantie["paidLeave"] if p.get("conditions", [{}])[0].get("conditionType") == "EmploymentDuration"]
    assert duur and all("age" not in p["conditions"][0] for p in duur)
    leeftijd = [p for p in vakantie["paidLeave"] if p.get("conditions", [{}])[0].get("conditionType") == "Age"]
    assert [p["conditions"][0]["age"] for p in leeftijd] == ["45", "55"]  # tekst, geen getal
    # Bijzonder verlof komt achteraan in leave (leave_EXTRA_LEAVES)
    assert namen[-1] == "Bijzonder verlof: null dagen in het geval van: null"
