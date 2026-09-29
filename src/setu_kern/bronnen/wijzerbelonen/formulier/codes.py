"""Gedeelde keuzelijsten van het webformulier (docs/formulier/00_bouwstenen.md, B2–B6).

De enum-waarden zijn exact de waarden die de webform opslaat; het tweede element is het label in de tool.
"""

from ._basis import Keuze


class JaNee(Keuze):
    """B6 · Ja / Nee."""

    JA = "ja", "Ja"
    NEE = "nee", "Nee"


class Interval(Keuze):
    """B2 · Interval "per" (intervalCodeOptions)."""

    UUR = "Hour", "Uur"
    DAG = "Day", "Dag"
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    KWARTAAL = "Quarter", "Kwartaal"
    JAAR = "Year", "Jaar"
    DAGDEEL = "DayPart", "Dagdeel"
    DIENST = "Shift", "Dienst"
    EENMALIG = "Once", "Eenmalig"
    GEWERKTE_DAG = "WorkedDay", "Gewerkte dag"
    ITEM = "Item", "Item"
    KILOMETER = "Kilometer", "Kilometer"
    NACHT = "Night", "Nacht"
    OP_DECLARATIEBASIS = "OnExpenseBasis", "Op declaratie basis"
    RIT = "Trip", "Rit"
    ROUTE = "Route", "Route"
    THUISWERKDAG = "WorkFromHomeDay", "Thuiswerkdag"
    VERHUIZING = "Relocation", "Verhuizing"
    WEKELIJKSE_REISDAG = "WeeklyTravelDay", "Wekelijkse reisdag"


class Loonbasis(Keuze):
    """B3 · Loonbasis "van" (baseUnitOptions)."""

    UURLOON = "HourlyRate", "Uurloon"
    DAGLOON = "DailyRate", "Dagloon"
    VIERWEKENLOON = "FourWeeklyRate", "4-weken loon"
    MAANDLOON = "MonthlyRate", "Maandloon"
    JAARLOON = "YearlyRate", "Jaarloon"


class Grondslag(Keuze):
    """B4 · Grondslag (baseDefinitionOptions)."""

    BASISLOON = "BaseWage", "Basisloon grondslag"
    BRUTO_LOON = "GrossSalary", "Bruto loon grondslag"
    SV_LOON = "SocialInsuranceWage", "SVLoon grondslag"
    VAKANTIEBIJSLAG = "HolidayAllowance", "Vakantiebijslag grondslag"
    PENSIOEN = "Pension", "Pensioen grondslag"
    DERTIENDE_MAAND = "13thMonth", "13e maand grondslag"
    GEBRUIKELIJK_LOON = "UsualWage", "Gebruikelijk loon grondslag"


class Peildatum(Keuze):
    """B5 · Peildatum / referentiedatum (referenceDateOptions)."""

    ANCIENNITEITSDATUM = "SeniorityDate", "Anciënniteitsdatum"
    DATUM_INDIENSTTREDING = "HireDate", "Datum indiensttreding"
    STARTDATUM_CONTRACT = "ContractStartDate", "Startdatum contract"
    STARTDATUM_PLAATSING = "AssignmentStartDate", "Startdatum plaatsing"


ANDERS_NAMELIJK = "anders"
"""B7 · waarde van de optie "Anders, namelijk"."""
