"""De arbeidsvoorwaarden-regelingen: toeslagen, vakantiebijslag, ziekte, verlof, IKB, pensioen, ..."""

from ._basis import SetuModel
from .basis import (
    Amount,
    ArrangementLine,
    ArrangementLineLeave,
    Description,
    EffectivePeriod,
    Id,
    Identifier,
    Origin,
    Period,
    RequiredDescription,
)
from .codes import (
    AllowanceCode,
    AllowanceRelationType,
    IntervalHourDayUnitCode,
    SupplementaryArrangementCode,
    SustainabilityCode,
)
from .condities import Condition
from .tijd import Occurrence


class Arrangement(SetuModel):
    """Velden die elke regeling heeft."""

    id: Identifier | None = None
    name: str
    description: str | None = None
    origin: Origin
    effective_period: EffectivePeriod | None = None


class AllowanceReferenceExtended(SetuModel):
    """Relatie met een andere toeslag, bijv. cumulatief met de onregelmatigheidstoeslag."""

    id: Id | None = None
    type_code: AllowanceCode | None = None
    relation_type: AllowanceRelationType | None = None
    description: str


class AllowanceArrangement(Arrangement):
    type_code: AllowanceCode
    period: list[Period] | None = None
    line: list[ArrangementLine] | None = None
    pay_date: Occurrence | None = None
    reference: list[AllowanceReferenceExtended] | None = None
    phase_out_scheme: str | None = None


class HolidayAllowanceArrangement(Arrangement):
    line: list[ArrangementLine] | None = None
    pay_date: Occurrence | None = None


class WaitingDays(SetuModel):
    value: float
    unit_code: IntervalHourDayUnitCode
    conditions: list[Condition] | None = None


class SickPayArrangement(Arrangement):
    waiting_days: WaitingDays | None = None
    line: list[ArrangementLine] | None = None


class LeaveArrangement(Arrangement):
    paid_leave: list[ArrangementLineLeave] | None = None
    working_hours_reduction: list[ArrangementLineLeave] | None = None
    holidays: list[ArrangementLineLeave] | None = None
    special_leave: list[ArrangementLineLeave] | None = None
    additional_parental_leave: list[ArrangementLineLeave] | None = None
    mandatory_leave_allocation: Description | None = None


class IndividualChoiceBudgetArrangement(Arrangement):
    line: list[ArrangementLine] | None = None
    option: list[RequiredDescription] | None = None


class PensionArrangement(Arrangement):
    line: list[ArrangementLine] | None = None
    franchise: Description | None = None


class SustainableEmployabilityArrangement(Arrangement):
    type_code: SustainabilityCode
    line: list[ArrangementLine] | None = None
    pay_date: Occurrence | None = None


class SupplementaryArrangement(Arrangement):
    type_code: SupplementaryArrangementCode
    line: list[ArrangementLine] | None = None
    coverage: Amount | None = None


class OtherArrangement(Arrangement):
    line: list[ArrangementLine] | None = None
    coverage: Amount | None = None
