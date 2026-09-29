"""Condition: voorwaarden bij een regel, gekozen op ``conditionType`` (9 soorten, deels genest)."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from ._basis import SetuModel
from .codes import Operator, ReferenceDateType
from .tijd import Occurrence


class AgeCondition(SetuModel):
    condition_type: Literal["Age"] = "Age"
    operator: Operator
    age: float


class EmploymentDurationCondition(SetuModel):
    condition_type: Literal["EmploymentDuration"] = "EmploymentDuration"
    operator: Operator
    duration: str  # ISO 8601-duur, bijv. "P5Y"
    reference_date_type: ReferenceDateType


class OccurrenceCondition(SetuModel):
    condition_type: Literal["Occurrence"] = "Occurrence"
    occurrence: Occurrence


class PositionProfileCondition(SetuModel):
    condition_type: Literal["PositionProfile"] = "PositionProfile"
    operator: Literal[Operator.IN] = Operator.IN
    position_profile_ids: list[str]


class SalaryScaleCondition(SetuModel):
    condition_type: Literal["SalaryScale"] = "SalaryScale"
    operator: Operator
    salary_scale: str
    step: str | None = None


class TextCondition(SetuModel):
    """Vrije tekst, voor voorwaarden die (nog) niet gestructureerd vast te leggen zijn."""

    condition_type: Literal["Text"] = "Text"
    description: str


class AllOfCondition(SetuModel):
    condition_type: Literal["AllOf"] = "AllOf"
    conditions: list[Condition] = Field(min_length=1)


class AnyOfCondition(SetuModel):
    condition_type: Literal["AnyOf"] = "AnyOf"
    conditions: list[Condition] = Field(min_length=1)


class NotCondition(SetuModel):
    condition_type: Literal["Not"] = "Not"
    condition: Condition


Condition = Annotated[
    AgeCondition
    | EmploymentDurationCondition
    | OccurrenceCondition
    | PositionProfileCondition
    | SalaryScaleCondition
    | TextCondition
    | AllOfCondition
    | AnyOfCondition
    | NotCondition,
    Field(discriminator="condition_type"),
]

for _model in (AllOfCondition, AnyOfCondition, NotCondition):
    _model.model_rebuild()
