"""13 · Aanvullende regelingen (docs/formulier/13_aanvullende-regelingen.md).

De vijf vaste regelingen komen uit ``makeAanvullendeRegelingenRows``; ``<r>`` in de slugs van
``AanvullendeRegeling`` is de slug van de regeling (bijv. ``aanvullende-sociale-zekerheidsregelingen/paww``).
"""

from typing import Any

from pydantic import field_validator

from ._basis import FormulierModel, veld
from .bouwstenen import BedragSoort, Bedragregel
from .codes import JaNee
from .voorwaarden import Als

_JA = Als("ja_nee", JaNee.JA)


class AanvullendeRegeling(FormulierModel):
    """Vaste regeling zonder dekkingswaarde (RVU regeling)."""

    ja_nee: JaNee | None = veld("<r>", "(vraagtekst verschilt per regeling)", vraagtype="radio")
    omschrijving: str | None = veld("<r>/omschrijving", "Omschrijf de inhoud van de regeling", toon_als=_JA)
    werkgeverspremie: Bedragregel | None = veld(
        "<r>/werkgeverspremie/…",
        "Wat is de werkgeverspremie?",
        toon_als=_JA, opties=[BedragSoort.VAST_BEDRAG, BedragSoort.PERCENTAGE, BedragSoort.NVT],
    )
    werknemerspremie: Bedragregel | None = veld(
        "<r>/werknemerspremie/…",
        "Wat is de werknemerspremie?",
        toon_als=_JA, opties=[BedragSoort.VAST_BEDRAG, BedragSoort.PERCENTAGE, BedragSoort.NVT],
    )


class AanvullendeRegelingMetDekking(AanvullendeRegeling):
    """Vaste regeling met dekkingswaarde (PAWW, PAZW, WGA-Hiaat, Ongevallenverzekering)."""

    dekkingswaarde: Bedragregel | None = veld(
        "<r>/dekkingswaarde/…",
        "Wat is de dekkingswaarde?",
        toon_als=_JA,
        optioneel=True, opties=[BedragSoort.VAST_BEDRAG, BedragSoort.PERCENTAGE, BedragSoort.TIJD], zonder_per=True,
    )


_ANDERE_PREMIE_SOORTEN = [BedragSoort.VAST_BEDRAG, BedragSoort.PERCENTAGE, BedragSoort.TIJD]


class AndereSocialeRegeling(FormulierModel):
    """Eén rij ``andere-sociale-regelingen[i]``.

    De premies staan in de webform onder een extra lijstniveau (``…/werkgeverspremie[0]/amount-type``); de
    webform gebruikt alleen positie 0. Daarom zijn het hier lijsten van hooguit één Bedragregel. Je mag ook
    gewoon één ``Bedragregel`` toewijzen; die wordt dan in een lijst gezet.
    """

    omschrijving: str | None = veld(
        "andere-sociale-regelingen[i]/omschrijving", "Omschrijf de inhoud van de regeling"
    )
    werkgeverspremie: list[Bedragregel] = veld(
        "andere-sociale-regelingen[i]/werkgeverspremie[j]/…",
        "Wat is de werkgeverspremie? (alleen positie 0)",
        lijst=True, max_length=1,
    )
    werknemerspremie: list[Bedragregel] = veld(
        "andere-sociale-regelingen[i]/werknemerspremie[j]/…",
        "Wat is de werknemerspremie? (alleen positie 0)",
        lijst=True, max_length=1,
    )

    @field_validator("werkgeverspremie", "werknemerspremie", mode="before")
    @classmethod
    def _een_bedragregel(cls, waarde: Any) -> Any:
        if waarde is None:
            return []
        return [waarde] if isinstance(waarde, (Bedragregel, dict)) else waarde

    @field_validator("werkgeverspremie", "werknemerspremie")
    @classmethod
    def _soort_toegestaan(cls, waarde: list[Bedragregel]) -> list[Bedragregel]:
        # Standaard-Bedragregel: vast bedrag, percentage of tijd (geen N.v.t.).
        for regel in waarde:
            if regel.soort is not None and regel.soort not in _ANDERE_PREMIE_SOORTEN:
                raise ValueError(
                    f"optie '{regel.soort}' is niet toegestaan bij deze vraag "
                    f"(toegestaan: {', '.join(_ANDERE_PREMIE_SOORTEN)})"
                )
        return waarde


class AanvullendeRegelingen(FormulierModel):
    # PAWW
    paww: AanvullendeRegelingMetDekking | None = veld(
        "aanvullende-sociale-zekerheidsregelingen/paww",
        "Kent jouw onderneming een PAWW (private aanvulling WW) regeling?",
    )

    # PAZW
    pazw: AanvullendeRegelingMetDekking | None = veld(
        "aanvullende-sociale-zekerheidsregelingen/pazw",
        "Kent jouw onderneming een PAZW (private aanvulling Ziektewet) regeling?",
    )

    # RVU regeling
    rvu_regeling: AanvullendeRegeling | None = veld(
        "aanvullende-sociale-zekerheidsregelingen/rvu-regeling",
        "Kent jouw onderneming een RVU regeling, een generatiepact of regeling om minder te gaan werken "
        "richting het pensioen?",
    )

    # WGA-Hiaat
    wga_hiaat: AanvullendeRegelingMetDekking | None = veld(
        "aanvullende-sociale-zekerheidsregelingen/wga-hiaat", "Kent jouw onderneming een WGA-Hiaat regeling?"
    )

    # Ongevallenverzekering
    ongevallenverzekering: AanvullendeRegelingMetDekking | None = veld(
        "aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering",
        "Kent jouw onderneming een ongevallenverzekering?",
    )

    # Anders: andere aanvullende sociale zekerheidsregelingen
    andere_ja_nee: JaNee | None = veld(
        "andere-sociale-regelingen/ja-nee", "Kent jouw onderneming andere aanvullende sociale zekerheidsregeling?", vraagtype="radio"
    )
    andere_regelingen: list[AndereSocialeRegeling] = veld(
        "andere-sociale-regelingen[i]",
        "Andere aanvullende sociale zekerheidsregelingen (rijen hebben geen showIf; "
        "knop 'Regeling toevoegen' alleen bij ja)",
        lijst=True,
    )
