"""Gedeelde bouwstenen van SETU: identificatie, perioden, bedragen, intervallen en regels (lines)."""

import datetime as dt
from typing import Literal

from ._basis import SetuModel
from .codes import (
    AmountUnitCode,
    BaseDefinitionCode,
    BaseUnitCode,
    ContributionSource,
    IkbRelationType,
    IntervalCode,
    OriginType,
    SchemeAgencyId,
    Weekday,
)
from .condities import Condition


# --- identificatie en herkomst
class Id(SetuModel):
    value: str


class Identifier(SetuModel):
    value: str
    scheme_agency_id: SchemeAgencyId


class Origin(SetuModel):
    """LabourAgreementReference: waar de regeling vandaan komt (cao, eigen regeling, ...)."""

    type: OriginType


class EffectivePeriod(SetuModel):
    valid_from: dt.date | None = None
    valid_to: dt.date | None = None


# --- bedragen en intervallen
class BaseAmount(SetuModel):
    """Waarover een bedrag of percentage berekend wordt (bijv. 8% over het ``YearlyRate`` van ``GrossSalary``)."""

    unit_code: BaseUnitCode
    base_type: BaseDefinitionCode | None = None
    value: float | None = None
    min_value: float | None = None
    max_value: float | None = None


class Proportional(SetuModel):
    """Naar rato van deeltijdpercentage en/of duur van het dienstverband."""

    part_time_percentage: bool
    employment_duration: bool
    description: str | None = None


class Amount(SetuModel):
    value: float
    min_value: float | None = None
    max_value: float | None = None
    unit_code: AmountUnitCode
    base_amount: BaseAmount
    proportional: Proportional | None = None


class AmountLeaveDay(SetuModel):
    value: float
    min_value: float | None = None
    max_value: float | None = None
    unit_code: AmountUnitCode
    base_amount: BaseAmount


class AmountLimited(SetuModel):
    value: float
    unit_code: Literal["Hour"] = "Hour"


class Interval(SetuModel):
    """Per hoeveel eenheden het bedrag geldt, bijv. ``Interval(value=1, unit_code=IntervalCode.MONTH)``."""

    value: float
    unit_code: IntervalCode


class IkbReference(SetuModel):
    relation_type: IkbRelationType
    id: Id
    description: str | None = None


# --- regels (lines)
class ArrangementLine(SetuModel):
    line_id: Id | None = None
    amount: Amount | None = None
    interval: Interval | None = None
    conditions: list[Condition] | None = None
    contribution_source: ContributionSource | None = None
    ikb_reference: list[IkbReference] | None = None


class ArrangementLineLimited(SetuModel):
    line_id: Id | None = None
    amount: Amount | None = None
    interval: Interval | None = None
    conditions: list[Condition] | None = None
    contribution_source: ContributionSource | None = None


class ArrangementLineLeave(SetuModel):
    name: str | None = None
    description: str | None = None
    line_id: Id | None = None
    amount: Amount | None = None
    interval: Interval | None = None
    conditions: list[Condition] | None = None
    contribution_source: ContributionSource | None = None
    leave_day_value: AmountLeaveDay | None = None
    ikb_reference: list[IkbReference] | None = None


# --- perioden (wanneer geldt een toeslag)
class DatePeriod(SetuModel):
    start: dt.date
    end: dt.date | None = None


class TimePeriod(SetuModel):
    start: dt.time
    end: dt.time


class WeekdayCode(SetuModel):
    value: Weekday | None = None


class Period(SetuModel):
    date_period: list[DatePeriod] | None = None
    time_period: TimePeriod
    weekday: list[WeekdayCode] | None = None


class Description(SetuModel):
    """Element met alleen een omschrijving (MandatoryLeave, Franchise)."""

    description: str | None = None


class RequiredDescription(SetuModel):
    """Element met een verplichte omschrijving (IndividualChoiceBudgetOption)."""

    description: str
