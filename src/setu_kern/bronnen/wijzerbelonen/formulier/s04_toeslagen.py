"""04 · Toeslagen (docs/formulier/04_toeslagen.md).

De sectie begint met een checkbox per toeslagsoort (``makeToeslagRows``). Voor elke aangevinkte soort volgt een
dynamische subsectie met één of meer variaties (``<toeslag>[i]``), elk met eventueel toepassingsperiodes
(``<toeslag>[i]/toepassingsperiodes[j]``). ``<toeslag>`` is de slug uit ``ToeslagSoort``.
"""

import datetime as dt

from ._basis import FormulierModel, Keuze, veld
from .bouwstenen import BedragSoort, Bedragregel
from .codes import JaNee
from .voorwaarden import Als


class ToeslagSoort(Keuze):
    """De 9 toeslagsoorten (``makeToeslagRows``); ook gebruikt in 15 Grondslagen."""

    ONREGELMATIGHEIDSTOESLAGEN = "onregelmatigheids-toeslagen", "Onregelmatigheidstoeslagen (waaronder feestdagen)"
    PLOEGENTOESLAGEN = "ploegentoeslagen", "Ploegentoeslagen"
    VERSCHOVEN_DIENSTEN = "toeslagen-verschoven-diensten", "Toeslagen voor verschoven diensten"
    FYSIEKE_BELASTING = "toeslagen-fysieke-belasting", "Toeslagen voor (fysieke) belasting"
    STAND_BY = "toeslagen-stand-by-consignatie-bereikbaarheidsdiensten", "Toeslagen voor werken tijdens stand-by-, consignatie- of bereikbaarheidsdiensten"
    OVERWERK = "overwerktoeslag", "Overwerk"
    WAARNEMINGSTOESLAG = "waarnemingstoeslag", "Waarnemingstoeslag"
    PERFORMANCETOESLAG = "performancetoeslag", "Performancetoeslag"
    ANDERS = "anders", "Anders"


class Cumulatief(Keuze):
    JA_CUMULATIEF = "ja-cumulative", "Ja, toeslagen worden opgeteld"
    JA_COMPOUNDING = "ja-compounding", "Ja, deze toeslag wordt berekend over het resultaat na andere toeslagen, namelijk:"
    NEE = "nee", "Nee"


class ToepassingsperiodesType(Keuze):
    ALTIJD = "altijd", "Altijd"
    BEPAALD = "bepaald", "Bepaalde data/tijden/dagen"


_PERIODE = Als("toepassingsperiodes_type", ToepassingsperiodesType.BEPAALD)
_PERIODE_RIJ = Als("../toepassingsperiodes_type", ToepassingsperiodesType.BEPAALD)  # vanuit een toepassingsperiode
# niet controleerbaar: _BLOK_PERIODES en _BLOK_AFBOUW hangen af van de toeslagsoort (in welke lijst de variatie staat)
_BLOK_PERIODES = (
    "alleen bij onregelmatigheids-toeslagen, toeslagen-verschoven-diensten, "
    "toeslagen-stand-by-consignatie-bereikbaarheidsdiensten, overwerktoeslag en anders"
)
_BLOK_AFBOUW = "alleen bij ploegentoeslagen, waarnemingstoeslag, performancetoeslag en anders"


class Toepassingsperiode(FormulierModel):
    """Toepassingsperiode {num} (``<toeslag>[i]/toepassingsperiodes[j]``)."""

    # Datumbereik
    startdatum: dt.date | None = veld(
        "<toeslag>[i]/toepassingsperiodes[j]/startdatum",
        "Startdatum",
        toon_als=f"{_PERIODE_RIJ} en alleen bij anders",  # niet controleerbaar: hangt af van de toeslagsoort
        optioneel=True,
    )
    einddatum: dt.date | None = veld(
        "<toeslag>[i]/toepassingsperiodes[j]/einddatum",
        "Einddatum",
        toon_als=f"{_PERIODE_RIJ} en alleen bij anders",  # niet controleerbaar: hangt af van de toeslagsoort
        optioneel=True,
    )

    # Tijdsbestek: Op welke tijden is de toeslag van toepassing?
    starttijd: dt.time | None = veld(
        "<toeslag>[i]/toepassingsperiodes[j]/starttijd", "Starttijd", toon_als=_PERIODE_RIJ, optioneel=True
    )
    eindtijd: dt.time | None = veld(
        "<toeslag>[i]/toepassingsperiodes[j]/eindtijd", "Eindtijd", toon_als=_PERIODE_RIJ, optioneel=True
    )

    # Weekdagen (optioneel)
    maandag: bool | None = veld("<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Monday", "Maandag", toon_als=_PERIODE_RIJ)
    dinsdag: bool | None = veld("<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Tuesday", "Dinsdag", toon_als=_PERIODE_RIJ)
    woensdag: bool | None = veld(
        "<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Wednesday", "Woensdag", toon_als=_PERIODE_RIJ
    )
    donderdag: bool | None = veld(
        "<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Thursday", "Donderdag", toon_als=_PERIODE_RIJ
    )
    vrijdag: bool | None = veld("<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Friday", "Vrijdag", toon_als=_PERIODE_RIJ)
    zaterdag: bool | None = veld(
        "<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Saturday", "Zaterdag", toon_als=_PERIODE_RIJ
    )
    zondag: bool | None = veld("<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Sunday", "Zondag", toon_als=_PERIODE_RIJ)


class ToeslagVariatie(FormulierModel):
    """Eén variatie van een toeslag (``<toeslag>[i]``)."""

    # Variatie
    naam: str | None = veld("<toeslag>[i]/name", "Titel", toon_als="alleen bij anders")  # niet controleerbaar: hangt af van de toeslagsoort
    omschrijving: str | None = veld(
        "<toeslag>[i]/description", "Omschrijving van deze variatie", toon_als="meer dan 1 variatie", optioneel=True  # niet controleerbaar: hangt af van het aantal rijen
    )
    bedrag: Bedragregel | None = veld(
        "<toeslag>[i]/…", "Hoe wordt de toeslag uitgekeerd?", opties=[BedragSoort.VAST_BEDRAG, BedragSoort.PERCENTAGE, BedragSoort.TIJD]
    )
    voorwaarden: str | None = veld(
        "<toeslag>[i]/voorwaarden",
        "Onder welke voorwaarden geldt de toeslag? Of wanneer is er sprake van deze toeslag? "
        "(bij ploegentoeslagen: Geef een omschrijving van de ploegendienst, zoals het rooster)",
        optioneel=True,
    )
    cumulatief: Cumulatief | None = veld("<toeslag>[i]/cumulatief", "Is deze toeslag cumulatief?", vraagtype="radio")
    cumulatief_toelichting: str | None = veld(
        "<toeslag>[i]/cumulatief/ja-cumulative/namelijk",
        "Toelichting",
        toon_als=Als("cumulatief", Cumulatief.JA_CUMULATIEF),
        optioneel=True,
    )
    compounding: dict[ToeslagSoort, bool] = veld(
        "<toeslag>[i]/compounding/<andere-toeslag>",
        "Eén checkbox per andere aangevinkte toeslag (label = label van die toeslag)",
        toon_als=Als("cumulatief", Cumulatief.JA_COMPOUNDING),
        mapping=True,
    )

    # Toepassingsperiodes
    toepassingsperiodes_type: ToepassingsperiodesType | None = veld(
        "<toeslag>[i]/toepassingsperiodes-type",
        "Wanneer is de toeslag geldig? (Toepassingsperiodes)",
        toon_als=_BLOK_PERIODES, vraagtype="radio",  # niet controleerbaar: zie _BLOK_PERIODES
    )
    toepassingsperiodes: list[Toepassingsperiode] = veld(
        "<toeslag>[i]/toepassingsperiodes[j]", "Toepassingsperiode {num}", toon_als=_PERIODE, lijst=True
    )

    # Afbouwregeling
    afbouwregeling: JaNee | None = veld(
        "<toeslag>[i]/afbouwregeling", "Geldt er een afbouwregeling voor deze toeslag?", toon_als=_BLOK_AFBOUW, vraagtype="radio"  # niet controleerbaar: zie _BLOK_AFBOUW
    )
    afbouwregeling_namelijk: str | None = veld(
        "<toeslag>[i]/afbouwregeling/ja-namelijk",
        "Ja, namelijk (geen vraagtekst)",
        toon_als=Als("afbouwregeling", JaNee.JA),
    )


class Toeslagen(FormulierModel):
    # Toeslagen · Welke toeslagen kent jouw organisatie?
    onregelmatigheids_toeslagen_aan: bool | None = veld(
        "onregelmatigheids-toeslagen/enabled", "Onregelmatigheids- toeslagen (waaronder feestdagen)"
    )
    ploegentoeslagen_aan: bool | None = veld("ploegentoeslagen/enabled", "Ploegentoeslagen")
    toeslagen_verschoven_diensten_aan: bool | None = veld(
        "toeslagen-verschoven-diensten/enabled", "Toeslagen voor verschoven diensten"
    )
    toeslagen_fysieke_belasting_aan: bool | None = veld(
        "toeslagen-fysieke-belasting/enabled", "Toeslagen voor (fysieke) belasting"
    )
    toeslagen_stand_by_aan: bool | None = veld(
        "toeslagen-stand-by-consignatie-bereikbaarheidsdiensten/enabled",
        "Toeslagen voor werken tijdens stand-by-, consignatie- of bereik- baarheidsdiensten",
    )
    overwerktoeslag_aan: bool | None = veld("overwerktoeslag/enabled", "Overwerk")
    waarnemingstoeslag_aan: bool | None = veld("waarnemingstoeslag/enabled", "Waarnemingstoeslag")
    performancetoeslag_aan: bool | None = veld("performancetoeslag/enabled", "Performancetoeslag")
    anders_aan: bool | None = veld("anders/enabled", "Anders")
    geen_toeslagen: bool | None = veld("geen-toeslagen", "Geen toeslagen")

    # <Toeslag> · variaties per aangevinkte toeslagsoort
    onregelmatigheids_toeslagen: list[ToeslagVariatie] = veld(
        "onregelmatigheids-toeslagen[i]",
        "Onregelmatigheids- toeslagen (waaronder feestdagen): variaties",
        toon_als=Als("onregelmatigheids_toeslagen_aan"),
        lijst=True,
    )
    ploegentoeslagen: list[ToeslagVariatie] = veld(
        "ploegentoeslagen[i]",
        "Ploegentoeslagen: variaties",
        toon_als=Als("ploegentoeslagen_aan"),
        lijst=True,
    )
    toeslagen_verschoven_diensten: list[ToeslagVariatie] = veld(
        "toeslagen-verschoven-diensten[i]",
        "Toeslagen voor verschoven diensten: variaties",
        toon_als=Als("toeslagen_verschoven_diensten_aan"),
        lijst=True,
    )
    toeslagen_fysieke_belasting: list[ToeslagVariatie] = veld(
        "toeslagen-fysieke-belasting[i]",
        "Toeslagen voor (fysieke) belasting: variaties",
        toon_als=Als("toeslagen_fysieke_belasting_aan"),
        lijst=True,
    )
    toeslagen_stand_by: list[ToeslagVariatie] = veld(
        "toeslagen-stand-by-consignatie-bereikbaarheidsdiensten[i]",
        "Toeslagen voor werken tijdens stand-by-, consignatie- of bereikbaarheidsdiensten: variaties",
        toon_als=Als("toeslagen_stand_by_aan"),
        lijst=True,
    )
    overwerktoeslag: list[ToeslagVariatie] = veld(
        "overwerktoeslag[i]",
        "Overwerk: variaties",
        toon_als=Als("overwerktoeslag_aan"),
        lijst=True,
    )
    waarnemingstoeslag: list[ToeslagVariatie] = veld(
        "waarnemingstoeslag[i]",
        "Waarnemingstoeslag: variaties",
        toon_als=Als("waarnemingstoeslag_aan"),
        lijst=True,
    )
    performancetoeslag: list[ToeslagVariatie] = veld(
        "performancetoeslag[i]",
        "Performancetoeslag: variaties",
        toon_als=Als("performancetoeslag_aan"),
        lijst=True,
    )
    anders: list[ToeslagVariatie] = veld(
        "anders[i]",
        "Anders: variaties",
        toon_als=Als("anders_aan"),
        lijst=True,
    )
