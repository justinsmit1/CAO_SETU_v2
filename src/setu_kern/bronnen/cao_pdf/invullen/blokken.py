"""De indeling in LLM-aanroepen: per blok één aanroep.

Een blok is een sectie van het Formulier, of een deel ervan (``velden``: velden op het hoogste niveau van de
sectie). Grote secties (04, 06, 12, 13) worden later per blok gesplitst; hun schema is anders te groot.

Nu ondersteund: 05 Vakantiebijslag. Nieuwe blokken voeg je toe aan ``BLOKKEN``; secties zonder blok staan in het
rapport als "nog niet ondersteund".
"""

from dataclasses import dataclass

from pydantic import BaseModel

from ...wijzerbelonen.formulier import Formulier


@dataclass(frozen=True)
class Blok:
    naam: str  # voor het rapport, bijv. "05 Vakantiebijslag"
    sectie: str  # attribuut van Formulier, bijv. "vakantiebijslag"
    velden: tuple[str, ...] | None = None  # None = de hele sectie
    zoektermen: tuple[str, ...] = ()  # extra zoekvragen naast de vraagteksten
    toelichting: str = ""  # extra uitleg voor het LLM bij dit blok

    @property
    def model(self) -> type[BaseModel]:
        return Formulier.model_fields[self.sectie].annotation

    @property
    def schema_naam(self) -> str:
        """Naam voor het JSON-schema van de aanroep (alleen letters, cijfers en _)."""
        return "blok_" + "".join(c if c.isalnum() else "_" for c in self.naam.lower())

    def veldnamen(self) -> list[str]:
        return list(self.velden) if self.velden is not None else list(self.model.model_fields)


BLOKKEN: tuple[Blok, ...] = (
    Blok(
        naam="05 Vakantiebijslag",
        sectie="vakantiebijslag",
        zoektermen=("vakantiebijslag", "vakantietoeslag vakantiegeld percentage", "vakantiebijslag berekend over"),
        toelichting="Vakantiebijslag heet ook vakantietoeslag of vakantiegeld; meestal een percentage van het (jaar)loon.",
    ),
)

# Secties die niet uit de cao komen maar uit de parameters (naam, KvK, contactpersoon, ...).
UIT_PARAMETERS = ("algemeen", "ondertekenen")
