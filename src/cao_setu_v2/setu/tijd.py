"""Occurrence: een moment in de tijd (Single / Recurring / Relative), gekozen op ``occurrenceType``."""

import re
from typing import Annotated, Any, Literal

from pydantic import Field, field_validator, model_serializer, model_validator

from ._basis import SetuModel
from .codes import RelativeEvent


DATUM_TIJD = re.compile(r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})$")
"""RFC 3339 date-time, zoals het schema eist bij ``Single.date`` (``format: date-time``)."""


class Single(SetuModel):
    """Eén vast moment, bijv. ``"2026-01-01T00:00:00+01:00"``.

    Het schema eist een datum mét tijd (``format: date-time``), al gebruiken de voorbeelden in het schema zelf een
    losse datum. De wijzerbelonen-webform controleert hierop; tolerant inlezen zet een losse datum om.
    """

    occurrence_type: Literal["Single"] = "Single"
    date: str

    @field_validator("date")
    @classmethod
    def _datum_tijd(cls, waarde: str) -> str:
        if not DATUM_TIJD.match(waarde):
            raise ValueError(f"'{waarde}' is geen datum met tijd (verwacht bijv. '2026-12-15T00:00:00+01:00')")
        return waarde


class Recurring(SetuModel):
    """Terugkerend moment volgens ISO 8601-1, bijv. ``"R/2026-01-01/P1Y"`` (elk jaar op 1 januari).

    Het schema *vereist* ``interval`` maar *definieert* ``recurringInterval`` (fout in het schema).
    Daarom lezen we beide namen en schrijven we de waarde onder beide namen weg.
    """

    occurrence_type: Literal["Recurring"] = "Recurring"
    recurring_interval: str

    @model_validator(mode="before")
    @classmethod
    def _interval_als_alias(cls, data: Any) -> Any:
        if isinstance(data, dict) and "interval" in data:
            data = dict(data)
            waarde = data.pop("interval")
            if "recurringInterval" not in data and "recurring_interval" not in data:
                data["recurringInterval"] = waarde
        return data

    @model_serializer(mode="wrap")
    def _schrijf_beide_namen(self, handler: Any) -> dict:
        uit = handler(self)
        sleutel = "recurringInterval" if "recurringInterval" in uit else "recurring_interval"
        if sleutel in uit:
            uit["interval"] = uit[sleutel]
        return uit


class Relative(SetuModel):
    """Moment ten opzichte van een gebeurtenis, bijv. 1 jaar na ziekmelding: ``event=SICK_LEAVE, offset="P1Y"``."""

    occurrence_type: Literal["Relative"] = "Relative"
    event: RelativeEvent
    offset: str
    event_name: str | None = None


Occurrence = Annotated[Single | Recurring | Relative, Field(discriminator="occurrence_type")]
