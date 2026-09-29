"""08 · Loondoorbetaling bij ziekte (docs/formulier/08_loondoorbetaling-bij-ziekte.md)."""


from ._basis import FormulierModel, Keuze, veld
from .codes import Grondslag, JaNee, Loonbasis
from .voorwaarden import Als


class TijdvakZiekte(Keuze):
    """Tijdvak bij de percentageregels (deelverzameling van B2 Interval)."""

    UUR = "Hour", "Uur"
    DAG = "Day", "Dag"
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    JAAR = "Year", "Jaar"


class WachtdagcompensatieSoort(Keuze):
    VAST_BEDRAG = "vast-bedrag", "Vast bedrag"
    PERCENTAGE = "percentage", "Percentage van loon"


class LoondoorbetalingRegel(FormulierModel):
    """Eén variatie van het doorbetaalde percentage."""

    percentage: float | None = veld("loondoorbetaling-bij-ziekte[i]/percentage", "Percentage (%)", eenheid="%")
    van: Loonbasis | None = veld("loondoorbetaling-bij-ziekte[i]/percentage_bedrag", "Van:", vraagtype="keuzelijst")
    grondslag: Grondslag | None = veld("loondoorbetaling-bij-ziekte[i]/grondslag", "Grondslag:", optioneel=True, vraagtype="keuzelijst")
    per_tijdvak: TijdvakZiekte | None = veld("loondoorbetaling-bij-ziekte[i]/percentage_per_tijdvak", "Per", vraagtype="keuzelijst")
    voorwaarden: str | None = veld(
        "loondoorbetaling-bij-ziekte[i]/voorwaarden",
        "Voorwaarden (bijvoorbeeld: tijdens de eerste 3 dagen van de ziekte)",
    )


_WACHTDAGEN = Als("wachtdagen", JaNee.JA)
_COMPENSATIE_SOORT = "wachtdagcompensatie/amount-type"
_COMP_VAST = Als("compensatie_soort", WachtdagcompensatieSoort.VAST_BEDRAG)
_COMP_PCT = Als("compensatie_soort", WachtdagcompensatieSoort.PERCENTAGE)


class LoondoorbetalingBijZiekte(FormulierModel):
    # Hoe hoog is het percentage dat bij ziekte wordt doorbetaald?
    regels: list[LoondoorbetalingRegel] = veld(
        "loondoorbetaling-bij-ziekte[i]",
        "Hoe hoog is het percentage dat bij ziekte wordt doorbetaald? (variaties)",
        lijst=True,
    )

    # Wachtdagen
    wachtdagen: JaNee | None = veld("wachtdagen", "Zijn er wachtdagen?", vraagtype="radio")
    wachtdagen_aantal: int | None = veld("wachtdagen_ja_namelijk", "Ja, namelijk: … dagen", toon_als=_WACHTDAGEN, eenheid="dagen")

    # Voorwaarden wachtdagen
    wachtdagen_voorwaarden: JaNee | None = veld(
        "wachtdagen_voorwaarden", "Zitten er voorwaarden aan het toekennen van de wachtdagen?", toon_als=_WACHTDAGEN, vraagtype="radio"
    )
    wachtdagen_voorwaarden_namelijk: str | None = veld(
        "wachtdagen_voorwaarden_ja_namelijk", "Ja, namelijk:", toon_als=Als("wachtdagen_voorwaarden", JaNee.JA)
    )

    # Wachtdagcompensatie
    wachtdagcompensatie: JaNee | None = veld(
        "wachtdagcompensatie", "Geldt er een wachtdagcompensatie?", toon_als=_WACHTDAGEN, vraagtype="radio"
    )
    compensatie_soort: WachtdagcompensatieSoort | None = veld(
        _COMPENSATIE_SOORT, "Hoe wordt de wachtdagcompensatie uitgekeerd?", toon_als=Als("wachtdagcompensatie", JaNee.JA), vraagtype="radio"
    )
    compensatie_bedrag: float | None = veld(
        "wachtdagcompensatie/amount-type/vast-bedrag/bedrag", "Bedrag (€)", toon_als=_COMP_VAST, eenheid="€"
    )
    compensatie_percentage: float | None = veld(
        "wachtdagcompensatie/amount-type/percentage/percentage",
        "Percentage (%)",
        toon_als=_COMP_PCT, eenheid="%",
    )
    compensatie_basis: Loonbasis | None = veld(
        "wachtdagcompensatie/amount-type/percentage/basis", "van", toon_als=_COMP_PCT, vraagtype="keuzelijst"
    )
