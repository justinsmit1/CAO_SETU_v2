"""Keuzelijsten uit het SETU-schema (Inquiry Pay Equity v2.0). Waarden exact zoals in het schema."""

from enum import StrEnum


class IntervalCode(StrEnum):
    DAY = "Day"
    DAY_PART = "DayPart"
    HOUR = "Hour"
    ITEM = "Item"
    KILOMETER = "Kilometer"
    MONTH = "Month"
    NIGHT = "Night"
    ONCE = "Once"
    ON_EXPENSE_BASIS = "OnExpenseBasis"
    QUARTER = "Quarter"
    RELOCATION = "Relocation"
    ROUTE = "Route"
    SHIFT = "Shift"
    TRIP = "Trip"
    WEEK = "Week"
    WEEKLY_TRAVEL_DAY = "WeeklyTravelDay"
    WORKED_DAY = "WorkedDay"
    WORK_FROM_HOME_DAY = "WorkFromHomeDay"
    YEAR = "Year"


class AmountUnitCode(StrEnum):
    HOUR = "Hour"
    PERCENTAGE = "Percentage"
    EURO = "Euro"
    SALARY_STEP = "SalaryStep"
    DAY = "Day"


class BaseUnitCode(StrEnum):
    HOURLY_RATE = "HourlyRate"
    DAILY_RATE = "DailyRate"
    FOUR_WEEKLY_RATE = "FourWeeklyRate"
    MONTHLY_RATE = "MonthlyRate"
    YEARLY_RATE = "YearlyRate"
    EXPENSE = "Expense"
    FIXED = "Fixed"


class BaseDefinitionCode(StrEnum):
    GROSS_SALARY = "GrossSalary"
    USUAL_WAGE = "UsualWage"
    BASE_WAGE = "BaseWage"
    SOCIAL_INSURANCE_WAGE = "SocialInsuranceWage"
    HOLIDAY_ALLOWANCE = "HolidayAllowance"
    PENSION = "Pension"
    SICK_PAY = "SickPay"
    THIRTEENTH_MONTH = "13thMonth"


class Operator(StrEnum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"


class ContributionSource(StrEnum):
    EMPLOYEE = "Employee"
    EMPLOYER = "Employer"


class SchemeAgencyId(StrEnum):
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"


class LegalSchemeAgencyId(StrEnum):
    KVK = "KvK"
    OIN = "OIN"
    RSIN = "RSIN"


class OriginType(StrEnum):
    """LabourAgreementReference.type"""

    COLLECTIVE_LABOUR_AGREEMENT = "CollectiveLabourAgreement"
    COLLECTIVE_LABOUR_AGREEMENT_EXTENDED = "CollectiveLabourAgreementExtended"
    CUSTOM_LABOUR_AGREEMENT = "CustomLabourAgreement"
    UNKNOWN = "Unknown"


class SupplementaryArrangementCode(StrEnum):
    ERA = "ERA"
    GENERATIONPACT = "Generationpact"
    ACCIDENT_BENEFIT = "AccidentBenefit"
    PAWW = "PAWW"
    PAZW = "PAZW"
    RVU = "RVU"
    WGA = "WGA"


class SustainabilityCode(StrEnum):
    ARRANGEMENT_FOR_FINANCIAL_HEALTH = "ArrangementForFinancialHealth"
    ARRANGEMENT_FOR_HEALTH = "ArrangementForHealth"
    ARRANGEMENT_FOR_MENTAL_HEALTH = "ArrangementForMentalHealth"
    CAREER_COACHING = "CareerCoaching"
    EDUCATION = "Education"
    INFORMATION_PROVISION = "InformationProvision"
    OTHER = "Other"
    OUTPLACEMENT_PROGRAMS = "OutplacementPrograms"
    SOCIAL_SUPPORT = "SocialSupport"
    SUSTAINABLE_SOCIETY = "SustainableSociety"
    VITALITY_BUDGET = "VitalityBudget"


class IntervalHourDayUnitCode(StrEnum):
    DAY = "Day"
    HOUR = "Hour"


class ReferenceDateType(StrEnum):
    """EmploymentDurationCondition.referenceDateType"""

    SENIORITY_DATE = "SeniorityDate"
    HIRE_DATE = "HireDate"
    CONTRACT_START_DATE = "ContractStartDate"
    ASSIGNMENT_START_DATE = "AssignmentStartDate"


class RelativeEvent(StrEnum):
    """Relative.event"""

    HIRE_DATE = "HireDate"
    CONTRACT_START = "ContractStart"
    CONTRACT_END = "ContractEnd"
    SENIORITY_START = "SeniorityStart"
    BIRTH_DATE = "BirthDate"
    EVALUATION_DATE = "EvaluationDate"
    SALARY_PERIOD_START = "SalaryPeriodStart"
    SALARY_PERIOD_END = "SalaryPeriodEnd"
    SICK_LEAVE = "SickLeave"
    OTHER_EVENT = "OtherEvent"


class IkbRelationType(StrEnum):
    INCLUDED = "Included"
    ON_TOP = "OnTop"
    NONE = "None"


class AllowanceRelationType(StrEnum):
    """AllowanceReferenceExtended.relationType"""

    COMPOUNDING = "Compounding"
    CUMULATIVE = "Cumulative"
    SUBTRACTIVE = "Subtractive"


class EmailUseCode(StrEnum):
    BUSINESS = "Business"
    PRIVATE = "Private"


class Weekday(StrEnum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    HOLIDAY = "Holiday"


AllowanceCode = StrEnum(
    "AllowanceCode",
    {
        c: c
        for c in (
            "EA100 EA101 EA102 EA103 EA105 EA107 EA108 EA109 EA110 EA111 EA112 EA113 EA201 EA202 EA203 EA204 "
            "EA300 EA301 EA302 EA600 EA602 EA603 EA604 EA605 EA606 EA607 EA608 EA609 EA610 EA801 EA802 EA803 "
            "EA903 EA910 HT100 HT101 HT102 HT200 HT201 HT202 HT210 HT211 HT300 HT301 HT302 HT310 HT311 HT320 "
            "HT321 HT322 HT330 HT331 HT340 HT400 HT500 HT501 HT600 HT601 HT602 HT700 HT701 HT702 HT703 HT800"
        ).split()
    },
    module=__name__,
)
"""Toeslag-/vergoedingscodes (64), bijv. ``AllowanceCode.EA103`` (reiskosten per km), ``AllowanceCode.HT320``."""
