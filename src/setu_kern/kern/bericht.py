"""InquiryPayEquity: het complete SETU-bericht, met inlezen, wegschrijven en valideren."""

import copy
import datetime as dt
import json
import re
from functools import cache
from pathlib import Path
from typing import Any, Self

from pydantic import Field, PrivateAttr, ValidationError

from ._basis import SetuModel
from .basis import EffectivePeriod, Id, Identifier
from .beloning import BaseDefinition, LabourAgreements, PositionProfile, RemunerationPackage
from .partij import Party
from .regelingen import (
    AllowanceArrangement,
    HolidayAllowanceArrangement,
    IndividualChoiceBudgetArrangement,
    LeaveArrangement,
    OtherArrangement,
    PensionArrangement,
    SickPayArrangement,
    SupplementaryArrangement,
    SustainableEmployabilityArrangement,
)
from .tijd import DATUM_TIJD
from .tolerant import normaliseer, verwijder_op_pad

SCHEMA_PAD = Path(__file__).parent / "schema" / "inquiry_pay_equity_2.0.0_draft.json"


@cache
def officieel_schema() -> dict:
    return json.loads(SCHEMA_PAD.read_text(encoding="utf-8"))


class InquiryPayEquity(SetuModel):
    """SETU Inquiry Pay Equity v2.0.

    Velden buiten de standaard (bijv. ``__webform_data__`` van wijzerbelonen) worden bij inlezen apart
    bewaard in ``extensies`` en bij wegschrijven weer toegevoegd.
    """

    document_id: Identifier
    version_id: Id | None = None
    issued: dt.datetime | None = None
    effective_period: EffectivePeriod
    customer: Party
    base_definition: list[BaseDefinition] | None = None
    labour_agreements: LabourAgreements | None = None
    position_profile: list[PositionProfile] | None = None
    remuneration: list[RemunerationPackage] = Field(min_length=1)
    allowance: list[AllowanceArrangement] | None = None
    holiday_allowance: list[HolidayAllowanceArrangement] | None = None
    sick_pay: list[SickPayArrangement] | None = None
    leave: list[LeaveArrangement] | None = None
    individual_choice_budget: list[IndividualChoiceBudgetArrangement] | None = None
    pension: list[PensionArrangement] | None = None
    sustainable_employability: list[SustainableEmployabilityArrangement] | None = None
    supplementary_arrangement: list[SupplementaryArrangement] | None = None
    other_arrangement: list[OtherArrangement] | None = None

    _extensies: dict[str, Any] = PrivateAttr(default_factory=dict)

    @property
    def extensies(self) -> dict[str, Any]:
        return self._extensies

    # --- inlezen
    @classmethod
    def lees(cls, bron: str | Path | dict) -> Self:
        """Streng inlezen: alles wat niet aan het schema voldoet geeft een ValidationError."""
        data, extensies = cls._splits(_laad(bron))
        bericht = cls.model_validate(data)
        bericht._extensies = extensies
        return bericht

    @classmethod
    def lees_tolerant(cls, bron: str | Path | dict, max_verwijderingen: int = 100) -> tuple[Self, list[str]]:
        """Tolerant inlezen: bekende afwijkingen worden rechtgezet; onderdelen die dan nog ongeldig zijn,
        worden weggelaten. Geeft het bericht en de lijst meldingen terug.
        Verplichte onderdelen op het hoogste niveau kunnen niet weggelaten worden (dan volgt een ValidationError).
        """
        data, extensies = cls._splits(_laad(bron))
        data, meldingen = normaliseer(data)
        for _ in range(max_verwijderingen):
            try:
                bericht = cls.model_validate(data)
                break
            except ValidationError as fout:
                eerste = fout.errors()[0]
                pad = verwijder_op_pad(data, eerste["loc"])
                if pad is None:
                    raise
                meldingen.append(f"{pad}: weggelaten ({eerste['msg']})")
        else:
            raise ValueError(f"Meer dan {max_verwijderingen} ongeldige onderdelen")
        bericht._extensies = extensies
        return bericht, meldingen

    @classmethod
    def _splits(cls, data: dict) -> tuple[dict, dict]:
        bekend = {info.alias or naam for naam, info in cls.model_fields.items()} | set(cls.model_fields)
        return (
            {k: v for k, v in data.items() if k in bekend},
            {k: v for k, v in data.items() if k not in bekend},
        )

    # --- wegschrijven
    def naar_dict(self, met_extensies: bool = True) -> dict[str, Any]:
        uit = self.model_dump(mode="json", exclude_none=True)
        if met_extensies:
            uit.update(copy.deepcopy(self._extensies))
        return uit

    def naar_json(self, met_extensies: bool = True, indent: int = 2) -> str:
        return json.dumps(self.naar_dict(met_extensies), indent=indent, ensure_ascii=False)

    def schrijf(self, pad: str | Path, met_extensies: bool = True) -> None:
        Path(pad).write_text(self.naar_json(met_extensies) + "\n", encoding="utf-8")

    # --- valideren
    def valideer(self) -> list[str]:
        """Controleert het bericht (zonder extensies) met het officiële JSON-schema. Lege lijst = geldig."""
        return valideer_json(self.naar_dict(met_extensies=False))


_DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _formaten():
    """Controle van ``format: date-time`` en ``date`` (RFC 3339), zoals de validator in de wijzerbelonen-webform.

    ``jsonschema`` controleert date-time alleen als het pakket rfc3339-validator geïnstalleerd is; zonder die
    controle zou een datum zonder tijd (bijv. ``"2026-12-15"`` bij ``Single.date``) onterecht goedgekeurd worden.
    """
    from jsonschema import FormatChecker

    checker = FormatChecker()

    @checker.checks("date-time")
    def _datum_tijd(waarde: object) -> bool:
        return not isinstance(waarde, str) or bool(DATUM_TIJD.match(waarde))

    @checker.checks("date")
    def _datum(waarde: object) -> bool:
        return not isinstance(waarde, str) or bool(_DATUM.match(waarde))

    return checker


def valideer_json(data: dict) -> list[str]:
    """Valideert willekeurige JSON-data met het officiële SETU-schema, inclusief datum(-tijd)formaten."""
    from jsonschema import Draft202012Validator

    validator = Draft202012Validator(officieel_schema(), format_checker=_formaten())
    return [
        f"{'/'.join(map(str, fout.absolute_path)) or '(root)'}: {fout.message}"
        for fout in sorted(validator.iter_errors(data), key=lambda f: list(map(str, f.absolute_path)))
    ]


def _laad(bron: str | Path | dict) -> dict:
    if isinstance(bron, dict):
        return copy.deepcopy(bron)
    if isinstance(bron, Path) or (isinstance(bron, str) and not bron.lstrip().startswith("{")):
        return json.loads(Path(bron).read_text(encoding="utf-8"))
    return json.loads(bron)
