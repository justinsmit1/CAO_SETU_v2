"""Tests voor het SETU-kernmodel (src/cao_setu_v2/setu/)."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cao_setu_v2.setu import InquiryPayEquity, valideer_json
from cao_setu_v2.setu.conformiteit import verschillen

VOORBEELD = Path(__file__).parents[1] / "docs" / "setu_bron" / "InquiryPayEquity"


def _voorbeeld() -> dict:
    tekst = VOORBEELD.read_text(encoding="utf-8")
    return json.loads(tekst[tekst.index("{") :])


MINIMAAL = {
    "documentId": {"value": "regeling-1", "schemeAgencyId": "Customer"},
    "effectivePeriod": {"validFrom": "2026-01-01"},
    "customer": {
        "name": "Voorbeeld B.V.",
        "legalId": [{"value": "12345678", "schemeAgencyId": "KvK"}],
        "personContacts": [{"name": {"formattedName": "J. Jansen"}}],
    },
    "remuneration": [
        {
            "origin": {"type": "Unknown"},
            "workDuration": {"amount": {"value": 40, "unitCode": "Hour"}, "interval": {"value": 1, "unitCode": "Week"}, "valuePerWeek": 40},
        }
    ],
    "__webform_data__": {"appVersion": "2.1.0", "answers": {"id": "regeling-1"}},
}


def test_model_komt_overeen_met_officieel_schema():
    assert verschillen() == []


def test_minimaal_bericht_is_geldig_en_blijft_gelijk():
    bericht = InquiryPayEquity.lees(MINIMAAL)
    assert bericht.valideer() == []
    assert bericht.customer.name == "Voorbeeld B.V."
    assert InquiryPayEquity.lees(bericht.naar_dict()) == bericht


def test_extensies_blijven_bewaard():
    bericht = InquiryPayEquity.lees(MINIMAAL)
    assert bericht.extensies == {"__webform_data__": MINIMAAL["__webform_data__"]}
    assert bericht.naar_dict()["__webform_data__"] == MINIMAAL["__webform_data__"]
    assert "__webform_data__" not in bericht.naar_dict(met_extensies=False)


def test_streng_inlezen_weigert_onbekende_velden():
    with pytest.raises(ValidationError):
        InquiryPayEquity.lees({**MINIMAAL, "customer": {**MINIMAAL["customer"], "onbekend": 1}})


def test_officieel_voorbeeld_streng_ongeldig():
    with pytest.raises(ValidationError):
        InquiryPayEquity.lees(_voorbeeld())
    assert valideer_json(_voorbeeld()) != []


def test_officieel_voorbeeld_tolerant():
    bericht, meldingen = InquiryPayEquity.lees_tolerant(_voorbeeld())
    assert meldingen
    assert bericht.valideer() == []
    assert InquiryPayEquity.lees(bericht.naar_dict()) == bericht
    # Een losse datum bij Recurring wordt een jaarlijkse ISO 8601-reeks.
    peildatum = bericht.naar_dict()["baseDefinition"][0]["referenceDate"]
    assert peildatum["recurringInterval"].startswith("R/") and peildatum["recurringInterval"].endswith("/P1Y")


def test_recurring_wordt_onder_beide_namen_geschreven():
    grondslag = {
        "baseType": "BaseWage",
        "remunerationIndicator": True,
        "holidayAllowanceIndicator": False,
        "paidLeaveDayIndicator": False,
        "allAllowancesIndicator": False,
        "referenceDate": {"occurrenceType": "Recurring", "interval": "R/2026-06-01/P1Y"},
    }
    data = {**MINIMAAL, "baseDefinition": [grondslag]}
    bericht = InquiryPayEquity.lees(data)
    uit = bericht.naar_dict()["baseDefinition"][0]["referenceDate"]
    assert uit["interval"] == uit["recurringInterval"] == "R/2026-06-01/P1Y"
    assert bericht.valideer() == []


def test_condities_kiezen_de_juiste_soort():
    from cao_setu_v2.setu import condities

    regel = {
        "name": "Toeslag",
        "origin": {"type": "Unknown"},
        "typeCode": "EA100",
        "line": [
            {
                "amount": {"value": 10, "unitCode": "Percentage", "baseAmount": {"unitCode": "HourlyRate"}},
                "conditions": [
                    {"conditionType": "Age", "operator": "gte", "age": 21},
                    {"conditionType": "Not", "condition": {"conditionType": "Text", "description": "niet op zondag"}},
                ],
            }
        ],
    }
    bericht = InquiryPayEquity.lees({**MINIMAAL, "allowance": [regel]})
    c = bericht.allowance[0].line[0].conditions
    assert isinstance(c[0], condities.AgeCondition)
    assert isinstance(c[1], condities.NotCondition)
    assert isinstance(c[1].condition, condities.TextCondition)
    assert bericht.valideer() == []
