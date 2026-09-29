"""15 · Grondslagen (docs/formulier/15_grondslagen.md).

Dynamische sectie: één set vragen per grondslag die elders in het formulier gekozen is.
De antwoorden staan in de webform onder de grondslagcode (``grondslag/<code>/...``).
"""

import datetime as dt

from ._basis import FormulierModel, Keuze, veld
from .codes import Grondslag
from .s04_toeslagen import ToeslagSoort
from .voorwaarden import Als


class ToeslagenMeegenomen(Keuze):
    ALLE = "all", "Alle toeslagen"
    GEEN = "none", "Geen toeslagen"
    SOMMIGE = "some", "Sommige toeslagen:"


class GrondslagInstelling(FormulierModel):
    salaris: bool | None = veld("grondslag/<code>/salaris", "Salaris wordt meegenomen bij deze grondslag")
    vakantietoeslag: bool | None = veld(
        "grondslag/<code>/vakantietoeslag", "Vakantietoeslag wordt meegenomen bij deze grondslag"
    )
    betaald_verlof: bool | None = veld(
        "grondslag/<code>/betaald-verlof", "Betaald verlof wordt meegenomen bij deze grondslag"
    )
    toeslagen: ToeslagenMeegenomen | None = veld(
        "grondslag/<code>/toeslagen", "Worden toeslagen meegenomen bij deze grondslag?", vraagtype="radio"
    )
    toeslag: dict[ToeslagSoort, bool] = veld(
        "grondslag/<code>/toeslag-<toeslag-slug>",
        "Eén checkbox per toeslagsoort",
        toon_als=Als("toeslagen", ToeslagenMeegenomen.SOMMIGE),
        mapping=True,
    )
    peildatum: dt.date | None = veld("grondslag/<code>/peildatum", "Peildatum voor deze grondslag", optioneel=True)


class Grondslagen(FormulierModel):
    per_grondslag: dict[Grondslag, GrondslagInstelling] = veld(
        "grondslag/<code>", "Instellingen per gebruikte grondslag", mapping=True
    )
