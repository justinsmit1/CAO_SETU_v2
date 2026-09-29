"""Gedeelde bouwstenen (docs/formulier/00_bouwstenen.md).

De slugs zijn relatief ten opzichte van het prefix ``<p>`` waarmee de Bedragregel wordt aangeroepen.
"""

from ._basis import FormulierModel, Keuze, veld
from .codes import Grondslag, Interval, Loonbasis
from .voorwaarden import Als


class BedragSoort(Keuze):
    VAST_BEDRAG = "vast-bedrag", "Vast bedrag"
    PERCENTAGE = "percentage", "Percentage van loon"
    TIJD = "tijd", "In tijd"
    NVT = "n/a", "N.v.t."


class VastBedrag(FormulierModel):
    bedrag: float | None = veld("<p>/vast-bedrag/bedrag", "Bedrag", eenheid="€")
    per: Interval | None = veld("<p>/vast-bedrag/per", "per", vraagtype="keuzelijst")


class Percentage(FormulierModel):
    percentage: float | None = veld("<p>/percentage/percentage", "Percentage", eenheid="%")
    basis: Loonbasis | None = veld("<p>/percentage/basis", "van", vraagtype="keuzelijst")
    per: Interval | None = veld("<p>/percentage/per", "per", vraagtype="keuzelijst")
    grondslag: Grondslag | None = veld(
        "<p>/percentage/grondslag", "grondslag", vraagtype="keuzelijst", optioneel=True
    )


class Tijd(FormulierModel):
    uur: float | None = veld("<p>/tijd/uur", "Aantal", eenheid="uur")
    per: Interval | None = veld("<p>/tijd/per", "per", vraagtype="keuzelijst")


class Bedragregel(FormulierModel):
    """B1 · Bedragregel (makeLineAmountQuestions).

    Alleen het deel dat hoort bij ``soort`` is zichtbaar in de webform; de andere delen moeten leeg blijven
    (afgedwongen via ``toon_als``).
    Welke soorten een vraag toestaat verschilt per aanroep: dat staat als ``opties`` op het veld dat
    de Bedragregel gebruikt, en wordt daar gecontroleerd.
    """

    soort: BedragSoort | None = veld("<p>/amount-type", "(vraagtekst verschilt per aanroep)", vraagtype="radio")
    vast_bedrag: VastBedrag | None = veld("<p>/vast-bedrag", "Vast bedrag", toon_als=Als("soort", BedragSoort.VAST_BEDRAG))
    percentage: Percentage | None = veld("<p>/percentage", "Percentage van loon", toon_als=Als("soort", BedragSoort.PERCENTAGE))
    tijd: Tijd | None = veld("<p>/tijd", "In tijd", toon_als=Als("soort", BedragSoort.TIJD))

    def per(self) -> Interval | None:
        """Het ingevulde "per" van het gekozen deel (None bij n.v.t. of leeg)."""
        deel = {"vast-bedrag": self.vast_bedrag, "percentage": self.percentage, "tijd": self.tijd}.get(
            self.soort or ""
        )
        return deel.per if deel else None
