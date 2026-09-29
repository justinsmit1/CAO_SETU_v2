"""Vul het complete wijzerbelonen-formulier in Python, maak het SETU-kernmodel en schrijf een bestand dat je kunt
uploaden op https://standaard-uitvraag.wijzerbelonen.nl/ (knop "Importeren").

Draaien vanuit de projectmap:

    .venv\\Scripts\\python.exe examples\\maak_upload.py                 # schrijft uitvoer\\wijzerbelonen_upload.json
    .venv\\Scripts\\python.exe examples\\maak_upload.py pad\\naar\\bestand.json

HOE JE DIT BESTAND INVULT
- Hieronder staat per sectie van het formulier een functie ``vul_...``, in dezelfde volgorde als op de website
  (01 Algemeen t/m 16 Ondertekenen). Samen vormen ze het hele formulier.
- Er staat nu een fictief voorbeeld in ("Voorbeeld Bouw B.V."). Vervang de waarden door die van jouw opdrachtgever.
- Geldt iets niet, zet dan de ja/nee-vraag op ``JaNee.NEE`` en haal de regels eronder weg (of zet er ``#`` voor).
- Alle vragen en keuzes per sectie staan in ``INVULHULP.md`` in de hoofdmap.
- Het script controleert alles tijdens het invullen: een optie die niet bestaat of een vraag die bij jouw antwoord
  niet getoond wordt, geeft direct een melding met wat er niet klopt.

Wat het script maakt (in de map ``uitvoer``):
- ``wijzerbelonen_upload.json``: dit upload je op wijzerbelonen.nl. Alleen de antwoorden in dit bestand
  (``__webform_data__``) worden door de website gelezen.
- ``setu_kernmodel.json``: dezelfde gegevens volgens de SETU-standaard (``InquiryPayEquity``), om te vergelijken met
  SETU uit andere formulieren of bronnen.
"""

import datetime as dt
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from cao_setu_v2.formulier import Formulier  # noqa: E402
from cao_setu_v2.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage, Tijd, VastBedrag  # noqa: E402, F401
from cao_setu_v2.formulier.codes import Grondslag, Interval, JaNee, Loonbasis, Peildatum  # noqa: E402
from cao_setu_v2.koppeling.wijzerbelonen import naar_setu  # noqa: E402
from cao_setu_v2.setu import InquiryPayEquity  # noqa: E402

STANDAARD_UITVOER = PROJECT / "uitvoer" / "wijzerbelonen_upload.json"
KERNMODEL_UITVOER = PROJECT / "uitvoer" / "setu_kernmodel.json"


# ======================================================================================================================
# 01 · Algemeen
# ======================================================================================================================
def vul_algemeen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s01_algemeen import CaoOfRegeling, CaoVanToepassingOmdat, TypeIdentificatienummer

    a = f.algemeen
    a.naam_regeling = "Voorbeeld Bouw 2026"  # naam of nummer van deze uitvraag
    a.geldig_van = dt.date(2026, 1, 1)
    a.geldig_tot = dt.date(2026, 12, 31)  # mag leeg: haal de regel dan weg

    # Opdrachtgever
    a.opdrachtgever_naam = "Voorbeeld Bouw B.V."
    a.opdrachtgever_kvk = "12345678"
    a.opdrachtgever_kvk_type = TypeIdentificatienummer.KVK  # KVK, OIN of RSIN
    a.sector = "Bouw en infra"

    # Hoe zijn de arbeidsvoorwaarden geregeld? CAO, EIGEN_REGELING, CAO_EN_EIGEN_REGELING of GEEN
    a.cao_of_regeling = CaoOfRegeling.CAO
    # Alleen bij een cao:
    a.cao_naam = "Cao Bouw & Infra"
    a.cao_nummer = "1496"
    a.cao_van_toepassing_omdat = CaoVanToepassingOmdat.ALGEMEEN_VERBINDEND  # of LID_BRANCHEORGANISATIE / IN_ARBEIDSOVEREENKOMST
    a.cao_van = dt.date(2025, 6, 1)  # alleen bij algemeen verbindend
    a.cao_tot = dt.date(2027, 5, 31)


# ======================================================================================================================
# 02 · Beloning
# ======================================================================================================================
def vul_beloning(f: Formulier) -> None:
    from cao_setu_v2.formulier.s02_beloning import (
        BeloningInterval,
        NormaleArbeidsduur,
        PeriodiekeVerhoging,
        Salarisschaal,
        Salaristabel,
        Stap,
        VerhogingBerekening,
        VerhogingWanneer,
        WerkervaringInschaling,
    )

    # Eén of meer salaristabellen; elke tabel heeft schalen, elke schaal heeft stappen (treden).
    f.beloning.beloningen = [
        Salaristabel(
            naam="Salaristabel 2026",
            geldig_vanaf=dt.date(2026, 1, 1),
            normale_arbeidsduur=NormaleArbeidsduur.UUR_40,  # UUR_40, UUR_38, UUR_36 of ANDERS (+ normale_arbeidsduur_anders=...)
            beloning_vastgesteld=BeloningInterval.PER_MAAND,  # PER_MAAND, PER_VIER_WEKEN, PER_WEEK of PER_UUR
            uurlonen_vastgelegd=JaNee.NEE,
            salarisschalen=[
                Salarisschaal(naam="A", stappen=[Stap(naam="0", bedrag=2450), Stap(naam="1", bedrag=2525)]),
                Salarisschaal(naam="B", stappen=[Stap(naam="0", bedrag=2800), Stap(naam="1", bedrag=2890)]),
            ],
            werkervaring_inschaling=WerkervaringInschaling.NEE,
            periodieke_verhogingen=JaNee.JA,
            minimale_duur_dienstverband=PeriodiekeVerhoging(
                aangevinkt=True,
                wanneer=VerhogingWanneer.GEWERKT_JAAR,
                berekening=VerhogingBerekening.TREDEN,
                berekening_treden=1,
            ),
            initiele_eenmalige_verhogingen=JaNee.NEE,
            afwijkende_arbeidsduur=JaNee.NEE,
        )
    ]
    f.beloning.betaalde_rusttijden_en_pauzes = JaNee.NEE


# ======================================================================================================================
# 03 · Functiegroepen
# ======================================================================================================================
def vul_functiegroepen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s03_functiegroepen import Functiegroep

    # salarisschaal = "tabel,schaal", geteld vanaf 0: "0,0" = 1e salaristabel, 1e schaal (A); "0,1" = schaal B.
    f.functiegroepen.functie_groepen = [
        Functiegroep(titel="Timmerman", code="TIM", salarisschaal="0,0"),
        Functiegroep(titel="Uitvoerder", code="UITV", salarisschaal="0,1"),
    ]


# ======================================================================================================================
# 04 · Toeslagen
# ======================================================================================================================
def vul_toeslagen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s04_toeslagen import (
        Cumulatief,
        ToepassingsperiodesType,
        Toepassingsperiode,
        ToeslagVariatie,
    )

    t = f.toeslagen
    # Vink per soort aan welke toeslagen er zijn (geen toeslagen? zet dan alleen t.geen_toeslagen = True).
    t.overwerktoeslag_aan = True
    t.overwerktoeslag = [
        ToeslagVariatie(
            bedrag=Bedragregel(
                soort=BedragSoort.PERCENTAGE,
                percentage=Percentage(percentage=125, basis=Loonbasis.UURLOON, per=Interval.UUR),
            ),
            voorwaarden="Voor elk uur boven de 40 uur per week",
            cumulatief=Cumulatief.NEE,
        )
    ]
    t.onregelmatigheids_toeslagen_aan = True
    t.onregelmatigheids_toeslagen = [
        ToeslagVariatie(
            bedrag=Bedragregel(
                soort=BedragSoort.PERCENTAGE,
                percentage=Percentage(percentage=50, basis=Loonbasis.UURLOON, per=Interval.UUR),
            ),
            voorwaarden="Werken op zaterdag",
            cumulatief=Cumulatief.NEE,
            toepassingsperiodes_type=ToepassingsperiodesType.BEPAALD,
            toepassingsperiodes=[
                Toepassingsperiode(starttijd=dt.time(0, 0), eindtijd=dt.time(23, 59), zaterdag=True),
            ],
        )
    ]


# ======================================================================================================================
# 05 · Vakantiebijslag
# ======================================================================================================================
def vul_vakantiebijslag(f: Formulier) -> None:
    f.vakantiebijslag.ja_nee = JaNee.JA
    f.vakantiebijslag.bedrag = Bedragregel(  # alleen een percentage is mogelijk
        soort=BedragSoort.PERCENTAGE,
        percentage=Percentage(percentage=8, basis=Loonbasis.JAARLOON, per=Interval.JAAR, grondslag=Grondslag.BRUTO_LOON),
    )


# ======================================================================================================================
# 06 · Vergoedingen
# ======================================================================================================================
def vul_vergoedingen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s06_vergoedingen import (
        EigenVervoerType,
        EigenVervoerVariatie,
        KostenVergoeding,
        ReistijdVergoeding,
        TijdvakKosten,
    )

    v = f.vergoedingen
    # Reiskosten: vink aan wat er is, en vul daarna de details in.
    v.reiskosten.kent_eigen_vervoer = True
    v.reiskosten.eigen_vervoer = [
        EigenVervoerVariatie(type=EigenVervoerType.STANDAARD_TARIEF, voorwaarden="Bij een enkele reis van meer dan 10 km"),
    ]
    v.reisuren.vergoeding = ReistijdVergoeding.NEE
    v.stand_by.ja_nee = JaNee.NEE
    v.zorgverzekering.ja_nee = JaNee.NEE
    v.thuiswerk.ja_nee = JaNee.NEE
    # Mobiliteit (leaseauto, leasefiets, OV, fiets, mobiliteitsvergoeding): hier niet van toepassing.
    # Kostenvergoedingen: koffiegeld, maaltijd, was, bedrijfskleding/schoenen, arbo, BYOD of anders.
    v.kosten.bedrijfskleding_schoenen = KostenVergoeding(
        aangevinkt=True, bedrag=150, tijdvak=TijdvakKosten.JAAR, voorwaarden="Voor veiligheidsschoenen", naar_rato=JaNee.NEE
    )


# ======================================================================================================================
# 07 · Bijzondere uitkeringen
# ======================================================================================================================
def vul_bijzondere_uitkeringen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s07_bijzondere_uitkeringen import (
        HoeToegekend,
        HoeToegekendVast,
        Jubileumuitkering,
        VasteUitkering,
    )

    b = f.bijzondere_uitkeringen
    b.eenmalige_uitkeringen_bekend = JaNee.NEE
    b.vaste_uitkering_van_toepassing = JaNee.JA
    b.vaste_uitkeringen = [
        VasteUitkering(
            naam="Eindejaarsuitkering",
            toekenning_datum=dt.date(2026, 12, 15),
            hoe_toegekend=HoeToegekendVast.PERCENTAGE_LOON,
            percentage=4,
            percentage_van=Loonbasis.JAARLOON,
        )
    ]
    b.jubileumuitkering_van_toepassing = JaNee.JA
    b.jubileumuitkeringen = [
        Jubileumuitkering(
            naam="25-jarig dienstjubileum",
            hoe_toegekend=HoeToegekend.PERCENTAGE_LOON,
            percentage=100,
            percentage_van=Loonbasis.MAANDLOON,
            dienstverband_jaren=25,
            referentiedatum=Peildatum.DATUM_INDIENSTTREDING,
        )
    ]
    b.variabele_uitkering_van_toepassing = JaNee.NEE


# ======================================================================================================================
# 08 · Loondoorbetaling bij ziekte
# ======================================================================================================================
def vul_loondoorbetaling_bij_ziekte(f: Formulier) -> None:
    from cao_setu_v2.formulier.s08_loondoorbetaling_bij_ziekte import LoondoorbetalingRegel, TijdvakZiekte

    z = f.loondoorbetaling_bij_ziekte
    z.regels = [
        LoondoorbetalingRegel(percentage=100, van=Loonbasis.MAANDLOON, per_tijdvak=TijdvakZiekte.JAAR, voorwaarden="Eerste ziektejaar"),
        LoondoorbetalingRegel(percentage=70, van=Loonbasis.MAANDLOON, per_tijdvak=TijdvakZiekte.JAAR, voorwaarden="Tweede ziektejaar"),
    ]
    z.wachtdagen = JaNee.NEE


# ======================================================================================================================
# 09 · Verlof
# ======================================================================================================================
def vul_verlof(f: Formulier) -> None:
    from cao_setu_v2.formulier.s09_verlof import (
        AdvToekenning,
        AdvToekenningSoort,
        BijzonderVerlofEenheid,
        BijzonderVerlofVariatie,
        ExtraDagenLeeftijd,
        Tijdvak,
        VakantiedagenType,
    )

    v = f.verlof
    # ADV / ATV
    v.adv_atv.adv_regeling = JaNee.JA
    v.adv_atv.toekenning = AdvToekenning(toekenning=AdvToekenningSoort.TIJD_DAGEN, dagen_aantal=13, dagen_tijdvak=Tijdvak.JAAR)
    v.adv_atv.aanvullende_regeling = JaNee.NEE

    # Vakantiedagen
    v.vakantiedagen.aantal = 25
    v.vakantiedagen.type = VakantiedagenType.DAGEN
    v.vakantiedagen.tijdvak = Tijdvak.JAAR
    v.vakantiedagen.dagen_leeftijd = True
    v.vakantiedagen.leeftijd = [ExtraDagenLeeftijd(leeftijd=55, dagen=2), ExtraDagenLeeftijd(leeftijd=60, dagen=4)]

    # Bijzonder verlof
    v.bijzonder_verlof.aanwezig = JaNee.JA
    v.bijzonder_verlof.variaties = [
        BijzonderVerlofVariatie(hoeveel=1, wat=BijzonderVerlofEenheid.DAGEN, voorwaarden="Bij verhuizing"),
        BijzonderVerlofVariatie(hoeveel=2, wat=BijzonderVerlofEenheid.DAGEN, voorwaarden="Bij eigen huwelijk"),
    ]

    v.tijd_voor_tijd.tijd_voor_tijd = JaNee.NEE
    v.aanvulling_wazo.wazo_aanvulling = JaNee.NEE

    # Verplichte aanwending van verlof (bijvoorbeeld een bouwvak of collectieve vrije dagen)
    v.verplichte_aanwending.verplichte_aanwending = JaNee.JA
    v.verplichte_aanwending.periode_dagen_uren = "Drie weken zomervakantie (bouwvak)"
    v.verplichte_aanwending.welk_verlof = "Vakantiedagen"

    # Feestdagen
    v.feestdagen.aantal = 8
    v.feestdagen.welke = "Nieuwjaarsdag\nTweede paasdag\nKoningsdag\nBevrijdingsdag (lustrumjaren)\nHemelvaartsdag\nTweede pinksterdag\nEerste kerstdag\nTweede kerstdag"
    v.feestdagen.niet_elk_jaar = JaNee.NEE
    v.feestdagen.persoonlijke_feestdagen = JaNee.NEE

    v.waarde_verlofdag.waarde_verlofdag = JaNee.NEE


# ======================================================================================================================
# 10 · Individueel keuzebudget (IKB)
# ======================================================================================================================
def vul_individueel_keuzebudget(f: Formulier) -> None:
    from cao_setu_v2.formulier.s10_individueel_keuzebudget import IkbVan

    ikb = f.individueel_keuzebudget
    ikb.ja_nee = JaNee.JA
    ikb.waarde = Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=1200, per=Interval.JAAR))
    ikb.arbeidsvoorwaarden_opgenomen = JaNee.JA
    ikb.eindejaarsuitkering = True
    ikb.eindejaarsuitkering_percentage = 3
    ikb.eindejaarsuitkering_van = IkbVan.MAANDLOON


# ======================================================================================================================
# 11 · Pensioen
# ======================================================================================================================
def vul_pensioen(f: Formulier) -> None:
    p = f.pensioen
    p.van_toepassing = JaNee.JA
    p.pensioenfonds_naam = "bpfBOUW"
    p.werkgeverspremie_percentage = 14.5
    p.franchise = JaNee.JA
    p.franchise_namelijk = "Franchise volgens het pensioenreglement"


# ======================================================================================================================
# 12 · Duurzaam werken en leven
# ======================================================================================================================
def vul_duurzaam_werken_en_leven(f: Formulier) -> None:
    from cao_setu_v2.formulier.s12_duurzaam_werken_en_leven import (
        BudgetOfGemiddeld,
        RegelingBudgetType,
        RegelingVraagset,
        ScholingWanneer,
        TijdEenheid,
        Tijdvak,
    )

    d = f.duurzaam_werken_en_leven
    # Duurzame inzetbaarheid: opleidingen, loopbaancoaching, outplacement, ... (elke regeling dezelfde vragen)
    d.opleidingen = RegelingVraagset(
        aangevinkt=True,
        budget=BudgetOfGemiddeld.JA,
        budget_type=RegelingBudgetType.VAST_BEDRAG,
        vast_bedrag=500,
        vast_bedrag_tijdvak=Tijdvak.JAAR,
        naar_rato=JaNee.JA,
        uitgekeerd=JaNee.NEE,
        voorwaarden=JaNee.NEE,
    )
    d.vitaliteit_geen = True  # geen regelingen voor vitaliteit (fysieke, mentale, financiële gezondheid)

    # Verplichte scholing (op grond van wet of cao)
    d.verplichte_scholing = JaNee.JA
    d.verplichte_scholing_namelijk = "VCA-basis"
    d.scholing_tijd = 8
    d.scholing_tijd_type = TijdEenheid.UUR
    d.scholing_wanneer = ScholingWanneer.TIJDENS_WERKTIJD
    d.scholing_tijdens_werktijd = "Tijdens werktijd, met doorbetaling van loon"
    d.scholing_kosten = 250

    # Duurzame samenleving en groene aarde
    d.samenleving_regeling = JaNee.NEE


# ======================================================================================================================
# 13 · Aanvullende regelingen
# ======================================================================================================================
def vul_aanvullende_regelingen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s13_aanvullende_regelingen import AanvullendeRegeling, AanvullendeRegelingMetDekking

    r = f.aanvullende_regelingen
    r.paww = AanvullendeRegelingMetDekking(
        ja_nee=JaNee.JA,
        omschrijving="Private aanvulling WW volgens de cao",
        werkgeverspremie=Bedragregel(soort=BedragSoort.NVT),
        werknemerspremie=Bedragregel(
            soort=BedragSoort.PERCENTAGE,
            percentage=Percentage(percentage=0.4, basis=Loonbasis.MAANDLOON, per=Interval.MAAND),
        ),
    )
    r.pazw = AanvullendeRegelingMetDekking(ja_nee=JaNee.NEE)
    r.rvu_regeling = AanvullendeRegeling(ja_nee=JaNee.NEE)
    r.wga_hiaat = AanvullendeRegelingMetDekking(ja_nee=JaNee.NEE)
    r.ongevallenverzekering = AanvullendeRegelingMetDekking(ja_nee=JaNee.NEE)
    r.andere_ja_nee = JaNee.NEE


# ======================================================================================================================
# 14 · Overig
# ======================================================================================================================
def vul_overig(f: Formulier) -> None:
    from cao_setu_v2.formulier.s14_overig import OverigeRegeling

    f.overig.ja_nee = JaNee.JA
    f.overig.overige_regelingen = [
        OverigeRegeling(
            naam="Gereedschapsvergoeding",
            voorwaarden="Voor timmerlieden die eigen gereedschap gebruiken",
            waarde=Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=5, per=Interval.WEEK)),
        )
    ]


# ======================================================================================================================
# 15 · Grondslagen
# ======================================================================================================================
def vul_grondslagen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s04_toeslagen import ToeslagSoort
    from cao_setu_v2.formulier.s15_grondslagen import GrondslagInstelling, ToeslagenMeegenomen

    # Alleen voor grondslagen die elders gekozen zijn (hier: bruto loon, bij de vakantiebijslag).
    f.grondslagen.per_grondslag = {
        Grondslag.BRUTO_LOON: GrondslagInstelling(
            salaris=True,
            betaald_verlof=True,
            toeslagen=ToeslagenMeegenomen.SOMMIGE,
            toeslag={ToeslagSoort.ONREGELMATIGHEIDSTOESLAGEN: True},
            peildatum=dt.date(2026, 6, 1),
        )
    }


# ======================================================================================================================
# 16 · Ondertekenen
# ======================================================================================================================
def vul_ondertekenen(f: Formulier) -> None:
    from cao_setu_v2.formulier.s16_ondertekenen import Contactpersoon

    f.ondertekenen.contactpersonen = [
        Contactpersoon(naam="J. Jansen", email="hr@voorbeeld.nl", telefoon="+31201234567", functie="HR-adviseur"),
    ]
    # Hiermee verklaar je, net als op de website, bevoegd te zijn en de arbeidsvoorwaarden volledig door te geven.
    f.ondertekenen.akkoord = True


def vul_formulier() -> Formulier:
    """Het hele formulier: alle secties in de volgorde van de website."""
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


def vul_kernmodel(formulier: Formulier) -> InquiryPayEquity:
    """Het SETU-kernmodel van dit formulier: dezelfde gegevens, maar in de standaard (Engelse SETU-namen).

    Dit object gebruik je om te vergelijken met andere bronnen, bijvoorbeeld::

        ander = InquiryPayEquity.lees("export_andere_bron.json")
        bericht.customer.name, ander.customer.name
        [s.name for r in bericht.remuneration for s in r.salary_scale or []]
    """
    bericht, meldingen = naar_setu.kernmodel(formulier)
    if meldingen:
        print(f"  Let op: {len(meldingen)} onderdeel/onderdelen van de webform-SETU voldeden niet aan het schema:")
        for m in meldingen:
            print(f"    - {m}")
    return bericht


def toon_kernmodel(bericht: InquiryPayEquity) -> None:
    """Een korte samenvatting van wat er in het kernmodel staat."""
    print(f"  opdrachtgever: {bericht.customer.name}")
    if bericht.labour_agreements and bericht.labour_agreements.collective_labour_agreement:
        print(f"  cao:           {bericht.labour_agreements.collective_labour_agreement.name}")
    for i, beloning in enumerate(bericht.remuneration):
        schalen = ", ".join(s.name for s in beloning.salary_scale or [])
        print(f"  salaristabel {i + 1}: {beloning.work_duration.value_per_week} uur per week, schalen {schalen}")
    for toeslag in bericht.allowance or []:
        print(f"  toeslag/vergoeding/uitkering: {toeslag.name} ({toeslag.type_code})")
    for bijslag in bericht.holiday_allowance or []:
        bedrag = bijslag.line[0].amount if bijslag.line else None
        print(f"  vakantiebijslag: {bedrag.value if bedrag else '?'} {bedrag.unit_code if bedrag else ''}")
    print(f"  geldig volgens het officiële schema: {'ja' if not bericht.valideer() else 'nee'}")


def controleer_met_webform(formulier: Formulier) -> None:
    """Optioneel: laat de échte webform (in V8) de antwoorden inlezen en controleert elke vraag.

    Werkt alleen met de dev-afhankelijkheid ``mini-racer`` (``uv sync``) en de bundle in ``tests/referentie``.
    """
    try:
        sys.path.insert(0, str(PROJECT / "tests"))
        from referentie.controle import antwoord_problemen, vergelijk_setu
        from referentie.webform import Webform
    except ImportError:
        print("  (overgeslagen: mini-racer niet geïnstalleerd)")
        return
    from cao_setu_v2.koppeling.wijzerbelonen.antwoorden import naar_antwoorden

    antwoorden = naar_antwoorden(formulier)
    with Webform() as wf:
        problemen = antwoord_problemen(wf, antwoorden)
        verschillen = vergelijk_setu(wf, antwoorden, naar_setu.setu_json(antwoorden))
    print(f"  antwoorden die de webform niet kent of verbergt: {len(problemen)}")
    for p in problemen:
        print(f"    - {p}")
    print(f"  verschillen met de SETU-export van de webform zelf: {len(verschillen)}")
    for v in verschillen:
        print(f"    - {v}")


def verwerk(formulier: Formulier, uitvoer: Path, kernmodel_uitvoer: Path) -> None:
    """Controleert het formulier, schrijft het uploadbestand en het SETU-kernmodel, en controleert met de webform."""
    uitvoer.parent.mkdir(parents=True, exist_ok=True)
    open_voorwaarden = formulier.controleer()
    if open_voorwaarden:
        print("Het formulier bevat antwoorden die in de tool verborgen zouden zijn:")
        for regel in open_voorwaarden:
            print(f"  - {regel}")
        raise SystemExit(1)
    print(formulier)
    problemen = naar_setu.schrijf_export(formulier, uitvoer)
    print(f"Geschreven: {uitvoer}")
    print("Upload dit bestand op https://standaard-uitvraag.wijzerbelonen.nl/ via 'Importeren'.")

    print("\nSETU-controle tegen het officiële schema:")
    if problemen:
        print(f"  {len(problemen)} punt(en). De upload werkt wel; dit gaat alleen over het SETU-deel en komt vaak door")
        print("  een fout in de webform zelf (zie docs/koppeling_wijzerbelonen.md):")
        for p in problemen:
            print(f"    - {p}")
    else:
        print("  geldig")

    print("\nSETU-kernmodel (InquiryPayEquity):")
    bericht = vul_kernmodel(formulier)
    toon_kernmodel(bericht)
    bericht.schrijf(kernmodel_uitvoer, met_extensies=False)
    print(f"  Geschreven: {kernmodel_uitvoer}")

    print("\nControle met de echte webform:")
    controleer_met_webform(formulier)


def main() -> None:
    uitvoer = Path(sys.argv[1]) if len(sys.argv) > 1 else STANDAARD_UITVOER
    verwerk(vul_formulier(), uitvoer, KERNMODEL_UITVOER)


if __name__ == "__main__":
    main()
