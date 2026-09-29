"""Beloning: salaristabellen (RemunerationPackage), functies, grondslagen en cao-gegevens."""

from ._basis import SetuModel
from .basis import AmountLimited, ArrangementLineLimited, EffectivePeriod, Id, Interval, Origin
from .codes import AllowanceCode, AmountUnitCode, BaseDefinitionCode
from .condities import Condition
from .tijd import Occurrence


# --- salaristabel
class WorkDuration(SetuModel):
    """Arbeidsduur waarvoor de tabel geldt, bijv. 40 uur per week."""

    amount: AmountLimited
    interval: Interval
    value_per_week: float


class HourlyWageConversion(SetuModel):
    hourly_wage_factor: float | None = None
    hourly_wage_percentage: float | None = None


class SalaryScaleStep(SetuModel):
    name: str
    value: float
    minimum_wage: bool | None = None
    conditions: list[Condition] | None = None


class CareerLevel(SetuModel):
    indicator: bool | None = None
    description: str | None = None


class PositionProfileReference(SetuModel):
    position_id: Id
    start_salary_step: str | None = None
    description: str | None = None


class SalaryScale(SetuModel):
    name: str
    min_value: float | None = None
    max_value: float | None = None
    currency: str
    salary_step: list[SalaryScaleStep] | None = None
    career_level: CareerLevel | None = None
    position_profile_reference: list[PositionProfileReference] | None = None


class IndividualSalaryIncrease(SetuModel):
    effective_date: Occurrence | None = None
    line: ArrangementLineLimited | None = None


class IncreaseAmount(SetuModel):
    value: float
    unit_code: AmountUnitCode


class GeneralSalaryIncrease(SetuModel):
    effective_date: Occurrence | None = None
    amount: IncreaseAmount | None = None
    description: str | None = None


class RemunerationPackage(SetuModel):
    origin: Origin
    effective_period: EffectivePeriod | None = None
    work_duration: WorkDuration
    interval: Interval | None = None
    hourly_wage_conversion: HourlyWageConversion | None = None
    salary_scale: list[SalaryScale] | None = None
    individual_salary_increase: list[IndividualSalaryIncrease] | None = None
    general_salary_increase: list[GeneralSalaryIncrease] | None = None
    conditions: list[Condition] | None = None


# --- functies
class PositionProfile(SetuModel):
    position_id: Id
    position_title: str
    origin: Origin
    reference_title: str | None = None
    work_description: str | None = None


# --- grondslagen
class AllowanceReference(SetuModel):
    type_code: AllowanceCode | None = None


class BaseDefinition(SetuModel):
    base_type: BaseDefinitionCode
    remuneration_indicator: bool
    holiday_allowance_indicator: bool
    paid_leave_day_indicator: bool
    all_allowances_indicator: bool
    allowances: list[AllowanceReference] | None = None
    reference_date: Occurrence | None = None


# --- cao / arbeidsvoorwaardenregeling
class CollectiveLabourAgreement(SetuModel):
    name: str
    id: Id
    effective_period: EffectivePeriod | None = None
    based_on: str | None = None


class LabourAgreements(SetuModel):
    industry_identifier: list[Id] | None = None
    collective_labour_agreement: CollectiveLabourAgreement | None = None
    custom_labour_agreement: bool | None = None

