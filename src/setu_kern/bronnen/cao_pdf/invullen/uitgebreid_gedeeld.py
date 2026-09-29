"""Bouwstenen voor het uitgebreide invullen: de SETU-velden die de wijzerbelonen-webform niet vraagt.

Dezelfde velden komen bij bijna elke regeling terug (zie docs/gap_analyse_setu.md): geldigheidsperiode, minimum en
maximum, naar rato, voorwaarden. Ze zijn hier één keer uitgewerkt, zodat een nieuwe regeling ze kan hergebruiken:

- het LLM-model (``Voorwaarde``, met ``veld()`` zoals het formulier, zodat schema, prompt en controle hetzelfde werken);
- de omzetting naar het kernmodel (``effective_period``, ``proportional``, ``conditions``, ``bedrag_naar_kern``).

Elke omzetting geeft meldingen terug voor wat ontbrak en is aangenomen. Een lege vraag blijft leeg: "niet gevonden"
is iets anders dan "nee".
"""

import datetime as dt

from ....kern.basis import Amount, BaseAmount, EffectivePeriod, Interval, Proportional
from ....kern.codes import (
    AmountUnitCode,
    BaseDefinitionCode,
    BaseUnitCode,
    IntervalCode,
    Operator,
    ReferenceDateType,
)
from ....kern.condities import (
    AgeCondition,
    Condition,
    EmploymentDurationCondition,
    SalaryScaleCondition,
    TextCondition,
)
from ...wijzerbelonen.formulier._basis import FormulierModel, Keuze, veld
from ...wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort
from ...wijzerbelonen.formulier.codes import JaNee, Peildatum
from ...wijzerbelonen.formulier.voorwaarden import Als

STANDAARD_PEILDATUM = ReferenceDateType.HIRE_DATE


# --- voorwaarden (SETU ``conditions``)
class VoorwaardeSoort(Keuze):
    LEEFTIJD = "leeftijd", "Leeftijd"
    DIENSTVERBAND = "dienstverband", "Duur van het dienstverband"
    SALARISSCHAAL = "salarisschaal", "Salarisschaal (en eventueel trede)"
    TEKST = "tekst", "Andere voorwaarde, in eigen woorden"


class Vergelijking(Keuze):
    GELIJK = "eq", "is gelijk aan"
    MEER_DAN = "gt", "meer dan"
    VANAF = "gte", "vanaf / ten minste"
    MINDER_DAN = "lt", "minder dan"
    TOT_EN_MET = "lte", "tot en met / ten hoogste"


_MET_VERGELIJKING = Als("soort", VoorwaardeSoort.LEEFTIJD, VoorwaardeSoort.DIENSTVERBAND, VoorwaardeSoort.SALARISSCHAAL)


class Voorwaarde(FormulierModel):
    """Eén voorwaarde waaronder een regel geldt. Meerdere voorwaarden bij een regel gelden allemaal tegelijk."""

    soort: VoorwaardeSoort | None = veld("cao_pdf/voorwaarde/soort", "Soort voorwaarde", vraagtype="radio")
    vergelijking: Vergelijking | None = veld(
        "cao_pdf/voorwaarde/vergelijking", "Vergelijking (bijv. 'vanaf' bij 'vanaf 21 jaar')", toon_als=_MET_VERGELIJKING
    )
    leeftijd: float | None = veld(
        "cao_pdf/voorwaarde/leeftijd", "Leeftijd", eenheid="jaar", toon_als=Als("soort", VoorwaardeSoort.LEEFTIJD)
    )
    duur_jaren: float | None = veld(
        "cao_pdf/voorwaarde/duur", "Duur van het dienstverband", eenheid="jaar", toon_als=Als("soort", VoorwaardeSoort.DIENSTVERBAND)
    )
    peildatum: Peildatum | None = veld(
        "cao_pdf/voorwaarde/peildatum",
        "Vanaf welk moment wordt de duur van het dienstverband geteld? Alleen invullen als de cao dat zegt.",
        vraagtype="keuzelijst",
        toon_als=Als("soort", VoorwaardeSoort.DIENSTVERBAND),
    )
    salarisschaal: str | None = veld(
        "cao_pdf/voorwaarde/salarisschaal", "Naam van de salarisschaal", toon_als=Als("soort", VoorwaardeSoort.SALARISSCHAAL)
    )
    trede: str | None = veld(
        "cao_pdf/voorwaarde/trede", "Trede in de salarisschaal, als de cao die noemt", toon_als=Als("soort", VoorwaardeSoort.SALARISSCHAAL)
    )
    tekst: str | None = veld(
        "cao_pdf/voorwaarde/tekst", "De voorwaarde in eigen woorden, dicht bij de tekst van de cao", toon_als=Als("soort", VoorwaardeSoort.TEKST)
    )


def conditions(voorwaarden: list[Voorwaarde], pad: str, meldingen: list[str]) -> list[Condition] | None:
    """Voorwaarden → SETU-conditions. Een voorwaarde met te weinig gegevens valt weg, met een melding."""
    uit: list[Condition] = []
    for i, v in enumerate(voorwaarden):
        plek = f"{pad}[{i}]"
        operator = Operator(v.vergelijking.value) if v.vergelijking else None
        if v.soort == VoorwaardeSoort.LEEFTIJD and operator and v.leeftijd is not None:
            uit.append(AgeCondition(operator=operator, age=v.leeftijd))
        elif v.soort == VoorwaardeSoort.DIENSTVERBAND and operator and v.duur_jaren is not None:
            peildatum = ReferenceDateType(v.peildatum.value) if v.peildatum else STANDAARD_PEILDATUM
            if not v.peildatum:
                meldingen.append(f"{plek}: peildatum voor de duur van het dienstverband niet genoemd, '{peildatum.value}' aangenomen")
            uit.append(EmploymentDurationCondition(operator=operator, duration=_jaren(v.duur_jaren), reference_date_type=peildatum))
        elif v.soort == VoorwaardeSoort.SALARISSCHAAL and operator and v.salarisschaal:
            uit.append(SalaryScaleCondition(operator=operator, salary_scale=v.salarisschaal, step=v.trede or None))
        elif v.soort == VoorwaardeSoort.TEKST and v.tekst:
            uit.append(TextCondition(description=v.tekst))
        else:
            meldingen.append(f"{plek}: voorwaarde ({v.soort.value if v.soort else 'zonder soort'}) is onvolledig en is weggelaten")
    return uit or None


def _jaren(jaren: float) -> str:
    """Duur als ISO 8601, bijv. 5 → ``P5Y``."""
    return f"P{int(jaren) if float(jaren).is_integer() else jaren}Y"


# --- geldigheidsperiode (SETU ``effectivePeriod``)
def effective_period(geldig_van: dt.date | None, geldig_tot: dt.date | None) -> EffectivePeriod | None:
    if geldig_van is None and geldig_tot is None:
        return None
    return EffectivePeriod(valid_from=geldig_van, valid_to=geldig_tot)


# --- naar rato (SETU ``proportional``)
def proportional(deeltijd: JaNee | None, dienstverband: JaNee | None, pad: str, meldingen: list[str]) -> Proportional | None:
    """Beide velden zijn bij SETU verplicht zodra ``proportional`` er is. Is er maar één beantwoord, dan geldt de
    ander als 'nee' (met een melding), omdat de cao er dan niets over zegt."""
    if deeltijd is None and dienstverband is None:
        return None
    for naam, waarde in (("deeltijdpercentage", deeltijd), ("duur van het dienstverband", dienstverband)):
        if waarde is None:
            meldingen.append(f"{pad}: naar rato van {naam} niet genoemd in de cao, als 'nee' opgenomen (SETU vereist beide)")
    return Proportional(part_time_percentage=deeltijd == JaNee.JA, employment_duration=dienstverband == JaNee.JA)


# --- bedrag (SETU ``amount`` en ``interval``)
def bedrag_naar_kern(
    bedrag: Bedragregel | None,
    minimum: float | None,
    maximum: float | None,
    grondslag_minimum: float | None,
    grondslag_maximum: float | None,
    naar_rato: Proportional | None,
    pad: str,
    meldingen: list[str],
) -> tuple[Amount | None, Interval | None]:
    """Een Bedragregel (percentage of vast bedrag) met grenzen → ``Amount`` en ``Interval`` van de kern."""
    if bedrag is None or bedrag.soort is None:
        meldingen.append(f"{pad}: geen bedrag ingevuld")
        return None, None
    if bedrag.soort == BedragSoort.PERCENTAGE and bedrag.percentage:
        p = bedrag.percentage
        if p.percentage is None or p.basis is None:
            meldingen.append(f"{pad}: percentage of loonbasis ontbreekt")
            return None, None
        basis = BaseAmount(
            unit_code=BaseUnitCode(p.basis.value),
            base_type=BaseDefinitionCode(p.grondslag.value) if p.grondslag else None,
            min_value=grondslag_minimum,
            max_value=grondslag_maximum,
        )
        amount = Amount(
            value=p.percentage,
            unit_code=AmountUnitCode.PERCENTAGE,
            base_amount=basis,
            min_value=minimum,
            max_value=maximum,
            proportional=naar_rato,
        )
        per = p.per
    elif bedrag.soort == BedragSoort.VAST_BEDRAG and bedrag.vast_bedrag:
        v = bedrag.vast_bedrag
        if v.bedrag is None:
            meldingen.append(f"{pad}: bedrag ontbreekt")
            return None, None
        if grondslag_minimum is not None or grondslag_maximum is not None:
            meldingen.append(f"{pad}: grens op het loon genegeerd, want een vast bedrag heeft geen loon als grondslag")
        amount = Amount(
            value=v.bedrag,
            unit_code=AmountUnitCode.EURO,
            base_amount=BaseAmount(unit_code=BaseUnitCode.FIXED),
            min_value=minimum,
            max_value=maximum,
            proportional=naar_rato,
        )
        per = v.per
    else:
        meldingen.append(f"{pad}: soort bedrag '{bedrag.soort.value}' wordt hier niet ondersteund")
        return None, None
    if per is None:
        meldingen.append(f"{pad}: 'per' ontbreekt, geen interval opgenomen")
        return amount, None
    return amount, Interval(value=1, unit_code=IntervalCode(per.value))
