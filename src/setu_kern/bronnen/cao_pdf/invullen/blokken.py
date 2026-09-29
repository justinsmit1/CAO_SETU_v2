"""De indeling in LLM-aanroepen: per blok één aanroep.

Een blok is een sectie van het Formulier, of een deel ervan (``velden``: velden op het hoogste niveau van de
sectie). Grote secties (04, 06, 12, 13) worden later per blok gesplitst; hun schema is anders te groot.

Nu ondersteund: 05 Vakantiebijslag. Nieuwe blokken voeg je toe aan ``BLOKKEN``; secties zonder blok staan in het
rapport als "nog niet ondersteund".
"""

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel

from ....kern import InquiryPayEquity
from ...wijzerbelonen.formulier import Formulier
from .uitgebreid_vakantiebijslag import VakantiebijslagSETU
from .uitgebreid_vakantiebijslag import naar_formulier as vakantiebijslag_naar_formulier
from .uitgebreid_vakantiebijslag import naar_kern as vakantiebijslag_naar_kern


@dataclass(frozen=True)
class Blok:
    """Een LLM-aanroep. Meestal een sectie van het wijzerbelonen-Formulier.

    Een *uitgebreid* blok (``uitgebreid``) vraagt meer dan de webform kent. Het LLM vult dan dat eigen model in en:
    - ``naar_formulier`` haalt daar de webform-vragen uit (het Formulier blijft 1-op-1 met de webform);
    - ``naar_kern`` zet de volledige SETU-regeling in het kernbericht en geeft meldingen terug.
    """

    naam: str  # voor het rapport, bijv. "05 Vakantiebijslag"
    sectie: str  # attribuut van Formulier, bijv. "vakantiebijslag"
    velden: tuple[str, ...] | None = None  # None = de hele sectie
    zoektermen: tuple[str, ...] = ()  # extra zoekvragen naast de vraagteksten
    toelichting: str = ""  # extra uitleg voor het LLM bij dit blok
    uitgebreid: type[BaseModel] | None = None
    naar_formulier: Callable[[BaseModel], BaseModel] | None = None
    naar_kern: Callable[[BaseModel, InquiryPayEquity, Formulier], list[str]] | None = None

    @property
    def model(self) -> type[BaseModel]:
        return self.uitgebreid or Formulier.model_fields[self.sectie].annotation

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

VAKANTIEBIJSLAG_SETU = Blok(
    naam="05 Vakantiebijslag (SETU)",
    sectie="vakantiebijslag",
    zoektermen=(
        "vakantiebijslag",
        "vakantietoeslag vakantiegeld percentage",
        "vakantiebijslag berekend over",
        "vakantiebijslag uitbetaald in mei of juni",
        "vakantiebijslag minimum maximum naar evenredigheid",
    ),
    toelichting=(
        "Vakantiebijslag heet ook vakantietoeslag of vakantiegeld; meestal een percentage van het (jaar)loon.\n"
        "Vul ook de details in als de cao ze noemt: geldigheid, uitbetaalmaand, minimum en maximum, naar rato en "
        "voorwaarden. Maak een aparte regel per tarief. Laat een detail dat niet genoemd wordt null."
    ),
    uitgebreid=VakantiebijslagSETU,
    naar_formulier=vakantiebijslag_naar_formulier,
    naar_kern=vakantiebijslag_naar_kern,
)

# Zoals BLOKKEN, maar met de SETU-velden die de webform niet kent (geldigheid, uitbetaling, minimum/maximum, naar rato,
# voorwaarden). Nog een proef voor de vakantiebijslag; de standaard BLOKKEN blijft 1-op-1 met de webform.
BLOKKEN_SETU: tuple[Blok, ...] = (VAKANTIEBIJSLAG_SETU,)

# Secties die niet uit de cao komen maar uit de parameters (naam, KvK, contactpersoon, ...).
UIT_PARAMETERS = ("algemeen", "ondertekenen")
