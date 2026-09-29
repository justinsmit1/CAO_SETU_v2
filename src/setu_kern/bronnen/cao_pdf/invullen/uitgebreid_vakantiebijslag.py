"""05 · Vakantiebijslag, uitgebreid met de SETU-velden die de wijzerbelonen-webform niet vraagt.

De webform kent bij de vakantiebijslag alleen ja/nee en één percentage. De cao zegt meestal meer: vanaf wanneer, in
welke maand uitbetaald, een minimum of maximum, naar rato, en voor wie. Het LLM vult hier ``VakantiebijslagSETU`` in;
daaruit komt:

- ``naar_formulier``: de webform-vragen (ja/nee en het eerste percentage), zodat het Formulier en de rest van de
  koppeling hetzelfde blijven;
- ``naar_kern``: de volledige ``HolidayAllowanceArrangement`` (alle regels, periode, uitbetaling, voorwaarden) die de
  door de webform-koppeling gemaakte regeling in het kernbericht vervangt.
"""

import datetime as dt

from ....kern import InquiryPayEquity
from ....kern.basis import ArrangementLine, Id, Identifier, Origin
from ....kern.codes import OriginType, SchemeAgencyId
from ....kern.regelingen import HolidayAllowanceArrangement
from ....kern.tijd import Recurring
from ...wijzerbelonen.formulier import Formulier
from ...wijzerbelonen.formulier._basis import FormulierModel, veld
from ...wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort
from ...wijzerbelonen.formulier.codes import JaNee
from ...wijzerbelonen.formulier.s01_algemeen import CaoOfRegeling, CaoVanToepassingOmdat
from ...wijzerbelonen.formulier.s05_vakantiebijslag import Vakantiebijslag
from ...wijzerbelonen.formulier.voorwaarden import Als
from .uitgebreid_gedeeld import Voorwaarde, bedrag_naar_kern, conditions, effective_period, proportional

NAAM = "Vakantiebijslag"
ID_ARRANGEMENT = "VAKANTIEBIJSLAG"


class VakantiebijslagRegel(FormulierModel):
    """Eén tarief. Meerdere regels bij verschillende tarieven, bijv. een ander percentage vanaf een bepaalde leeftijd."""

    bedrag: Bedragregel | None = veld(
        "cao_pdf/vakantiebijslag/regel/bedrag",
        "Hoeveel bedraagt de vakantiebijslag in deze regel?",
        opties=[BedragSoort.PERCENTAGE, BedragSoort.VAST_BEDRAG],
    )
    minimum_bedrag: float | None = veld(
        "cao_pdf/vakantiebijslag/regel/minimum",
        "Is er een minimumbedrag aan vakantiebijslag (bijv. 'ten minste € 500')? Het bedrag dat de werknemer dan minimaal krijgt.",
        eenheid="€",
    )
    maximum_bedrag: float | None = veld(
        "cao_pdf/vakantiebijslag/regel/maximum",
        "Is er een maximumbedrag aan vakantiebijslag? Het bedrag dat de werknemer dan maximaal krijgt.",
        eenheid="€",
    )
    loon_minimum: float | None = veld(
        "cao_pdf/vakantiebijslag/regel/loon-minimum",
        "Is er een ondergrens voor het loon waarover de vakantiebijslag berekend wordt? Het loonbedrag, in dezelfde periode als 'van'.",
        eenheid="€",
    )
    loon_maximum: float | None = veld(
        "cao_pdf/vakantiebijslag/regel/loon-maximum",
        "Is er een bovengrens voor het loon waarover de vakantiebijslag berekend wordt (bijv. het maximumdagloon)? Het loonbedrag, in dezelfde periode als 'van'.",
        eenheid="€",
    )
    naar_rato_deeltijd: JaNee | None = veld(
        "cao_pdf/vakantiebijslag/regel/rato-deeltijd",
        "Wordt de vakantiebijslag naar rato van het deeltijdpercentage (de arbeidsduur) toegekend?",
        vraagtype="radio",
    )
    naar_rato_dienstverband: JaNee | None = veld(
        "cao_pdf/vakantiebijslag/regel/rato-dienstverband",
        "Wordt de vakantiebijslag naar rato van de duur van het dienstverband toegekend (bijv. bij korter dan een jaar in dienst)?",
        vraagtype="radio",
    )
    voorwaarden: list[Voorwaarde] = veld(
        "cao_pdf/vakantiebijslag/regel/voorwaarden",
        "Onder welke voorwaarden geldt dit tarief (leeftijd, duur dienstverband, salarisschaal, of iets anders)? "
        "Leeg laten als het tarief voor iedereen geldt.",
        lijst=True,
    )


class VakantiebijslagSETU(FormulierModel):
    ja_nee: JaNee | None = veld("cao_pdf/vakantiebijslag/ja-nee", "Is er een vakantiebijslag?", vraagtype="radio")
    geldig_van: dt.date | None = veld(
        "cao_pdf/vakantiebijslag/geldig-van",
        "Vanaf welke datum geldt deze regeling voor de vakantiebijslag, als de cao dat noemt?",
        toon_als=Als("ja_nee", JaNee.JA),
    )
    geldig_tot: dt.date | None = veld(
        "cao_pdf/vakantiebijslag/geldig-tot",
        "Tot en met welke datum geldt deze regeling voor de vakantiebijslag, als de cao dat noemt?",
        toon_als=Als("ja_nee", JaNee.JA),
    )
    uitbetaling_maand: int | None = veld(
        "cao_pdf/vakantiebijslag/uitbetaling-maand",
        "In welke maand wordt de vakantiebijslag uitbetaald (1 = januari, 12 = december)? Alleen als het één vaste maand is.",
        toon_als=Als("ja_nee", JaNee.JA),
        ge=1,
        le=12,
    )
    toelichting: str | None = veld(
        "cao_pdf/vakantiebijslag/toelichting",
        "Zijn er uitzonderingen of beperkingen die nergens anders passen (bijv. peildatum, uitbetaling bij einde dienstverband)? "
        "Kort, dicht bij de tekst van de cao.",
        toon_als=Als("ja_nee", JaNee.JA),
    )
    regels: list[VakantiebijslagRegel] = veld(
        "cao_pdf/vakantiebijslag/regels",
        "De tarieven van de vakantiebijslag. Eén regel per tarief.",
        lijst=True,
        toon_als=Als("ja_nee", JaNee.JA),
    )


def naar_formulier(uitgebreid: VakantiebijslagSETU) -> Vakantiebijslag:
    """De webform-vragen: ja/nee en het bedrag van de eerste regel (de webform kent alleen een percentage)."""
    bedrag = None
    if uitgebreid.ja_nee == JaNee.JA and uitgebreid.regels:
        eerste = uitgebreid.regels[0].bedrag
        if eerste is not None and eerste.soort == BedragSoort.PERCENTAGE:
            bedrag = eerste
    return Vakantiebijslag(ja_nee=uitgebreid.ja_nee, bedrag=bedrag)


def naar_kern(
    uitgebreid: VakantiebijslagSETU, bericht: InquiryPayEquity, formulier: Formulier
) -> list[str]:
    """Zet de volledige vakantiebijslag in het kernbericht (vervangt wat de webform-koppeling maakte).
    Geeft meldingen terug over wat ontbrak of is aangenomen."""
    if uitgebreid.ja_nee != JaNee.JA:
        return []
    meldingen: list[str] = []
    jaar = (uitgebreid.geldig_van or formulier.algemeen.geldig_van or dt.date.min).year
    regeling = HolidayAllowanceArrangement(
        id=Identifier(value=ID_ARRANGEMENT, scheme_agency_id=SchemeAgencyId.CUSTOMER),
        name=NAAM,
        description=uitgebreid.toelichting or None,
        origin=Origin(type=_origin(formulier)),
        effective_period=effective_period(uitgebreid.geldig_van, uitgebreid.geldig_tot),
        line=_regels(uitgebreid, meldingen),
        pay_date=_uitbetaling(uitgebreid.uitbetaling_maand, jaar, meldingen),
    )
    bericht.holiday_allowance = [regeling]
    meldingen += _grondslag_meldingen(regeling, bericht)
    return [f"{NAAM.lower()}: {m}" for m in meldingen]


def _regels(uitgebreid: VakantiebijslagSETU, meldingen: list[str]) -> list[ArrangementLine] | None:
    regels = []
    for i, r in enumerate(uitgebreid.regels):
        pad = f"regels[{i}]"
        naar_rato = proportional(r.naar_rato_deeltijd, r.naar_rato_dienstverband, pad, meldingen)
        amount, interval = bedrag_naar_kern(
            r.bedrag, r.minimum_bedrag, r.maximum_bedrag, r.loon_minimum, r.loon_maximum, naar_rato, pad, meldingen
        )
        if amount is None:
            meldingen.append(f"{pad}: regel weggelaten")
            continue
        regels.append(
            ArrangementLine(
                line_id=Id(value=f"{ID_ARRANGEMENT}-{i + 1}"),
                amount=amount,
                interval=interval,
                conditions=conditions(r.voorwaarden, f"{pad}.voorwaarden", meldingen),
            )
        )
    return regels or None


def _uitbetaling(maand: int | None, jaar: int, meldingen: list[str]) -> Recurring | None:
    """Elk jaar op de 1e van de maand, bijv. ``R/2026-05-01/P1Y`` (ISO 8601-1 repeating interval)."""
    if maand is None:
        return None
    if jaar < 1900:
        meldingen.append("uitbetaling: geen jaar bekend om de terugkerende datum op te baseren (geldig_van ontbreekt), niet opgenomen")
        return None
    return Recurring(recurring_interval=f"R/{jaar}-{maand:02d}-01/P1Y")


def _origin(formulier: Formulier) -> OriginType:
    """Herkomst volgens 01 Algemeen; onbekend zolang dat niet is ingevuld (zoals de webform)."""
    a = formulier.algemeen
    if a.cao_of_regeling in (CaoOfRegeling.CAO, CaoOfRegeling.CAO_EN_EIGEN_REGELING):
        if a.cao_van_toepassing_omdat == CaoVanToepassingOmdat.ALGEMEEN_VERBINDEND:
            return OriginType.COLLECTIVE_LABOUR_AGREEMENT_EXTENDED
        return OriginType.COLLECTIVE_LABOUR_AGREEMENT
    if a.cao_of_regeling == CaoOfRegeling.EIGEN_REGELING:
        return OriginType.CUSTOM_LABOUR_AGREEMENT
    return OriginType.UNKNOWN


def _grondslag_meldingen(regeling: HolidayAllowanceArrangement, bericht: InquiryPayEquity) -> list[str]:
    """Een ``baseType`` verwijst naar een baseDefinition; die komt uit 15 Grondslagen, niet uit dit blok."""
    bekend = {b.base_type for b in bericht.base_definition or []}
    codes = {
        r.amount.base_amount.base_type
        for r in regeling.line or []
        if r.amount and r.amount.base_amount.base_type and r.amount.base_amount.base_type not in bekend
    }
    return [f"grondslag '{c.value}' heeft nog geen baseDefinition (sectie 15 Grondslagen)" for c in sorted(codes)]
