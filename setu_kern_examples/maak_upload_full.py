"""Het VOLLEDIGE voorbeeld: elk onderdeel van het formulier uit ``INVULHULP.md`` wordt hier gebruikt.

Draaien vanuit de projectmap:

    .venv\\Scripts\\python.exe setu_kern_examples\\maak_upload_full.py

Schrijft ``uitvoer\\setu_kern\\wijzerbelonen_upload_full.json`` (uploaden op wijzerbelonen.nl) en
``uitvoer\\setu_kern\\setu_kernmodel_full.json``.

Waarvoor:
- Als naslag: zie je in ``INVULHULP.md`` een vraag, dan vind je hier een werkend voorbeeld.
- Als test: na het uploaden zie je op de website hoe elk onderdeel eruitziet.

Bij een keuzevraag kan maar één optie tegelijk. Waar het formulier meerdere rijen of variaties toestaat, laten de
extra rijen de andere opties zien. Een paar vragen kunnen niet tegelijk (bijv. "geen toeslagen" naast toeslagen); dat
staat er als commentaar bij.

Het verwerken (controleren, uploadbestand, SETU-kernmodel, controle met de webform) gebeurt met dezelfde code als in
``maak_upload.py``.
"""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from maak_upload import PROJECT, verwerk  # noqa: E402

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier  # noqa: E402
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage, Tijd, VastBedrag  # noqa: E402
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Grondslag, Interval, JaNee, Loonbasis, Peildatum  # noqa: E402

UITVOER = PROJECT / "uitvoer" / "setu_kern" / "wijzerbelonen_upload_full.json"
KERNMODEL_UITVOER = PROJECT / "uitvoer" / "setu_kern" / "setu_kernmodel_full.json"


def _vast(bedrag: float, per: Interval | None = None) -> Bedragregel:
    return Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=bedrag, per=per))


def _pct(percentage: float, basis: Loonbasis, per: Interval | None = None, grondslag: Grondslag | None = None) -> Bedragregel:
    return Bedragregel(
        soort=BedragSoort.PERCENTAGE,
        percentage=Percentage(percentage=percentage, basis=basis, per=per, grondslag=grondslag),
    )


def _tijd(uur: float, per: Interval | None = None) -> Bedragregel:
    return Bedragregel(soort=BedragSoort.TIJD, tijd=Tijd(uur=uur, per=per))


# ======================================================================================================================
# 01 · Algemeen: alle vragen (cao én eigen regeling, algemeen verbindend met periode)
# ======================================================================================================================
def vul_algemeen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s01_algemeen import CaoOfRegeling, CaoVanToepassingOmdat, TypeIdentificatienummer

    a = f.algemeen
    a.naam_regeling = "Volledig voorbeeld 2026"
    a.geldig_van = dt.date(2026, 1, 1)
    a.geldig_tot = dt.date(2026, 12, 31)
    a.opdrachtgever_naam = "Voorbeeld Techniek B.V."
    a.opdrachtgever_kvk = "87654321"
    a.opdrachtgever_kvk_type = TypeIdentificatienummer.KVK
    a.sector = "Metaal en techniek"
    a.cao_of_regeling = CaoOfRegeling.CAO_EN_EIGEN_REGELING
    a.cao_naam = "Cao Metaal & Techniek"
    a.cao_nummer = "1234"
    a.cao_van_toepassing_omdat = CaoVanToepassingOmdat.ALGEMEEN_VERBINDEND
    a.cao_van = dt.date(2025, 6, 1)
    a.cao_tot = dt.date(2027, 5, 31)


# ======================================================================================================================
# 02 · Beloning: twee salaristabellen, alle periodieke rijen, eenmalige verhoging, afwijkende roosters
# ======================================================================================================================
def vul_beloning(f: Formulier) -> None:
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

    b = f.beloning
    b.betaalde_rusttijden_en_pauzes = JaNee.JA
    b.betaalde_rusttijden_namelijk = "15 minuten betaalde pauze per 4 uur werk"

    dagtabel = Salaristabel(
        naam="Salaristabel dagdienst 2026",
        geldig_vanaf=dt.date(2026, 1, 1),
        geldig_per=dt.date(2026, 12, 31),
        normale_arbeidsduur=NormaleArbeidsduur.UUR_38,
        beloning_vastgesteld=BeloningInterval.PER_MAAND,
        uurlonen_vastgelegd=JaNee.JA,
        uurlonen_percentage=0.6,
        salarisschalen=[
            Salarisschaal(
                naam="A",
                minimaal_bedrag=2300,
                maximaal_bedrag=2600,
                stappen=[Stap(naam="0", bedrag=2300), Stap(naam="1", bedrag=2450), Stap(naam="2", bedrag=2600)],
            ),
            Salarisschaal(
                naam="B",
                minimaal_bedrag=2700,
                maximaal_bedrag=3100,
                stappen=[Stap(naam="0", bedrag=2700), Stap(naam="1", bedrag=2900), Stap(naam="2", bedrag=3100)],
            ),
        ],
        werkervaring_inschaling=WerkervaringInschaling.JA_SECTOR,
        werkervaring_sector="Per 2 jaar relevante ervaring in de sector 1 trede hoger, maximaal 3 treden",
        periodieke_verhogingen=JaNee.JA,
        minimale_duur_dienstverband=PeriodiekeVerhoging(
            aangevinkt=True,
            wanneer=VerhogingWanneer.VAST_MOMENT,
            wanneer_vast_moment=dt.date(2026, 7, 1),
            berekening=VerhogingBerekening.TREDEN,
            berekening_treden=1,
        ),
        beoordeling_werknemer=PeriodiekeVerhoging(
            aangevinkt=True,
            wanneer=VerhogingWanneer.GEWERKT_JAAR,
            berekening=VerhogingBerekening.VAST_PERCENTAGE,
            berekening_vast_percentage=2.5,
        ),
        periodiek_ja=PeriodiekeVerhoging(
            aangevinkt=True,
            wanneer=VerhogingWanneer.ANDERS,
            wanneer_anders="Na de jaarlijkse beoordeling in januari",
            berekening=VerhogingBerekening.VAST_BEDRAG,
            berekening_vast_bedrag=50,
        ),
        andere_verhogingen=PeriodiekeVerhoging(
            aangevinkt=True,
            wanneer=VerhogingWanneer.GEWERKT_JAAR,
            berekening=VerhogingBerekening.ANDERS,
            berekening_anders="Naar beoordeling van de leidinggevende",
        ),
        initiele_eenmalige_verhogingen=JaNee.JA,
        eenmalig_type=EenmaligeVerhogingType.PERCENTAGE,
        eenmalig_percentage=3,
        eenmalig_geldig_vanaf=dt.date(2026, 4, 1),
        eenmalig_beschrijving="Structurele loonsverhoging volgens de cao",
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
                arbeidsduur=152,
                arbeidsduur_per=BeloningInterval.PER_VIER_WEKEN,
                in_situatie="Drieploegendienst",
                uurloon_factor_vastgelegd=JaNee.NEE,
            ),
        ],
    )
    uurtabel = Salaristabel(
        naam="Salaristabel oproepkrachten",
        geldig_vanaf=dt.date(2026, 1, 1),
        voorwaarden="Voor oproepkrachten zonder vaste arbeidsduur",  # alleen vanaf de 2e salaristabel
        normale_arbeidsduur=NormaleArbeidsduur.ANDERS,
        normale_arbeidsduur_anders=24,
        beloning_vastgesteld=BeloningInterval.PER_UUR,
        salarisschalen=[Salarisschaal(naam="O1", stappen=[Stap(naam="0", bedrag=14.5), Stap(naam="1", bedrag=15.25)])],
        werkervaring_inschaling=WerkervaringInschaling.JA_ALS_VOLGT,
        werkervaring_als_volgt="Ervaring wordt niet meegeteld bij oproepkrachten",
        periodieke_verhogingen=JaNee.NEE,
        initiele_eenmalige_verhogingen=JaNee.JA,
        eenmalig_type=EenmaligeVerhogingType.EURO,
        eenmalig_euro=250,
        eenmalig_geldig_vanaf=dt.date(2026, 7, 1),
        eenmalig_beschrijving="Eenmalige uitkering bij de start",
        afwijkende_arbeidsduur=JaNee.NEE,
    )
    # Nog twee kleine tabellen, om de andere keuzes bij werkervaring te laten zien.
    stagetabel = Salaristabel(
        naam="Salaristabel stagiairs",
        voorwaarden="Voor stagiairs en leerlingen (BBL)",
        normale_arbeidsduur=NormaleArbeidsduur.UUR_36,
        beloning_vastgesteld=BeloningInterval.PER_VIER_WEKEN,
        uurlonen_vastgelegd=JaNee.NEE,
        salarisschalen=[Salarisschaal(naam="S1", stappen=[Stap(naam="0", bedrag=1400)])],
        werkervaring_inschaling=WerkervaringInschaling.JA_ONDERNEMING,
        werkervaring_onderneming="Eerdere stages bij onze onderneming tellen mee",
        periodieke_verhogingen=JaNee.NEE,
        initiele_eenmalige_verhogingen=JaNee.NEE,
        afwijkende_arbeidsduur=JaNee.NEE,
    )
    weektabel = Salaristabel(
        naam="Salaristabel weekloners",
        voorwaarden="Voor werknemers met een weekloon",
        normale_arbeidsduur=NormaleArbeidsduur.UUR_40,
        beloning_vastgesteld=BeloningInterval.PER_WEEK,
        uurlonen_vastgelegd=JaNee.NEE,
        salarisschalen=[Salarisschaal(naam="W1", stappen=[Stap(naam="0", bedrag=650)])],
        werkervaring_inschaling=WerkervaringInschaling.JA_FUNCTIE,
        werkervaring_functie="Ervaring in dezelfde functie telt volledig mee",
        periodieke_verhogingen=JaNee.NEE,
        initiele_eenmalige_verhogingen=JaNee.NEE,
        afwijkende_arbeidsduur=JaNee.NEE,
    )
    b.beloningen = [dagtabel, uurtabel, stagetabel, weektabel]


# ======================================================================================================================
# 03 · Functiegroepen: met en zonder code, verschillende tabellen en schalen
# ======================================================================================================================
def vul_functiegroepen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s03_functiegroepen import Functiegroep

    f.functiegroepen.functie_groepen = [
        Functiegroep(titel="Monteur", code="MON", salarisschaal="0,0"),  # tabel 1, schaal A
        Functiegroep(titel="Werkvoorbereider", code="WVB", salarisschaal="0,1"),  # tabel 1, schaal B
        Functiegroep(titel="Oproepkracht productie", salarisschaal="1,0"),  # tabel 2, schaal O1 (zonder code)
    ]


# ======================================================================================================================
# 04 · Toeslagen: alle 9 soorten, elke bedragsoort, periodes, cumulatief, compounding en afbouwregeling
# ======================================================================================================================
def vul_toeslagen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s04_toeslagen import (
        Cumulatief,
        ToepassingsperiodesType,
        Toepassingsperiode,
        ToeslagSoort,
        ToeslagVariatie,
    )

    t = f.toeslagen
    # t.geen_toeslagen = True kan niet samen met toeslagen: dan geen van de soorten hieronder aanvinken.
    t.onregelmatigheids_toeslagen_aan = True
    t.ploegentoeslagen_aan = True
    t.toeslagen_verschoven_diensten_aan = True
    t.toeslagen_fysieke_belasting_aan = True
    t.toeslagen_stand_by_aan = True
    t.overwerktoeslag_aan = True
    t.waarnemingstoeslag_aan = True
    t.performancetoeslag_aan = True
    t.anders_aan = True

    # Onregelmatigheid: twee variaties (dan mag er een omschrijving bij), met toepassingsperiodes.
    t.onregelmatigheids_toeslagen = [
        ToeslagVariatie(
            omschrijving="Avond en nacht",
            bedrag=_pct(25, Loonbasis.UURLOON, Interval.UUR),
            voorwaarden="Werken tussen 20:00 en 06:00",
            cumulatief=Cumulatief.JA_CUMULATIEF,
            cumulatief_toelichting="Opgeteld bij een eventuele ploegentoeslag",
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[
                Toepassingsperiode(
                    starttijd=dt.time(20, 0), eindtijd=dt.time(23, 59),
                    maandag=True, dinsdag=True, woensdag=True, donderdag=True, vrijdag=True,
                ),
                Toepassingsperiode(
                    starttijd=dt.time(0, 0), eindtijd=dt.time(6, 0),
                    maandag=True, dinsdag=True, woensdag=True, donderdag=True, vrijdag=True,
                ),
            ],
        ),
        ToeslagVariatie(
            omschrijving="Zon- en feestdagen",
            bedrag=_pct(100, Loonbasis.UURLOON, Interval.UUR),
            cumulatief=Cumulatief.NEE,
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[
                Toepassingsperiode(starttijd=dt.time(0, 0), eindtijd=dt.time(23, 59), zaterdag=True, zondag=True),
            ],
        ),
    ]
    # Ploegen: vast bedrag, met afbouwregeling.
    t.ploegentoeslagen = [
        ToeslagVariatie(
            bedrag=_vast(12.5, Interval.DIENST),
            voorwaarden="Drieploegendienst volgens rooster: vroege, late en nachtdienst",
            cumulatief=Cumulatief.NEE,
            afbouwregeling=JaNee.JA,
            afbouwregeling_namelijk="Bij stoppen met ploegendienst na 5 jaar: 2 jaar lang 50% van de toeslag",
        )
    ]
    # Verschoven diensten: berekend over het resultaat na de onregelmatigheidstoeslag (compounding).
    t.toeslagen_verschoven_diensten = [
        ToeslagVariatie(
            bedrag=_pct(10, Loonbasis.UURLOON, Interval.UUR),
            voorwaarden="Als de dienst meer dan 2 uur verschoven wordt",
            cumulatief=Cumulatief.JA_COMPOUNDING,
            compounding={ToeslagSoort.ONREGELMATIGHEIDSTOESLAGEN: True},
            toepassingsperiodes_type=ToepassingsperiodesType.ALTIJD,
        )
    ]
    # Fysieke belasting: in tijd.
    t.toeslagen_fysieke_belasting = [
        ToeslagVariatie(
            bedrag=_tijd(0.5, Interval.DAG),
            voorwaarden="Werken in de koelcel of bij extreme hitte",
            cumulatief=Cumulatief.NEE,
        )
    ]
    # Stand-by: percentage per uur, altijd geldig.
    t.toeslagen_stand_by = [
        ToeslagVariatie(
            bedrag=_pct(20, Loonbasis.UURLOON, Interval.UUR),
            voorwaarden="Werken tijdens een bereikbaarheidsdienst",
            cumulatief=Cumulatief.NEE,
            toepassingsperiodes_type=ToepassingsperiodesType.ALTIJD,
        )
    ]
    # Overwerk.
    t.overwerktoeslag = [
        ToeslagVariatie(
            bedrag=_pct(125, Loonbasis.UURLOON, Interval.UUR),
            voorwaarden="Voor elk uur boven de 38 uur per week",
            cumulatief=Cumulatief.NEE,
            toepassingsperiodes_type=ToepassingsperiodesType.ALTIJD,
        )
    ]
    # Waarneming en performance: vast bedrag per maand, zonder afbouwregeling.
    t.waarnemingstoeslag = [
        ToeslagVariatie(
            bedrag=_vast(150, Interval.MAAND),
            voorwaarden="Bij waarneming van een hogere functie langer dan 2 weken",
            cumulatief=Cumulatief.NEE,
            afbouwregeling=JaNee.NEE,
        )
    ]
    t.performancetoeslag = [
        ToeslagVariatie(
            bedrag=_pct(5, Loonbasis.MAANDLOON, Interval.MAAND),
            voorwaarden="Bij een beoordeling 'goed' of hoger",
            cumulatief=Cumulatief.NEE,
            afbouwregeling=JaNee.NEE,
        )
    ]
    # Anders: met eigen naam en een datumbereik in de toepassingsperiode.
    t.anders = [
        ToeslagVariatie(
            naam="Vuilwerktoeslag",
            bedrag=_vast(2, Interval.UUR),
            voorwaarden="Werkzaamheden in sterk vervuilde ruimtes",
            cumulatief=Cumulatief.NEE,
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[
                Toepassingsperiode(startdatum=dt.date(2026, 3, 1), einddatum=dt.date(2026, 10, 31)),
            ],
            afbouwregeling=JaNee.NEE,
        )
    ]


# ======================================================================================================================
# 05 · Vakantiebijslag
# ======================================================================================================================
def vul_vakantiebijslag(f: Formulier) -> None:
    f.vakantiebijslag.ja_nee = JaNee.JA
    f.vakantiebijslag.bedrag = _pct(8, Loonbasis.JAARLOON, Interval.JAAR, grondslag=Grondslag.BRUTO_LOON)


# ======================================================================================================================
# 06 · Vergoedingen: alle reiskosten, reisuren, stand-by, zorg, thuiswerk, mobiliteit en kosten
# ======================================================================================================================
def vul_vergoedingen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s06_vergoedingen import (
        EigenVervoerType,
        EigenVervoerVariatie,
        KostenVergoeding,
        MobiliteitsRegeling,
        MobiliteitsRegelingMetAlternatief,
        OvType,
        OvVergoeding,
        ReistijdVergoeding,
        StandByType,
        Tijdvak,
        TijdvakKosten,
        TijdvakReisuren,  # noqa: F401  (gebruikt in het commentaar bij reisuren)
        TijdvakStandBy,
        ZorgverzekeringType,
    )

    v = f.vergoedingen

    # Reiskosten
    r = v.reiskosten
    r.kent_eigen_vervoer = True
    r.kent_ov = True
    r.kent_zakelijke_kilometers = True
    r.kent_zakelijke_kilometers_ov = True
    r.kent_andere = True
    r.eigen_vervoer = [  # elke soort vergoeding als eigen variatie
        EigenVervoerVariatie(type=EigenVervoerType.STANDAARD_TARIEF, voorwaarden="Auto, vanaf 10 km enkele reis"),
        EigenVervoerVariatie(type=EigenVervoerType.ANDER_TARIEF_PER_KM, ander_tarief_per_km_bedrag=0.19, voorwaarden="Fiets"),
        EigenVervoerVariatie(type=EigenVervoerType.PER_TIJDVAK, per_tijdvak_bedrag=60, per_tijdvak_type=Tijdvak.MAAND, voorwaarden="Bromfiets"),
        EigenVervoerVariatie(type=EigenVervoerType.ANDERS, anders_namelijk="Carpoolvergoeding volgens regeling", voorwaarden="Bij carpoolen"),
    ]
    r.ov = OvVergoeding(type=OvType.VOLLEDIGE_VERGOEDING, voorwaarden="Op basis van het tweede-klas-tarief")
    r.zakelijke_kilometers = [
        EigenVervoerVariatie(type=EigenVervoerType.ANDER_TARIEF_PER_KM, ander_tarief_per_km_bedrag=0.25, voorwaarden="Met eigen auto voor klantbezoek"),
    ]
    r.zakelijke_kilometers_ov = OvVergoeding(type=OvType.PER_KILOMETER, per_kilometer_bedrag=0.15, voorwaarden="Tussen projectlocaties")
    # Andere OV-keuzes: OvType.PER_RIT (per_rit_bedrag=...), OvType.PER_TRAJECT (per_traject_bedrag=...),
    #                   OvType.ANDERS (anders_namelijk="...")
    r.andere_namelijk = "Parkeerkosten bij projectlocaties worden vergoed op declaratiebasis"

    # Reisuren
    v.reisuren.vergoeding = ReistijdVergoeding.PERCENTAGE
    v.reisuren.percentage = 100
    v.reisuren.percentage_van = Loonbasis.UURLOON
    v.reisuren.percentage_tijdvak = Tijdvak.UUR
    v.reisuren.voorwaarden = "Reistijd boven 1 uur per dag naar een projectlocatie"
    # Of een vaste vergoeding:  v.reisuren.vergoeding = ReistijdVergoeding.VASTE_VERGOEDING
    #                           v.reisuren.vaste_vergoeding_bedrag = 10; v.reisuren.vaste_vergoeding_per = TijdvakReisuren.UUR
    # Of anders:                v.reisuren.vergoeding = ReistijdVergoeding.ANDERS; v.reisuren.anders_namelijk = "..." 

    # Stand-by
    v.stand_by.ja_nee = JaNee.JA
    v.stand_by.type = StandByType.VERGOEDING_PER_TIJDVAK
    v.stand_by.vast_bedrag = 35
    v.stand_by.vast_tijdvak = TijdvakStandBy.DIENST
    v.stand_by.voorwaarden = "Per piketdienst van 24 uur"
    # Of een percentage:  v.stand_by.type = StandByType.PERCENTAGE_PER_TIJDVAK; v.stand_by.percentage = 20
    #                     v.stand_by.percentage_van = Loonbasis.UURLOON; v.stand_by.percentage_tijdvak = TijdvakStandBy.UUR
    # Of anders:          v.stand_by.type = StandByType.ANDERS; v.stand_by.anders_namelijk = "..." 

    # Zorgverzekering
    z = v.zorgverzekering
    z.ja_nee = JaNee.JA
    z.type = ZorgverzekeringType.VERGOEDING_PER_TIJDSEENHEID
    z.bedrag = 10
    z.tijdvak = Tijdvak.MAAND
    z.min_max = JaNee.JA
    z.minimum = 5
    z.maximum = 15
    z.naar_rato = JaNee.JA
    z.voorwaarden = "Alleen bij deelname aan de collectieve zorgverzekering"
    # Of anders:  z.type = ZorgverzekeringType.ANDERS; z.anders_namelijk = "..." (dan geen bedrag, min/max en naar rato)

    # Thuiswerk en internet
    th = v.thuiswerk
    th.ja_nee = JaNee.JA
    th.bedrag = 2.35
    th.tijdvak = Tijdvak.DAG
    th.voorwaarden = "Per volledige thuiswerkdag"
    th.naar_rato = JaNee.NEE
    th.internet_inbegrepen = JaNee.NEE
    th.extra_internet = JaNee.JA
    th.internet_bedrag = 20
    th.internet_tijdvak = Tijdvak.MAAND
    th.internet_voorwaarden = "Bij minimaal 2 thuiswerkdagen per week"
    th.internet_naar_rato = JaNee.JA

    # Mobiliteit: alle vijf regelingen; de leaseregelingen en OV hebben ook een alternatief
    m = v.mobiliteit
    m.mobiliteitsvergoeding = MobiliteitsRegeling(
        aangevinkt=True, bedrag=100, tijdvak=Interval.MAAND, voorwaarden="Vrij te besteden aan vervoer", naar_rato=JaNee.JA
    )
    m.regeling_leaseauto = MobiliteitsRegelingMetAlternatief(
        aangevinkt=True, bedrag=550, tijdvak=Interval.MAAND, voorwaarden="Vanaf functiegroep Werkvoorbereider", naar_rato=JaNee.NEE,
        alternatief=True, alternatief_bedrag=400, alternatief_tijdvak=Interval.MAAND,
        alternatief_voorwaarden="Bruto vergoeding bij afzien van een leaseauto", alternatief_naar_rato=JaNee.NEE,
    )
    m.regeling_leasefiets = MobiliteitsRegelingMetAlternatief(
        aangevinkt=True, bedrag=40, tijdvak=Interval.MAAND, voorwaarden="Via fietsleasepartner", naar_rato=JaNee.NEE,
    )
    m.regeling_ov_vergoeding = MobiliteitsRegelingMetAlternatief(
        aangevinkt=True, bedrag=90, tijdvak=Interval.MAAND, voorwaarden="NS-Business Card", naar_rato=JaNee.NEE,
    )
    m.fietsregeling = MobiliteitsRegeling(
        aangevinkt=True, bedrag=750, tijdvak=Interval.EENMALIG, voorwaarden="Eens per 3 jaar", naar_rato=JaNee.NEE
    )

    # Kostenvergoedingen: alle zes plus anders (k.geen = True kan niet samen met deze vergoedingen)
    k = v.kosten
    k.koffiegeld = KostenVergoeding(aangevinkt=True, bedrag=1.5, tijdvak=TijdvakKosten.DAG, voorwaarden="Op werkdagen buiten kantoor", naar_rato=JaNee.NEE)
    k.maaltijdvergoeding = KostenVergoeding(aangevinkt=True, bedrag=15, tijdvak=TijdvakKosten.ITEM, voorwaarden="Bij overwerk van meer dan 2 uur", naar_rato=JaNee.NEE)
    k.wasvergoeding = KostenVergoeding(aangevinkt=True, bedrag=5, tijdvak=TijdvakKosten.WEEK, voorwaarden="Voor werkkleding", naar_rato=JaNee.JA)
    k.bedrijfskleding_schoenen = KostenVergoeding(aangevinkt=True, bedrag=150, tijdvak=TijdvakKosten.JAAR, voorwaarden="Veiligheidsschoenen S3", naar_rato=JaNee.NEE)
    k.arbo_vergoeding = KostenVergoeding(aangevinkt=True, bedrag=250, tijdvak=TijdvakKosten.JAAR, voorwaarden="Voor een ergonomische werkplek thuis", naar_rato=JaNee.NEE)
    k.byod_vergoeding = KostenVergoeding(aangevinkt=True, bedrag=15, tijdvak=TijdvakKosten.MAAND, voorwaarden="Gebruik van eigen telefoon", naar_rato=JaNee.NEE)
    k.anders = True
    k.anders_namelijk = "Vergoeding voor het behalen van een rijbewijs C"


# ======================================================================================================================
# 07 · Bijzondere uitkeringen: eenmalig, vast, jubileum en variabel, met alle voorwaarden
# ======================================================================================================================
def vul_bijzondere_uitkeringen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s07_bijzondere_uitkeringen import (
        EenmaligeUitkering,
        HoeToegekend,
        HoeToegekendVast,
        Jubileumuitkering,
        SoortVariabeleUitkering,
        VariabeleUitkering,
        VasteUitkering,
    )

    b = f.bijzondere_uitkeringen
    b.eenmalige_uitkeringen_bekend = JaNee.JA
    b.eenmalige_uitkeringen = [
        EenmaligeUitkering(
            naam="Eenmalige cao-uitkering",
            min_duur_dienstverband=True,
            min_duur_namelijk="Minimaal 3 maanden in dienst",
            dienstverband_op_datum=True,
            dienstverband_datum_namelijk="In dienst op 1 juni 2026",
            voorwaarde_anders=True,
            voorwaarde_anders_namelijk="Niet voor stagiairs",
            toekenning_datum=dt.date(2026, 6, 30),
            hoe_toegekend=HoeToegekend.VAST_BEDRAG,
            vast_bedrag=500,
            naar_rato_deeltijd=JaNee.JA,
            naar_rato_duur_dienstverband=JaNee.NEE,
            min_max=JaNee.JA,  # alleen met een bedrag: zonder bedrag loopt de webform vast
            minimum=250,
            maximum=500,
        ),
        EenmaligeUitkering(
            naam="Koopkrachtuitkering",
            toekenning_datum=dt.date(2026, 12, 1),
            hoe_toegekend=HoeToegekend.PERCENTAGE_LOON,
            percentage=1,
            percentage_van=Loonbasis.JAARLOON,
            min_max=JaNee.NEE,
        ),
        EenmaligeUitkering(
            naam="Uitkering bij afronden project",
            toekenning_datum=dt.date(2026, 9, 1),
            hoe_toegekend=HoeToegekend.ANDERS,
            anders="Bedrag afhankelijk van de projectomvang",
            min_max=JaNee.NEE,  # bij "anders" nooit min/max = ja (dan loopt de webform vast)
        ),
    ]
    b.vaste_uitkering_van_toepassing = JaNee.JA
    b.vaste_uitkeringen = [
        VasteUitkering(
            naam="Dertiende maand",
            toekenning_datum=dt.date(2026, 12, 15),
            hoe_toegekend=HoeToegekendVast.DERTIENDE_MAAND,
        ),
        VasteUitkering(
            naam="Eindejaarsuitkering",
            min_duur_dienstverband=True,
            min_duur_namelijk="Minimaal 1 jaar in dienst",
            toekenning_datum=dt.date(2026, 12, 15),
            hoe_toegekend=HoeToegekendVast.VAST_BEDRAG,
            vast_bedrag=750,
            naar_rato=JaNee.JA,
        ),
        VasteUitkering(
            naam="Vakantie-extra",
            dienstverband_op_datum=True,
            dienstverband_datum_namelijk="In dienst op 1 mei",
            voorwaarde_anders=True,
            voorwaarde_anders_namelijk="Niet tijdens onbetaald verlof",
            toekenning_datum=dt.date(2026, 5, 31),
            hoe_toegekend=HoeToegekendVast.PERCENTAGE_LOON,
            percentage=1,
            percentage_van=Loonbasis.JAARLOON,
        ),
        VasteUitkering(
            naam="Kerstpakket",
            toekenning_datum=dt.date(2026, 12, 20),
            hoe_toegekend=HoeToegekendVast.ANDERS,
            anders="Kerstpakket ter waarde van ongeveer € 75",
        ),
    ]
    b.jubileumuitkering_van_toepassing = JaNee.JA
    b.jubileumuitkeringen = [
        Jubileumuitkering(
            naam="12,5-jarig dienstjubileum",
            hoe_toegekend=HoeToegekend.VAST_BEDRAG,
            vast_bedrag=500,
            naar_rato=JaNee.NEE,
            dienstverband_jaren=12,
            dienstverband_maanden=6,
            referentiedatum=Peildatum.DATUM_INDIENSTTREDING,
            voorwaarden="Onafgebroken dienstverband",
        ),
        Jubileumuitkering(
            naam="25-jarig dienstjubileum",
            hoe_toegekend=HoeToegekend.PERCENTAGE_LOON,
            percentage=100,
            percentage_van=Loonbasis.MAANDLOON,
            dienstverband_jaren=25,
            referentiedatum=Peildatum.ANCIENNITEITSDATUM,
            toekenning_datum=dt.date(2026, 1, 1),
        ),
        Jubileumuitkering(
            naam="40-jarig dienstjubileum",
            hoe_toegekend=HoeToegekend.ANDERS,
            anders="Een extra vrije week en een cadeaubon",
            dienstverband_jaren=40,
            referentiedatum=Peildatum.STARTDATUM_CONTRACT,
        ),
    ]
    b.variabele_uitkering_van_toepassing = JaNee.JA
    b.variabele_uitkeringen = [
        VariabeleUitkering(
            soort=SoortVariabeleUitkering.WINST,
            resultaat=True,
            resultaat_namelijk="Bij een nettowinst boven 1 miljoen euro",
            dienstverband_op_datum=True,
            dienstverband_datum_namelijk="In dienst op 31 december",
            toekenning_datum=dt.date(2026, 4, 1),
            hoe_toegekend=HoeToegekend.PERCENTAGE_LOON,
            percentage=2,
            percentage_van=Loonbasis.JAARLOON,
            min_max=JaNee.JA,
            minimum=500,
            maximum=2500,
        ),
        VariabeleUitkering(
            soort=SoortVariabeleUitkering.PERFORMANCE,
            prestatie=True,
            prestatie_namelijk="Bij het behalen van de persoonlijke doelen",
            min_duur_dienstverband=True,
            min_duur_namelijk="Minimaal 6 maanden in dienst",
            voorwaarde_anders=True,
            voorwaarde_anders_namelijk="Vast te stellen door de directie",
            hoe_toegekend=HoeToegekend.VAST_BEDRAG,
            vast_bedrag=1000,
            naar_rato=JaNee.JA,
            min_max=JaNee.NEE,
        ),
        VariabeleUitkering(
            soort=SoortVariabeleUitkering.ANDERS,
            soort_anders_namelijk="Aanbrengpremie voor nieuwe collega's",
            hoe_toegekend=HoeToegekend.ANDERS,
            anders="€ 500 na afloop van de proeftijd van de nieuwe collega",
            min_max=JaNee.NEE,
        ),
    ]
    # SoortVariabeleUitkering.BONUS is de vierde keuze bij "Wat voor soort uitkering gaat het om?".


# ======================================================================================================================
# 08 · Loondoorbetaling bij ziekte: meerdere periodes, wachtdagen met voorwaarden en compensatie
# ======================================================================================================================
def vul_loondoorbetaling_bij_ziekte(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s08_loondoorbetaling_bij_ziekte import (
        LoondoorbetalingRegel,
        TijdvakZiekte,
        WachtdagcompensatieSoort,
    )

    z = f.loondoorbetaling_bij_ziekte
    z.regels = [
        LoondoorbetalingRegel(percentage=100, van=Loonbasis.MAANDLOON, grondslag=Grondslag.BASISLOON, per_tijdvak=TijdvakZiekte.JAAR, voorwaarden="Eerste ziektejaar"),
        LoondoorbetalingRegel(percentage=70, van=Loonbasis.MAANDLOON, grondslag=Grondslag.BASISLOON, per_tijdvak=TijdvakZiekte.JAAR, voorwaarden="Tweede ziektejaar"),
    ]
    z.wachtdagen = JaNee.JA
    z.wachtdagen_aantal = 1
    z.wachtdagen_voorwaarden = JaNee.JA
    z.wachtdagen_voorwaarden_namelijk = "Maximaal 2 wachtdagen per kalenderjaar"
    z.wachtdagcompensatie = JaNee.JA
    z.compensatie_soort = WachtdagcompensatieSoort.PERCENTAGE
    z.compensatie_percentage = 100
    z.compensatie_basis = Loonbasis.DAGLOON
    # Of een vast bedrag:  z.compensatie_soort = WachtdagcompensatieSoort.VAST_BEDRAG; z.compensatie_bedrag = 50


# ======================================================================================================================
# 09 · Verlof: ADV met aanvullingen, vakantiedagen met alle extra's, bijzonder verlof, Wazo, feestdagen, ...
# ======================================================================================================================
def vul_verlof(f: Formulier) -> None:
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

    v = f.verlof

    # ADV / ATV, met alle drie de aanvullende regelingen (elk een andere manier van toekennen)
    adv = v.adv_atv
    adv.adv_regeling = JaNee.JA
    adv.namelijk = "ADV volgens de cao"
    adv.toekenning = AdvToekenning(toekenning=AdvToekenningSoort.TIJD_DAGEN, dagen_aantal=13, dagen_tijdvak=Tijdvak.JAAR)
    adv.aanvullende_regeling = JaNee.JA
    adv.ouderen = True
    adv.ouderen_namelijk = "Vanaf 60 jaar"
    adv.toekenning_ouderen = AdvToekenning(toekenning=AdvToekenningSoort.TIJD_UREN, uren_aantal=4, uren_tijdvak=Tijdvak.MAAND)
    adv.duur_dienstverband = True
    adv.duur_dienstverband_namelijk = "Na 10 jaar dienstverband"
    adv.toekenning_duur_dienstverband = AdvToekenning(toekenning=AdvToekenningSoort.TIJD_DAGEN, dagen_aantal=2, dagen_tijdvak=Tijdvak.JAAR)
    adv.anders = True
    adv.anders_namelijk = "Voor werknemers in de nachtdienst"
    adv.toekenning_anders = AdvToekenning(toekenning=AdvToekenningSoort.GELD, geld_percentage=2, geld_van=Loonbasis.JAARLOON)

    # Vakantiedagen, met extra dagen voor leeftijd, dienstverband en anders
    vd = v.vakantiedagen
    vd.aantal = 25
    vd.type = VakantiedagenType.DAGEN
    vd.tijdvak = Tijdvak.JAAR
    vd.dagen_leeftijd = True
    vd.leeftijd = [ExtraDagenLeeftijd(leeftijd=55, dagen=27), ExtraDagenLeeftijd(leeftijd=60, dagen=29)]
    vd.dagen_duur_dienstverband = True
    vd.duur_dienstverband = [ExtraDagenDuurDienstverband(jaar=10, dagen=26), ExtraDagenDuurDienstverband(jaar=25, dagen=28)]
    vd.dagen_anders = True
    vd.anders = [ExtraDagenAnders(dagen=26, namelijk="Werknemers in de volcontinudienst")]

    # Bijzonder verlof
    v.bijzonder_verlof.aanwezig = JaNee.JA
    v.bijzonder_verlof.variaties = [
        BijzonderVerlofVariatie(hoeveel=1, wat=BijzonderVerlofEenheid.DAGEN, voorwaarden="Bij verhuizing"),
        BijzonderVerlofVariatie(hoeveel=2, wat=BijzonderVerlofEenheid.DAGEN, voorwaarden="Bij eigen huwelijk"),
        BijzonderVerlofVariatie(hoeveel=4, wat=BijzonderVerlofEenheid.UUR, voorwaarden="Bij bezoek aan huisarts of tandarts"),
    ]

    # Tijd voor tijd
    v.tijd_voor_tijd.tijd_voor_tijd = JaNee.JA
    v.tijd_voor_tijd.namelijk = "Overuren kunnen worden opgenomen als vrije tijd, 1 op 1"

    # Aanvulling Wazo-verlof: alle zeven regels
    w = v.aanvulling_wazo
    w.wazo_aanvulling = JaNee.JA
    w.betaald_ouderschapsverlof = WazoRegel(aangevinkt=True, namelijk="Aanvulling tot 90% van het loon")
    w.onbetaald_ouderschapsverlof = WazoRegel(aangevinkt=True, namelijk="25% doorbetaling gedurende 6 weken")
    w.geboorteverlof = WazoRegel(aangevinkt=True, namelijk="Aanvulling tot 100% van het loon")
    w.kortdurend_zorgverlof = WazoRegel(aangevinkt=True, namelijk="Aanvulling tot 100% van het loon")
    w.langdurend_zorgverlof = WazoRegel(aangevinkt=True, namelijk="50% doorbetaling gedurende 2 weken")
    w.langere_verlofduur = WazoRegel(aangevinkt=True, namelijk="2 extra weken geboorteverlof")
    w.anders = WazoRegel(aangevinkt=True, namelijk="Adoptieverlof: 1 extra week")

    # Verplichte aanwending van verlof
    v.verplichte_aanwending.verplichte_aanwending = JaNee.JA
    v.verplichte_aanwending.periode_dagen_uren = "Collectieve vrije dagen tussen kerst en oud en nieuw"
    v.verplichte_aanwending.welk_verlof = "ADV-dagen, en anders vakantiedagen"

    # Feestdagen, ook niet-jaarlijkse en persoonlijke
    fd = v.feestdagen
    fd.aantal = 9
    fd.welke = "Nieuwjaarsdag\nGoede Vrijdag\nTweede paasdag\nKoningsdag\nBevrijdingsdag\nHemelvaartsdag\nTweede pinksterdag\nEerste kerstdag\nTweede kerstdag"
    fd.voorwaarden = "Als de feestdag op een roostervrije dag valt, vervalt de dag"
    fd.niet_elk_jaar = JaNee.JA
    fd.niet_elk_jaar_voorwaarden = "Bevrijdingsdag alleen in lustrumjaren"
    fd.persoonlijke_feestdagen = JaNee.JA
    fd.persoonlijk_aantal = 1
    fd.persoonlijk_namelijk = "Een zelf te kiezen religieuze feestdag"
    fd.persoonlijk_voorwaarden = "Minimaal 4 weken van tevoren aanvragen"

    # Waarde van een verlofdag
    v.waarde_verlofdag.waarde_verlofdag = JaNee.JA
    v.waarde_verlofdag.percentage = 0.44


# ======================================================================================================================
# 10 · Individueel keuzebudget: percentage, met alle opgenomen arbeidsvoorwaarden
# ======================================================================================================================
def vul_individueel_keuzebudget(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s10_individueel_keuzebudget import IkbVan

    ikb = f.individueel_keuzebudget
    ikb.ja_nee = JaNee.JA
    ikb.waarde = _pct(16.3, Loonbasis.MAANDLOON, Interval.MAAND)  # of een vast bedrag: _vast(1200, Interval.JAAR)
    ikb.arbeidsvoorwaarden_opgenomen = JaNee.JA
    ikb.bovenwettelijke_vakantiedagen = True
    ikb.bovenwettelijke_vakantiedagen_percentage = 1.9
    ikb.bovenwettelijke_vakantiedagen_van = IkbVan.UURLOON
    ikb.adv_dagen = True
    ikb.adv_dagen_percentage = 4.8
    ikb.adv_dagen_van = IkbVan.WEEKLOON
    ikb.eindejaarsuitkering = True
    ikb.eindejaarsuitkering_percentage = 1.6
    ikb.eindejaarsuitkering_van = IkbVan.MAANDLOON
    ikb.vakantiebijslag = True
    ikb.vakantiebijslag_percentage = 8
    ikb.vakantiebijslag_van = IkbVan.PERIODELOON
    ikb.anders = True
    ikb.anders_namelijk = "Vakbondscontributie en fiscaal voordelige fietsregeling"


# ======================================================================================================================
# 11 · Pensioen
# ======================================================================================================================
def vul_pensioen(f: Formulier) -> None:
    p = f.pensioen
    p.van_toepassing = JaNee.JA
    p.pensioenfonds_naam = "PMT"
    p.werkgeverspremie_percentage = 14.5
    p.franchise = JaNee.JA
    p.franchise_namelijk = "Franchise van € 17.545 per jaar (2026)"


# ======================================================================================================================
# 12 · Duurzaam werken en leven: alle regelingen, elke budgetsoort, verplichte scholing en duurzame samenleving
# ======================================================================================================================
def vul_duurzaam_werken_en_leven(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s12_duurzaam_werken_en_leven import (
        BudgetOfGemiddeld,
        DagenPer,
        RegelingBudgetType,
        RegelingVraagset,
        SamenlevingBudgetHoogte,
        ScholingWanneer,
        TijdEenheid,
        Tijdvak,
    )

    d = f.duurzaam_werken_en_leven

    # Duurzame inzetbaarheid. Elke regeling heeft dezelfde vragen. Let op: naar rato, uitgekeerd en voorwaarden
    # alleen invullen als er ook een budget is (anders loopt de webform vast).
    d.opleidingen = RegelingVraagset(
        aangevinkt=True, budget=BudgetOfGemiddeld.JA, budget_type=RegelingBudgetType.VAST_BEDRAG,
        vast_bedrag=1000, vast_bedrag_tijdvak=Tijdvak.JAAR, naar_rato=JaNee.JA,
        uitgekeerd=JaNee.NEE, voorwaarden=JaNee.JA, voorwaarden_namelijk="Opleiding moet functiegericht zijn",
    )
    d.loopbaancoaching = RegelingVraagset(
        aangevinkt=True, budget=BudgetOfGemiddeld.JA, budget_type=RegelingBudgetType.PERCENTAGE,
        percentage=0.5, percentage_van=Loonbasis.JAARLOON, percentage_tijdvak=Tijdvak.JAAR, naar_rato=JaNee.NEE,
        uitgekeerd=JaNee.JA, uitgekeerd_voorwaarden="Het niet gebruikte deel wordt in december uitbetaald", voorwaarden=JaNee.NEE,
    )
    d.outplacementtrajecten = RegelingVraagset(
        aangevinkt=True, budget=BudgetOfGemiddeld.JA, budget_type=RegelingBudgetType.AANTAL_DAGEN_PER_JAAR,
        aantal_dagen_per_jaar=2, naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.voorlichting_nederland = RegelingVraagset(
        aangevinkt=True, budget=BudgetOfGemiddeld.NEE_GEMIDDELD, gemiddeld_bedrag=50, gemiddeld_tijdvak=Tijdvak.JAAR,
        naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.scholing_nederland = RegelingVraagset(
        aangevinkt=True, budget=BudgetOfGemiddeld.JA, budget_type=RegelingBudgetType.VAST_BEDRAG,
        vast_bedrag=300, vast_bedrag_tijdvak=Tijdvak.JAAR, naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.sociale_begeleiding_nederland = RegelingVraagset(
        aangevinkt=True, budget=BudgetOfGemiddeld.JA, budget_type=RegelingBudgetType.VAST_BEDRAG,
        vast_bedrag=200, vast_bedrag_tijdvak=Tijdvak.JAAR, naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.inzetbaarheid_anders = RegelingVraagset(
        aangevinkt=True, namelijk="Taalcursus Nederlands", budget=BudgetOfGemiddeld.JA,
        budget_type=RegelingBudgetType.VAST_BEDRAG, vast_bedrag=400, vast_bedrag_tijdvak=Tijdvak.JAAR,
        naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    # d.inzetbaarheid_geen = True kan niet samen met de regelingen hierboven.

    # Vitaliteit
    d.fysieke_gezondheid = RegelingVraagset(
        aangevinkt=True, namelijk="Sportabonnement", budget=BudgetOfGemiddeld.JA,
        budget_type=RegelingBudgetType.VAST_BEDRAG, vast_bedrag=25, vast_bedrag_tijdvak=Tijdvak.MAAND,
        naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.mentale_gezondheid = RegelingVraagset(
        aangevinkt=True, namelijk="Gesprekken met een psycholoog", budget=BudgetOfGemiddeld.JA,
        budget_type=RegelingBudgetType.VAST_BEDRAG, vast_bedrag=500, vast_bedrag_tijdvak=Tijdvak.JAAR,
        naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.financiele_gezondheid = RegelingVraagset(
        aangevinkt=True, namelijk="Budgetcoach", budget=BudgetOfGemiddeld.NEE_GEMIDDELD,
        gemiddeld_bedrag=100, gemiddeld_tijdvak=Tijdvak.JAAR, naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.vitaliteitsbudget = RegelingVraagset(
        aangevinkt=True, budget=BudgetOfGemiddeld.JA, budget_type=RegelingBudgetType.VAST_BEDRAG,
        vast_bedrag=300, vast_bedrag_tijdvak=Tijdvak.JAAR, naar_rato=JaNee.JA, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    d.vitaliteit_anders = RegelingVraagset(
        aangevinkt=True, namelijk="Gezonde lunch op kantoor", budget=BudgetOfGemiddeld.NEE_GEMIDDELD,
        gemiddeld_bedrag=5, gemiddeld_tijdvak=Tijdvak.WEEK, naar_rato=JaNee.NEE, uitgekeerd=JaNee.NEE, voorwaarden=JaNee.NEE,
    )
    # d.vitaliteit_geen = True kan niet samen met de regelingen hierboven.

    # Verplichte scholing
    d.verplichte_scholing = JaNee.JA
    d.verplichte_scholing_namelijk = "VCA-basis en NEN 3140"
    d.scholing_tijd = 2
    d.scholing_tijd_type = TijdEenheid.DAG
    d.scholing_wanneer = ScholingWanneer.ANDER_MOMENT
    d.scholing_ander_moment = "Op zaterdag, met compensatie in vrije tijd"
    d.scholing_kosten = 450
    # Of tijdens werktijd:  d.scholing_wanneer = ScholingWanneer.TIJDENS_WERKTIJD; d.scholing_tijdens_werktijd = "..." 

    # Duurzame samenleving en groene aarde
    d.samenleving_regeling = JaNee.JA
    d.samenleving_budget = JaNee.JA
    d.budget_hoogte = SamenlevingBudgetHoogte.UREN_OF_DAGEN
    # Of een percentage:  d.budget_hoogte = SamenlevingBudgetHoogte.PERCENTAGE; d.percentage = 0.5
    #                     d.percentage_van = Loonbasis.JAARLOON; d.percentage_tijdvak = Tijdvak.JAAR
    # Of een vast bedrag: d.budget_hoogte = SamenlevingBudgetHoogte.VAST_BEDRAG; d.vast_bedrag = 250
    #                     d.vast_bedrag_tijdvak = Tijdvak.JAAR
    d.uren_of_dagen_aantal = 1
    d.uren_of_dagen_type = TijdEenheid.DAG
    d.uren_of_dagen_per = DagenPer.JAAR
    d.budget_naar_rato = JaNee.JA
    d.budget_uitgekeerd = JaNee.JA
    d.budget_uitgekeerd_voorwaarden = "Een niet opgenomen dag wordt aan het eind van het jaar uitbetaald"
    d.budget_voorwaarden = JaNee.JA
    d.budget_voorwaarden_namelijk = "Een vrije dag voor vrijwilligerswerk voor een natuurorganisatie"


# ======================================================================================================================
# 13 · Aanvullende regelingen: alle vijf regelingen, alle premiesoorten en andere regelingen
# ======================================================================================================================
def vul_aanvullende_regelingen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s13_aanvullende_regelingen import (
        AanvullendeRegeling,
        AanvullendeRegelingMetDekking,
        AndereSocialeRegeling,
    )

    r = f.aanvullende_regelingen
    r.paww = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        omschrijving="Private aanvulling WW volgens de cao",
        werkgeverspremie=Bedragregel(soort=BedragSoort.NVT),
        werknemerspremie=_pct(0.4, Loonbasis.MAANDLOON, Interval.MAAND),
        dekkingswaarde=_tijd(38),  # de dekkingswaarde heeft geen "per"
    )
    r.pazw = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        omschrijving="Aanvulling op de Ziektewet tot 100%",
        werkgeverspremie=_pct(0.6, Loonbasis.MAANDLOON, Interval.MAAND),
        werknemerspremie=Bedragregel(soort=BedragSoort.NVT),
        dekkingswaarde=_pct(100, Loonbasis.MAANDLOON),
    )
    r.rvu_regeling = AanvullendeRegeling(
        ja_nee=JaNee.JA,
        omschrijving="Generatiepact: 80% werken, 90% loon, 100% pensioenopbouw",
        werkgeverspremie=_vast(25, Interval.MAAND),
        werknemerspremie=Bedragregel(soort=BedragSoort.NVT),
    )
    r.wga_hiaat = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        omschrijving="WGA-hiaatverzekering via de werkgever",
        werkgeverspremie=_pct(0.3, Loonbasis.JAARLOON, Interval.JAAR),
        werknemerspremie=_pct(0.2, Loonbasis.JAARLOON, Interval.JAAR),
        dekkingswaarde=_pct(70, Loonbasis.JAARLOON),
    )
    r.ongevallenverzekering = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        omschrijving="Collectieve ongevallenverzekering",
        werkgeverspremie=_vast(10, Interval.MAAND),
        werknemerspremie=Bedragregel(soort=BedragSoort.NVT),
        dekkingswaarde=_vast(50000),
    )
    r.andere_ja_nee = JaNee.JA
    r.andere_regelingen = [
        AndereSocialeRegeling(
            omschrijving="Aanvulling bij arbeidsongeschiktheid na het tweede ziektejaar",
            werkgeverspremie=_pct(0.25, Loonbasis.MAANDLOON, Interval.MAAND),
            werknemerspremie=_vast(3, Interval.MAAND),
        ),
    ]


# ======================================================================================================================
# 14 · Overig: meerdere regelingen, elke bedragsoort
# ======================================================================================================================
def vul_overig(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s14_overig import OverigeRegeling

    f.overig.ja_nee = JaNee.JA
    f.overig.overige_regelingen = [
        OverigeRegeling(naam="Gereedschapsvergoeding", voorwaarden="Bij gebruik van eigen gereedschap", waarde=_vast(5, Interval.WEEK)),
        OverigeRegeling(naam="Bedrijfshulpverlening", voorwaarden="Voor BHV'ers met geldig certificaat", waarde=_pct(1, Loonbasis.MAANDLOON, Interval.MAAND)),
        OverigeRegeling(naam="Vrijwilligersuren", voorwaarden="Voor vrijwilligerswerk in de regio", waarde=_tijd(8, Interval.JAAR)),
    ]


# ======================================================================================================================
# 15 · Grondslagen: alleen voor grondslagen die elders gekozen zijn (hier: bruto loon bij vakantiebijslag en
#      basisloon bij loondoorbetaling bij ziekte). Laat alle mogelijkheden zien.
# ======================================================================================================================
def vul_grondslagen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s04_toeslagen import ToeslagSoort
    from setu_kern.bronnen.wijzerbelonen.formulier.s15_grondslagen import GrondslagInstelling, ToeslagenMeegenomen

    f.grondslagen.per_grondslag = {
        Grondslag.BRUTO_LOON: GrondslagInstelling(
            salaris=True,
            vakantietoeslag=True,
            betaald_verlof=True,
            toeslagen=ToeslagenMeegenomen.SOMMIGE,
            toeslag={ToeslagSoort.ONREGELMATIGHEIDSTOESLAGEN: True, ToeslagSoort.PLOEGENTOESLAGEN: True},
            peildatum=dt.date(2026, 6, 1),
        ),
        Grondslag.BASISLOON: GrondslagInstelling(
            salaris=True,
            toeslagen=ToeslagenMeegenomen.ALLE,
        ),
    }


# ======================================================================================================================
# 16 · Ondertekenen: meerdere contactpersonen
# ======================================================================================================================
def vul_ondertekenen(f: Formulier) -> None:
    from setu_kern.bronnen.wijzerbelonen.formulier.s16_ondertekenen import Contactpersoon

    f.ondertekenen.contactpersonen = [
        Contactpersoon(naam="J. Jansen", email="hr@voorbeeld.nl", telefoon="+31201234567", functie="HR-adviseur"),
        Contactpersoon(naam="P. de Vries", email="salaris@voorbeeld.nl", telefoon="+31207654321", functie="Salarisadministrateur"),
    ]
    f.ondertekenen.akkoord = True


def vul_formulier() -> Formulier:
    f = Formulier()
    for vul in (
        vul_algemeen,
        vul_beloning,
        vul_functiegroepen,
        vul_toeslagen,
        vul_vakantiebijslag,
        vul_vergoedingen,
        vul_bijzondere_uitkeringen,
        vul_loondoorbetaling_bij_ziekte,
        vul_verlof,
        vul_individueel_keuzebudget,
        vul_pensioen,
        vul_duurzaam_werken_en_leven,
        vul_aanvullende_regelingen,
        vul_overig,
        vul_grondslagen,
        vul_ondertekenen,
    ):
        vul(f)
    return f


def main() -> None:
    verwerk(vul_formulier(), UITVOER, KERNMODEL_UITVOER)


if __name__ == "__main__":
    main()
