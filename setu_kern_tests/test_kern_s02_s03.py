"""02 Beloning en 03 Functiegroepen: formulier → antwoorden → SETU, vergeleken met de webform."""

import datetime as dt

import pytest

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.codes import JaNee
from setu_kern.bronnen.wijzerbelonen.formulier.s02_beloning import (
    AfwijkendRooster,
    BeloningInterval,
    EenmaligeVerhogingType,
    NormaleArbeidsduur,
    PeriodiekeVerhoging,
    Salarisschaal,
    Salaristabel,
    Stap,
    VerhogingBerekening,
    VerhogingWanneer,
    WerkervaringInschaling,
)
from setu_kern.bronnen.wijzerbelonen.formulier.s03_functiegroepen import Functiegroep
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import naar_antwoorden
from referentie_kern.controle import antwoord_problemen, vergelijk_setu


def _schaal(naam: str, stappen: list[tuple[str, float]], minimaal: float | None = None, maximaal: float | None = None):
    return Salarisschaal(
        naam=naam,
        minimaal_bedrag=minimaal,
        maximaal_bedrag=maximaal,
        stappen=[Stap(naam=n, bedrag=b) for n, b in stappen],
    )


def _rijk() -> Formulier:
    """Twee salaristabellen, meerdere schalen en stappen, alle periodieke rijen, roosters en functiegroepen."""
    f = Formulier()
    b = f.beloning
    b.betaalde_rusttijden_en_pauzes = JaNee.JA
    b.betaalde_rusttijden_namelijk = "15 minuten per 4 uur"

    t0 = Salaristabel(
        naam="Tabel 2026",
        geldig_vanaf=dt.date(2026, 1, 1),
        geldig_per=dt.date(2026, 12, 31),
        normale_arbeidsduur=NormaleArbeidsduur.UUR_38,
        beloning_vastgesteld=BeloningInterval.PER_MAAND,
        uurlonen_vastgelegd=JaNee.JA,
        uurlonen_percentage=0.6,
        salarisschalen=[
            _schaal("A", [("0", 2100.0), ("1", 2175.5), ("2", 2250)], minimaal=2100, maximaal=2250),
            _schaal("B", [("0", 2400.0), ("1", 2480.25)]),
            _schaal("C", [("0", 2700)], maximaal=2900.5),
        ],
        werkervaring_inschaling=WerkervaringInschaling.JA_SECTOR,
        werkervaring_sector="1 trede per 2 jaar ervaring",
        periodieke_verhogingen=JaNee.JA,
        minimale_duur_dienstverband=PeriodiekeVerhoging(
            aangevinkt=True,
            wanneer=VerhogingWanneer.VAST_MOMENT,
            wanneer_vast_moment=dt.date(2026, 7, 1),
            berekening=VerhogingBerekening.VAST_PERCENTAGE,
            berekening_vast_percentage=2.5,
        ),
        beoordeling_werknemer=PeriodiekeVerhoging(
            aangevinkt=True,
            wanneer=VerhogingWanneer.GEWERKT_JAAR,
            berekening=VerhogingBerekening.VAST_BEDRAG,
            berekening_vast_bedrag=50,
        ),
        periodiek_ja=PeriodiekeVerhoging(
            aangevinkt=True,
            wanneer=VerhogingWanneer.ANDERS,
            wanneer_anders="Na de jaarlijkse beoordeling",
            berekening=VerhogingBerekening.TREDEN,
            berekening_treden=1,
        ),
        andere_verhogingen=PeriodiekeVerhoging(
            aangevinkt=True,
            berekening=VerhogingBerekening.ANDERS,
            berekening_anders="Naar keuze van de directie",
        ),
        initiele_eenmalige_verhogingen=JaNee.JA,
        eenmalig_type=EenmaligeVerhogingType.EURO,
        eenmalig_euro=250,
        eenmalig_geldig_vanaf=dt.date(2026, 4, 1),
        eenmalig_beschrijving="Eenmalig bij de start van de cao",
        afwijkende_arbeidsduur=JaNee.JA,
        afwijkende_roosters=[
            AfwijkendRooster(
                arbeidsduur=36,
                arbeidsduur_per=BeloningInterval.PER_WEEK,
                in_situatie="Vijfploegendienst",
                uurloon_factor_vastgelegd=JaNee.JA,
                uurloon_factor=0.65,
            ),
            AfwijkendRooster(
                arbeidsduur=160.5,
                arbeidsduur_per=BeloningInterval.PER_VIER_WEKEN,
                in_situatie="Drieploegendienst",
                uurloon_factor_vastgelegd=JaNee.NEE,
            ),
        ],
    )
    t1 = Salaristabel(
        naam="Tabel ploegendienst",
        geldig_vanaf=dt.date(2026, 7, 1),
        voorwaarden="Bij werken in een vijfploegendienst",
        normale_arbeidsduur=NormaleArbeidsduur.ANDERS,
        normale_arbeidsduur_anders=33.6,
        beloning_vastgesteld=BeloningInterval.PER_UUR,
        salarisschalen=[_schaal("P1", [("a", 15.5), ("b", 16.25)])],
        werkervaring_inschaling=WerkervaringInschaling.NEE,
        periodieke_verhogingen=JaNee.NEE,
        initiele_eenmalige_verhogingen=JaNee.JA,
        eenmalig_type=EenmaligeVerhogingType.PERCENTAGE,
        eenmalig_percentage=3,
        eenmalig_beschrijving="Voor iedereen",
        afwijkende_arbeidsduur=JaNee.JA,
        afwijkende_roosters=[AfwijkendRooster(arbeidsduur=30, in_situatie="Weekenddienst")],
    )
    b.beloningen = [t0, t1]

    f.functiegroepen.functie_groepen = [
        Functiegroep(titel="Operator", code="OP-1", salarisschaal="0,1"),
        Functiegroep(titel="Monteur", salarisschaal="1,0"),
        Functiegroep(titel="Planner", code="PL", salarisschaal="0,1"),
        Functiegroep(titel="Stagiair"),
    ]
    return f


def _half() -> Formulier:
    """Half ingevuld: ontbrekende toelichtingen, verhoging zonder type, rooster zonder arbeidsduur."""
    f = Formulier()
    b = f.beloning
    b.betaalde_rusttijden_en_pauzes = JaNee.JA  # zonder toelichting: de webform schrijft "null"
    t0 = Salaristabel(
        naam="Enige tabel",
        normale_arbeidsduur=NormaleArbeidsduur.UUR_40,
        uurlonen_vastgelegd=JaNee.JA,  # zonder percentage
        salarisschalen=[_schaal("1", [("0", 1900)]), Salarisschaal(naam="2")],
        werkervaring_inschaling=WerkervaringInschaling.JA_ALS_VOLGT,
        periodieke_verhogingen=JaNee.JA,
        minimale_duur_dienstverband=PeriodiekeVerhoging(aangevinkt=True),
        periodiek_ja=PeriodiekeVerhoging(
            aangevinkt=True, wanneer=VerhogingWanneer.ANDERS, berekening=VerhogingBerekening.VAST_PERCENTAGE
        ),
        andere_verhogingen=PeriodiekeVerhoging(
            aangevinkt=True, wanneer=VerhogingWanneer.VAST_MOMENT, berekening=VerhogingBerekening.ANDERS
        ),
        initiele_eenmalige_verhogingen=JaNee.JA,  # zonder type en datum
        afwijkende_arbeidsduur=JaNee.JA,
        afwijkende_roosters=[
            AfwijkendRooster(in_situatie="Nachtdienst"),
            AfwijkendRooster(uurloon_factor_vastgelegd=JaNee.JA),
        ],
    )
    b.beloningen = [t0]
    f.functiegroepen.functie_groepen = [
        Functiegroep(titel="Zonder schaal"),
        Functiegroep(code="X1", salarisschaal="0,1"),  # zonder titel; schaal "2" heeft alleen een naam
    ]
    return f


def _alleen_functiegroepen() -> Formulier:
    """Functiegroepen die naar een salarisschaal verwijzen die niet in de SETU staat (geen remuneration)."""
    f = Formulier()
    f.functiegroepen.functie_groepen = [
        Functiegroep(titel="Chauffeur", salarisschaal="0,0"),
        Functiegroep(titel="Bijrijder", code="BR"),
    ]
    return f


def _varianten() -> list[Formulier]:
    """Alle radio-takken van werkervaring, arbeidsduur, beloning vastgesteld en afwijkende roosters."""
    uit = []
    werkervaring = {
        WerkervaringInschaling.JA_SECTOR: "werkervaring_sector",
        WerkervaringInschaling.JA_ONDERNEMING: "werkervaring_onderneming",
        WerkervaringInschaling.JA_FUNCTIE: "werkervaring_functie",
        WerkervaringInschaling.JA_ALS_VOLGT: "werkervaring_als_volgt",
        WerkervaringInschaling.NEE: None,
    }
    duren = list(NormaleArbeidsduur)
    intervallen = list(BeloningInterval)
    for n, (optie, veld) in enumerate(werkervaring.items()):
        t = Salaristabel(
            naam=f"Variant {n}",
            normale_arbeidsduur=duren[n % len(duren)],
            beloning_vastgesteld=intervallen[n % len(intervallen)],
            salarisschalen=[_schaal("S1", [("0", 2000 + n)]), _schaal("S2", [("0", 2500), ("1", 2600)])],
            werkervaring_inschaling=optie,
            afwijkende_arbeidsduur=JaNee.JA if n % 2 else JaNee.NEE,
        )
        if t.normale_arbeidsduur == NormaleArbeidsduur.ANDERS:
            t.normale_arbeidsduur_anders = 32
        if veld:
            setattr(t, veld, f"Toelichting {optie.value}")
        if t.beloning_vastgesteld != BeloningInterval.PER_UUR:
            t.uurlonen_vastgelegd = JaNee.NEE if n % 2 else JaNee.JA
            if t.uurlonen_vastgelegd == JaNee.JA:
                t.uurlonen_percentage = 100
        if t.afwijkende_arbeidsduur == JaNee.JA:
            t.afwijkende_roosters = [
                AfwijkendRooster(arbeidsduur=20, arbeidsduur_per=BeloningInterval.PER_MAAND, in_situatie="Deeltijd")
            ]
        f = Formulier()
        f.beloning.betaalde_rusttijden_en_pauzes = JaNee.NEE
        f.beloning.beloningen = [t]
        f.functiegroepen.functie_groepen = [Functiegroep(titel="Iedereen", salarisschaal="0,1")]
        uit.append(f)
    return uit


SCENARIOS = {
    "rijk": _rijk,
    "half": _half,
    "alleen-functiegroepen": _alleen_functiegroepen,
    "leeg": Formulier,
    **{f"variant-{n}": (lambda f=f: f) for n, f in enumerate(_varianten())},
}


def _verschillen(webform, antwoorden) -> list[str]:
    verschillen = vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden))
    return [v for v in verschillen if not v.startswith(".baseDefinition")]


@pytest.mark.parametrize("naam", SCENARIOS)
def test_antwoorden_passen_op_de_webform(webform, naam):
    assert antwoord_problemen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


@pytest.mark.parametrize("naam", SCENARIOS)
def test_setu_gelijk_aan_webform(webform, naam):
    assert _verschillen(webform, naar_antwoorden(SCENARIOS[naam]())) == []


def test_rijk_bevat_de_verwachte_onderdelen():
    data = naar_setu.setu_json(_rijk())
    beloningen = data["remuneration"]
    assert len(beloningen) == 2 + 3  # twee salaristabellen + drie afwijkende roosters
    assert beloningen[0]["workDuration"]["valuePerWeek"] == 38
    assert beloningen[1]["workDuration"]["valuePerWeek"] == 33.6
    assert [s["name"] for s in beloningen[0]["salaryScale"]] == ["A", "B", "C"]
    assert beloningen[0]["salaryScale"][1]["positionProfileReference"] == [
        {"positionId": {"value": "OP-1"}},
        {"positionId": {"value": "PL"}},
    ]
    # De kopieën van de afwijkende roosters zijn gemaakt vóór de functiegroepen.
    assert "positionProfileReference" not in beloningen[2]["salaryScale"][1]
    assert beloningen[2]["workDuration"]["valuePerWeek"] == 36
    assert beloningen[3]["workDuration"]["interval"] == {"value": 4, "unitCode": "Week"}
    assert data["positionProfile"][1]["positionId"]["value"] == "Monteur"  # zonder code: de titel
    assert data["allowance"][0]["typeCode"] == "HT400"


def test_half_nadoen_van_webformbugs():
    data = naar_setu.setu_json(_half())
    assert data["allowance"][0]["line"][0]["conditions"][0]["description"] == "null"
    stijging = data["remuneration"][0]["individualSalaryIncrease"]
    assert stijging[1]["line"]["conditions"][1]["description"] == "Wanneer wordt de verhoging toegekend: null"


def test_werkervaring_zonder_salaristabel_in_setu_loopt_vast(webform):
    """Zonder SETU-waarden voor de salaristabel crasht de export van de webform; wij geven een TypeError."""
    f = Formulier()
    f.beloning.beloningen = [Salaristabel(naam="Leeg", werkervaring_inschaling=WerkervaringInschaling.JA_SECTOR)]
    antwoorden = naar_antwoorden(f)
    assert antwoord_problemen(webform, antwoorden) == []
    with pytest.raises(Exception):
        webform.setu(antwoorden)
    with pytest.raises(TypeError):
        naar_setu.setu_json(antwoorden)
