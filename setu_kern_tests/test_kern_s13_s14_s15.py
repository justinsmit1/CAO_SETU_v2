"""13 Aanvullende regelingen, 14 Overig, 15 Grondslagen: formulier → antwoorden → SETU, vergeleken met de webform."""

import datetime as dt

import pytest
from pydantic import ValidationError

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage, Tijd, VastBedrag
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Grondslag, Interval, JaNee, Loonbasis
from setu_kern.bronnen.wijzerbelonen.formulier.s04_toeslagen import ToeslagSoort
from setu_kern.bronnen.wijzerbelonen.formulier.s13_aanvullende_regelingen import (
    AanvullendeRegeling,
    AanvullendeRegelingMetDekking,
    AndereSocialeRegeling,
)
from setu_kern.bronnen.wijzerbelonen.formulier.s14_overig import OverigeRegeling
from setu_kern.bronnen.wijzerbelonen.formulier.s15_grondslagen import GrondslagInstelling, ToeslagenMeegenomen
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import naar_antwoorden
from setu_kern.bronnen.wijzerbelonen.koppeling.motor import Antwoorden
from setu_kern.bronnen.wijzerbelonen.koppeling.setu_s15_grondslagen import gebruikte_grondslagen
from referentie_kern.controle import antwoord_problemen, vergelijk_setu


def _pct(grondslag: Grondslag | None = None, per: Interval | None = Interval.MAAND) -> Bedragregel:
    return Bedragregel(
        soort=BedragSoort.PERCENTAGE,
        percentage=Percentage(percentage=1.25, basis=Loonbasis.MAANDLOON, per=per, grondslag=grondslag),
    )


def _vast(bedrag: float, per: Interval | None = Interval.JAAR) -> Bedragregel:
    return Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=bedrag, per=per))


def _rijk() -> Formulier:
    """Alle takken van 13, 14 en 15, met grondslagen uit meerdere secties (ook 05 Vakantiebijslag)."""
    f = Formulier()
    f.vakantiebijslag.ja_nee = JaNee.JA
    f.vakantiebijslag.bedrag = _pct(Grondslag.BRUTO_LOON, per=Interval.JAAR)

    r = f.aanvullende_regelingen
    r.paww = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        omschrijving="Private aanvulling WW via de sector",
        werkgeverspremie=_pct(Grondslag.SV_LOON),
        werknemerspremie=_pct(Grondslag.SV_LOON),
        dekkingswaarde=_vast(2500, per=None),
    )
    r.pazw = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        werkgeverspremie=_vast(12.5, per=Interval.MAAND),
        werknemerspremie=Bedragregel(soort=BedragSoort.NVT),
        dekkingswaarde=Bedragregel(soort=BedragSoort.PERCENTAGE, percentage=Percentage(percentage=70, basis=Loonbasis.JAARLOON, grondslag=Grondslag.BASISLOON)),
    )
    r.rvu_regeling = AanvullendeRegeling(
        ja_nee=JaNee.JA, omschrijving="Generatiepact 80-90-100", werkgeverspremie=Bedragregel(soort=BedragSoort.NVT)
    )
    r.wga_hiaat = AanvullendeRegelingMetDekking(ja_nee=JaNee.NEE)
    r.ongevallenverzekering = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        omschrijving="24-uursdekking",
        werkgeverspremie=_pct(Grondslag.BASISLOON, per=Interval.JAAR),
        dekkingswaarde=Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=40)),
    )
    r.andere_ja_nee = JaNee.JA
    r.andere_regelingen.append(
        AndereSocialeRegeling(
            omschrijving="Aanvulling op de WIA",
            werkgeverspremie=_pct(Grondslag.DERTIENDE_MAAND),
            werknemerspremie=[Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=2, per=Interval.WEEK))],
        )
    )
    # Zonder omschrijving: de webform zet deze regeling niet in SETU (convertSetuValue alleen bij een waarde).
    r.andere_regelingen.append(AndereSocialeRegeling(werkgeverspremie=_vast(10), werknemerspremie=_pct(Grondslag.GEBRUIKELIJK_LOON)))
    r.andere_regelingen.append(AndereSocialeRegeling(omschrijving="Alleen een omschrijving"))

    o = f.overig
    o.ja_nee = JaNee.JA
    o.overige_regelingen.append(OverigeRegeling(naam="Fietsplan", voorwaarden="Na 1 jaar in dienst", waarde=_vast(750, Interval.EENMALIG)))
    o.overige_regelingen.append(OverigeRegeling(naam="Winstdeling", waarde=_pct(Grondslag.BRUTO_LOON, per=Interval.JAAR)))
    o.overige_regelingen.append(OverigeRegeling(naam="Extra vrije uren", voorwaarden="Vanaf 55 jaar", waarde=Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=16, per=Interval.JAAR))))
    o.overige_regelingen.append(OverigeRegeling(voorwaarden="Rij zonder naam"))  # levert geen otherArrangement op
    o.overige_regelingen.append(OverigeRegeling(naam="Alleen een naam"))

    g = f.grondslagen.per_grondslag
    g[Grondslag.BRUTO_LOON] = GrondslagInstelling(
        salaris=True, vakantietoeslag=True, betaald_verlof=True, toeslagen=ToeslagenMeegenomen.ALLE, peildatum=dt.date(2026, 7, 1)
    )
    g[Grondslag.SV_LOON] = GrondslagInstelling(
        salaris=True,
        toeslagen=ToeslagenMeegenomen.SOMMIGE,
        toeslag={ToeslagSoort.OVERWERK: True, ToeslagSoort.ONREGELMATIGHEIDSTOESLAGEN: True, ToeslagSoort.ANDERS: True},
    )
    g[Grondslag.BASISLOON] = GrondslagInstelling(betaald_verlof=True, toeslagen=ToeslagenMeegenomen.GEEN)
    g[Grondslag.DERTIENDE_MAAND] = GrondslagInstelling(toeslagen=ToeslagenMeegenomen.SOMMIGE)  # sommige, maar geen aangevinkt
    # GEBRUIKELIJK_LOON: gebruikt (andere regeling zonder omschrijving) maar niets ingevuld → toch een baseDefinition.
    return f


def _half() -> Formulier:
    """Half ingevuld: regelingen op ja zonder verdere antwoorden, rijen zonder ja/nee, grondslag zonder instellingen."""
    f = Formulier()
    r = f.aanvullende_regelingen
    r.paww = AanvullendeRegelingMetDekking(ja_nee=JaNee.JA)
    r.rvu_regeling = AanvullendeRegeling(ja_nee=JaNee.JA, werknemerspremie=Bedragregel(soort=BedragSoort.PERCENTAGE))
    r.pazw = AanvullendeRegelingMetDekking(ja_nee=JaNee.NEE)
    # Rijen zonder ja/nee-antwoord: de rijen hebben geen showIf en gaan dus toch mee.
    r.andere_regelingen.append(AndereSocialeRegeling(omschrijving="Half", werkgeverspremie=Bedragregel(soort=BedragSoort.PERCENTAGE, percentage=Percentage(grondslag=Grondslag.PENSIOEN))))
    f.overig.ja_nee = JaNee.JA
    f.overig.overige_regelingen.append(OverigeRegeling(naam="Nog in te vullen"))
    f.overig.overige_regelingen.append(OverigeRegeling())
    return f


def _alleen_nee() -> Formulier:
    f = Formulier()
    r = f.aanvullende_regelingen
    for naam in ("paww", "pazw", "wga_hiaat", "ongevallenverzekering"):
        setattr(r, naam, AanvullendeRegelingMetDekking(ja_nee=JaNee.NEE))
    r.rvu_regeling = AanvullendeRegeling(ja_nee=JaNee.NEE)
    r.andere_ja_nee = JaNee.NEE
    f.overig.ja_nee = JaNee.NEE
    return f


SCENARIOS = {"rijk": _rijk, "half": _half, "alleen_nee": _alleen_nee, "leeg": Formulier}


@pytest.mark.parametrize("naam", SCENARIOS)
def test_antwoorden_passen_op_de_webform(webform, naam):
    assert antwoord_problemen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


@pytest.mark.parametrize("naam", SCENARIOS)
def test_setu_gelijk_aan_webform(webform, naam):
    antwoorden = naar_antwoorden(SCENARIOS[naam]())
    assert vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden)) == []


def test_rijk_raakt_alle_takken():
    antwoorden = naar_antwoorden(_rijk())
    data = naar_setu.setu_json(antwoorden)
    assert [s["typeCode"] for s in data["supplementaryArrangement"]] == ["PAWW", "PAZW", "RVU", "AccidentBenefit"]
    namen = [o["name"] for o in data["otherArrangement"]]
    assert namen == ["Fietsplan", "Winstdeling", "Extra vrije uren", "Alleen een naam"] + [
        "Andere aanvullende sociale zekerheidsregeling"
    ] * 2
    assert gebruikte_grondslagen(Antwoorden(antwoorden)) == [
        "GrossSalary", "SocialInsuranceWage", "BaseWage", "13thMonth", "UsualWage"
    ]
    assert [b["baseType"] for b in data["baseDefinition"]] == gebruikte_grondslagen(Antwoorden(antwoorden))
    assert data["baseDefinition"][1]["allowances"] == [{"typeCode": "HT320"}, {"typeCode": "HT200"}, {"typeCode": "EA300"}]


def test_andere_premie_structuur():
    antwoorden = naar_antwoorden(_rijk())
    rij = antwoorden["andere-sociale-regelingen"][0]
    assert rij["werkgeverspremie"] == [
        {
            "amount-type": "percentage",
            "percentage/percentage": "1.25",
            "percentage/basis": "MonthlyRate",
            "percentage/per": "Month",
            "percentage/grondslag": "13thMonth",
        }
    ]
    with pytest.raises(ValidationError, match="niet toegestaan"):
        AndereSocialeRegeling(werkgeverspremie=Bedragregel(soort=BedragSoort.NVT))
    with pytest.raises(ValidationError):
        AndereSocialeRegeling(werkgeverspremie=[_vast(1), _vast(2)])


# --- grondslagen uit andere secties, rechtstreeks als antwoorden (alleen .baseDefinition vergeleken)
def _alleen_grondslagen(verschillen: list[str]) -> list[str]:
    return [v for v in verschillen if v.startswith(".baseDefinition")]


RUWE_ANTWOORDEN = {
    "uit_andere_secties": {
        # Individueel keuzebudget, toeslagvarianten, loondoorbetaling bij ziekte.
        "individueel-keuzebudget/percentage/grondslag": "HolidayAllowance",
        "overwerktoeslag/enabled": True,
        "overwerktoeslag": [{"amount-type": "percentage", "percentage/grondslag": "BaseWage"}, {"amount-type": "percentage", "percentage/grondslag": "UsualWage"}],
        "ploegentoeslagen": [{"amount-type": "percentage", "percentage/grondslag": "UsualWage"}],
        "loondoorbetaling-bij-ziekte": [{"grondslag": "SocialInsuranceWage"}, {}],
        "grondslag/UsualWage/salaris": True,
        "grondslag/UsualWage/toeslagen": "some",
        "grondslag/UsualWage/toeslag-ploegentoeslagen": True,
        "grondslag/UsualWage/toeslag-performancetoeslag": True,
        "grondslag/HolidayAllowance/peildatum": 1767222000000,
    },
    "pensioen_bug_ja": {
        # De webform leest "pensioenregeling" (bestaat niet als vraag): alleen dan verschijnt "Pension".
        "pensioenregeling": "ja",
        "grondslag/Pension/vakantietoeslag": True,
    },
    "pensioen_bug_echte_vraag": {"pensioenregeling/van-toepassing": "ja"},
    "verborgen_grondslag_telt_mee": {
        # Soort gewijzigd na het kiezen van een grondslag: het oude antwoord blijft staan en telt mee.
        "vakantiebijslag/ja-nee": "nee",
        "vakantiebijslag/amount-type": "vast-bedrag",
        "vakantiebijslag/percentage/grondslag": "13thMonth",
        "overige-regelingen-ja-nee": "nee",
        "overige-regelingen": [{"naam": "Verborgen", "percentage/grondslag": "BaseWage"}],
    },
    "dubbele_codes": {
        "vakantiebijslag/percentage/grondslag": "BaseWage",
        "individueel-keuzebudget/percentage/grondslag": "BaseWage",
        "aanvullende-sociale-zekerheidsregelingen/wga-hiaat/werknemerspremie/percentage/grondslag": "GrossSalary",
        "andere-sociale-regelingen": [{"werknemerspremie": [{"percentage/grondslag": "BaseWage"}]}],
    },
}


@pytest.mark.parametrize("naam", RUWE_ANTWOORDEN)
def test_grondslagen_uit_ruwe_antwoorden(webform, naam):
    antwoorden = {**naar_antwoorden(Formulier()), **RUWE_ANTWOORDEN[naam]}
    assert _alleen_grondslagen(vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))) == []


def test_pensioen_bug():
    assert gebruikte_grondslagen(Antwoorden(RUWE_ANTWOORDEN["pensioen_bug_ja"])) == ["Pension"]
    assert gebruikte_grondslagen(Antwoorden(RUWE_ANTWOORDEN["pensioen_bug_echte_vraag"])) == []


def test_overig_verborgen_rijen_niet_in_setu(webform):
    antwoorden = {**naar_antwoorden(Formulier()), **RUWE_ANTWOORDEN["verborgen_grondslag_telt_mee"]}
    data = naar_setu.setu_json(antwoorden)
    assert "otherArrangement" not in data
    assert [b["baseType"] for b in data["baseDefinition"]] == ["13thMonth", "BaseWage"]
    assert vergelijk_setu(webform, antwoorden, data) == []
