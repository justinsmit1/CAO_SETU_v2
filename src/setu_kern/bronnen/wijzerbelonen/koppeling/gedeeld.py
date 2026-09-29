"""Gedeelde omzettingen uit de webform: src/definition/util.ts en util_question_makers.tsx (v2.1.0)."""

from typing import Any

from .motor import Antwoorden, Pad, keuze_waarde, tekst_waarde, to_float

# --- vaste posities in SETU-lijsten (src/definition/constants.ts)
HOLIDAY_ALLOWANCE_PERCENTAGE_PERIOD, HOLIDAY_ALLOWANCE_PERCENTAGE_MINIMUM = range(2)

(
    ALLOWANCE_PAID_BREAKS,
    ALLOWANCE_TRAVEL_HOME_WORK_OV,
    ALLOWANCE_TRAVEL_WORK_WORK_OV,
    ALLOWANCE_TRAVEL_OTHER,
    ALLOWANCE_REISKOSTEN,
    ALLOWANCE_STANDBY,
    ALLOWANCE_ZORGVERZEKERING,
    ALLOWANCE_THUISWERKVERGOEDING,
    ALLOWANCE_INTERNETVERGOEDING,
    ALLOWANCE_ONREGELMATIGHEIDS_TOESLAGEN,
    ALLOWANCE_PLOEGETOESLAGEN,
    ALLOWANCE_TOESLAGEN_VERSCHOVEN_DIENSTEN,
    ALLOWANCE_TOESLAGEN_FYSIEKE_BELAS,
    ALLOWANCE_TOESLAGEN_STANDBY,
    ALLOWANCE_OVERWERK_TOESLAG,
    ALLOWANCE_WAARNEMINGSTOESLAG,
    ALLOWANCE_PERFORMANCETOESLAG,
    ALLOWANCE_TIJD_VOOR_TIJD,
    ALLOWANCE_TOESLAGEN_ANDERS,
    ALLOWANCE_KOFFIEGELD,
    ALLOWANCE_MAALTIJDVERGOEDING,
    ALLOWANCE_WASVERGOEDING,
    ALLOWANCE_VERGOEDING_BEDRIJFSKLEDING_SCHOENEN,
    ALLOWANCE_ARBO_VERGOEDING,
    ALLOWANCE_BYOD_VERGOEDING,
    ALLOWANCE_VERGOEDING_ANDERS,
    ALLOWANCE_MOBILITEITSVERGOEDING,
    ALLOWANCE_REGELING_LEASEAUTO,
    ALLOWANCE_REGELING_LEASEFIETS,
    ALLOWANCE_REGELING_OV_VERGOEDING,
    ALLOWANCE_FIETSREGELING,
    ALLOWANCE_EENMALIGE_UITKERINGEN,
    ALLOWANCE_VASTE_UITKERINGEN,
    ALLOWANCE_JUBILEUMUITKERING,
    ALLOWANCE_VARIABELE_UITKERINGEN,
    ALLOWANCE_WACHTDAGCOMPENSATIE,
    ALLOWANCE_ONGEVALLENVERZEKERING,
) = range(37)

(
    LEAVE_ADV,
    LEAVE_ADV_AANVULLING_OUDEREN,
    LEAVE_ADV_AANVULLING_DUUR_DIENSTVERBAND,
    LEAVE_ADV_AANVULLING_ANDERS,
    LEAVE_VAKANTIE,
    LEAVE_BIJZONDER_VERLOF,
    LEAVE_WAZO_BETAALD_OUDERSCHAPSVERLOF,
    LEAVE_WAZO_ONBETAALD_OUDERSCHAPSVERLOF,
    LEAVE_WAZO_GEBOORTEVERLOF,
    LEAVE_WAZO_KORTDUREND_ZORGVERLOF,
    LEAVE_WAZO_LANGDUREND_ZORGVERLOF,
    LEAVE_WAZO_LANGE_VERLOFDUUR,
    LEAVE_WAZO_ANDERS,
    LEAVE_VERPLICHT,
    LEAVE_FEESTDAGEN,
    LEAVE_PERSOONLIJKE_FEESTDAGEN,
    LEAVE_WAARDE_VERLOFDAG,
) = range(17)

INDIVIDUAL_CHOICE_BUDGET = 0

(
    SUSTAINABLE_EMPLOYABILITY_OPLEIDINGEN,
    SUSTAINABLE_EMPLOYABILITY_LOOPBAANCOACHING,
    SUSTAINABLE_EMPLOYABILITY_OUTPLACEMENTTRAJECTEN,
    SUSTAINABLE_EMPLOYABILITY_VOORLICHTING_NEDERLAND,
    SUSTAINABLE_EMPLOYABILITY_SCHOLING_NEDERLAND,
    SUSTAINABLE_EMPLOYABILITY_SOCIALE_BEGELEIDING_NEDERLAND,
    SUSTAINABLE_EMPLOYABILITY_ANDERS,
    SUSTAINABLE_EMPLOYABILITY_FYSIEKE_GEZONDHEID,
    SUSTAINABLE_EMPLOYABILITY_MENTALE_GEZONDHEID,
    SUSTAINABLE_EMPLOYABILITY_FINANCIELE_GEZONDHEID,
    SUSTAINABLE_EMPLOYABILITY_VITALITEITSBUDGET,
    SUSTAINABLE_EMPLOYABILITY_VITALITEIT_ANDERS,
    SUSTAINABLE_EMPLOYABILITY_VERPLICHTE_SCHOLING,
    SUSTAINABLE_EMPLOYABILITY_DUURZAME_SAMENLEVING,
) = range(14)

OTHER_PAWW, OTHER_PAZW, OTHER_ANDERS, OTHER_RVU_REGELING, OTHER_WGA_HIAAT, OTHER_ACCIDENT_BENEFIT, OTHER_OVERIG_START = range(7)

(
    INDIVIDUAL_SALARY_INCREASE_RATE_DUUR_DIENSTVERBAND,
    INDIVIDUAL_SALARY_INCREASE_RATE_BEOORDELING_WERKNEMER,
    INDIVIDUAL_SALARY_INCREASE_RATE_ANDERS,
    INDIVIDUAL_SALARY_INCREASE_RATE_OVERIG,
) = range(4)

BELONING_VOORWAARDE_ANDERS = 0


# --- keuzelijsten (util.ts)
REFERENCE_DATE_OPTIONS = {
    "SeniorityDate": "Anciënniteitsdatum",
    "HireDate": "Datum indiensttreding",
    "ContractStartDate": "Startdatum contract",
    "AssignmentStartDate": "Startdatum plaatsing",
}
BASE_DEFINITION_OPTIONS = {
    "BaseWage": "Basisloon grondslag",
    "GrossSalary": "Bruto loon grondslag",
    "SocialInsuranceWage": "SVLoon grondslag",
    "HolidayAllowance": "Vakantiebijslag grondslag",
    "Pension": "Pensioen grondslag",
    "13thMonth": "13e maand grondslag",
    "UsualWage": "Gebruikelijk loon grondslag",
}


def base_def_2_label(code: str) -> str:
    return BASE_DEFINITION_OPTIONS.get(code, code)


def base_amount_unit_code_to_interval(unit_code: str | None) -> str | None:
    return {"DailyRate": "Day", "HourlyRate": "Hour", "MonthlyRate": "Month", "Fixed": "Once", "YearlyRate": "Year"}.get(
        unit_code or ""
    )


def work_duration_2_interval(werkduur: str) -> dict:
    return {
        "per-maand": {"value": 1, "unitCode": "Month"},
        "per-vier-weken": {"value": 4, "unitCode": "Week"},
        "per-week": {"value": 1, "unitCode": "Week"},
        "per-uur": {"value": 1, "unitCode": "Hour"},
    }[werkduur]


# --- slugs (addSlugPrefix)
def add_slug_prefix(prefix: str | Pad, achtervoegsel: str) -> str | Pad:
    if isinstance(prefix, str):
        return f"{prefix}/{achtervoegsel}"
    return [*prefix, achtervoegsel]


# --- Bedragregel (makeLineAmountQuestions / getLineAmountAnswer)
def get_line_amount_answer(a: Antwoorden, prefix: str | Pad) -> dict[str, Any]:
    """getLineAmountAnswer: de ingevulde Bedragregel als SETU-``line``."""
    p = lambda achter: add_slug_prefix(prefix, achter)  # noqa: E731
    soort = a.get(p("amount-type"))
    if soort == "vast-bedrag":
        return {
            "amount": {"value": to_float(a.get(p("vast-bedrag/bedrag"))), "unitCode": "Euro", "baseAmount": {"unitCode": "Fixed"}},
            "interval": {"value": 1, "unitCode": a.get(p("vast-bedrag/per"))},
        }
    if soort == "percentage":
        return {
            "amount": {
                "value": to_float(a.get(p("percentage/percentage"))),
                "unitCode": "Percentage",
                "baseAmount": {"unitCode": a.get(p("percentage/basis")), "baseType": a.get(p("percentage/grondslag"))},
            },
            "interval": {"value": 1, "unitCode": a.get(p("percentage/per"))},
        }
    if soort == "tijd":
        return {
            "amount": {"value": to_float(a.get(p("tijd/uur"))), "unitCode": "Hour", "baseAmount": {"unitCode": "Fixed"}},
            "interval": {"value": 1, "unitCode": a.get(p("tijd/per"))},
        }
    if soort == "n/a":
        return {}
    return {"conditions": []}


# --- gemak
def tekst(a: Antwoorden, slug: str | Pad, restrict_to: str | None = None) -> Any:
    return tekst_waarde(a.get(slug), restrict_to)


def keuze(a: Antwoorden, slug: str | Pad, setu_waarden: dict[str, Any] | None = None) -> Any:
    return keuze_waarde(a.get(slug), setu_waarden)
