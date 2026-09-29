"""11 · Pensioen (docs/formulier/11_pensioen.md)."""

from ._basis import FormulierModel, veld
from .codes import JaNee
from .voorwaarden import Als

_PENSIOEN = Als("van_toepassing", JaNee.JA)


class Pensioen(FormulierModel):
    # Pensioen
    van_toepassing: JaNee | None = veld("pensioenregeling/van-toepassing", "Ken je een pensioenregeling?", vraagtype="radio")

    # Pensioenfonds
    pensioenfonds_naam: str | None = veld(
        "pensioenregeling/pensioenfonds/naam", "Wat is de naam van het pensioenfonds?", toon_als=_PENSIOEN
    )

    # Wat is de hoogte van de werkgeverspremie?
    werkgeverspremie_percentage: float | None = veld(
        "pensioenregeling/werkgeverspremie/percentage",
        "Wat is de hoogte van de werkgeverspremie? … % van de pensioengrondslag",
        toon_als=_PENSIOEN, eenheid="%",
    )

    # Hanteer je een franchise?
    franchise: JaNee | None = veld(
        "pensioenregeling/franchise/van-toepassing", "Hanteer je een franchise? (Ja, namelijk: / Nee)", toon_als=_PENSIOEN, vraagtype="radio"
    )
    franchise_namelijk: str | None = veld(
        "pensioenregeling/franchise/namelijk",
        "Geef een beschrijving van de franchise",
        toon_als=Als("franchise", JaNee.JA),
    )
