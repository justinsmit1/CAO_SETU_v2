"""14 · Overig (docs/formulier/14_overig.md)."""

from ._basis import FormulierModel, veld
from .bouwstenen import BedragSoort, Bedragregel
from .codes import JaNee
from .voorwaarden import Als

_JA = Als("../ja_nee", JaNee.JA)


class OverigeRegeling(FormulierModel):
    naam: str | None = veld("overige-regelingen[i]/naam", "Naam", toon_als=_JA)
    voorwaarden: str | None = veld("overige-regelingen[i]/voorwaarden", "Voorwaarden", toon_als=_JA, optioneel=True)
    waarde: Bedragregel | None = veld(
        "overige-regelingen[i]/…",
        "Hoe wordt de waarde uitgekeerd?",
        toon_als=_JA, opties=[BedragSoort.VAST_BEDRAG, BedragSoort.PERCENTAGE, BedragSoort.TIJD],
    )


class Overig(FormulierModel):
    ja_nee: JaNee | None = veld(
        "overige-regelingen-ja-nee", "Zijn er overige regelingen of arbeidsvoorwaarden van toepassing?", vraagtype="radio"
    )

    # Overige regelingen
    overige_regelingen: list[OverigeRegeling] = veld(
        "overige-regelingen[i]", "Overige regelingen", toon_als=Als("ja_nee", JaNee.JA), lijst=True
    )
