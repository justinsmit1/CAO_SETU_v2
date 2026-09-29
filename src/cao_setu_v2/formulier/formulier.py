"""Het complete webformulier "Standaard uitvraag Gelijkwaardig Belonen" (wijzerbelonen.nl, v2.1.0).

Eén attribuut per sectie, in de volgorde van de tool. Zie docs/formulier/README.md.
"""

from typing import ClassVar

from pydantic import Field

from ._basis import FormulierModel
from .s01_algemeen import Algemeen
from .s02_beloning import Beloning
from .s03_functiegroepen import Functiegroepen
from .s04_toeslagen import Toeslagen
from .s05_vakantiebijslag import Vakantiebijslag
from .s06_vergoedingen import Vergoedingen
from .s07_bijzondere_uitkeringen import BijzondereUitkeringen
from .s08_loondoorbetaling_bij_ziekte import LoondoorbetalingBijZiekte
from .s09_verlof import Verlof
from .s10_individueel_keuzebudget import IndividueelKeuzebudget
from .s11_pensioen import Pensioen
from .s12_duurzaam_werken_en_leven import DuurzaamWerkenEnLeven
from .s13_aanvullende_regelingen import AanvullendeRegelingen
from .s14_overig import Overig
from .s15_grondslagen import Grondslagen
from .s16_ondertekenen import Ondertekenen
from .voorwaarden import schendingen

WEBFORM_APP_VERSION = "2.1.0"


class Formulier(FormulierModel):
    is_wortel: ClassVar[bool] = True  # paden "/sectie.veld" in voorwaarden beginnen hier

    algemeen: Algemeen = Field(default_factory=Algemeen)
    beloning: Beloning = Field(default_factory=Beloning)
    functiegroepen: Functiegroepen = Field(default_factory=Functiegroepen)
    toeslagen: Toeslagen = Field(default_factory=Toeslagen)
    vakantiebijslag: Vakantiebijslag = Field(default_factory=Vakantiebijslag)
    vergoedingen: Vergoedingen = Field(default_factory=Vergoedingen)
    bijzondere_uitkeringen: BijzondereUitkeringen = Field(default_factory=BijzondereUitkeringen)
    loondoorbetaling_bij_ziekte: LoondoorbetalingBijZiekte = Field(default_factory=LoondoorbetalingBijZiekte)
    verlof: Verlof = Field(default_factory=Verlof)
    individueel_keuzebudget: IndividueelKeuzebudget = Field(default_factory=IndividueelKeuzebudget)
    pensioen: Pensioen = Field(default_factory=Pensioen)
    duurzaam_werken_en_leven: DuurzaamWerkenEnLeven = Field(default_factory=DuurzaamWerkenEnLeven)
    aanvullende_regelingen: AanvullendeRegelingen = Field(default_factory=AanvullendeRegelingen)
    overig: Overig = Field(default_factory=Overig)
    grondslagen: Grondslagen = Field(default_factory=Grondslagen)
    ondertekenen: Ondertekenen = Field(default_factory=Ondertekenen)

    def controleer(self) -> list[str]:
        """Alle geschonden voorwaarden in het hele formulier, ook die tussen secties.

        Bij het toewijzen van één veld (``f.algemeen.cao_naam = ...``) controleert Pydantic alleen dat
        submodel; voorwaarden die naar een andere sectie verwijzen worden pas hier gecontroleerd.
        """
        return schendingen(self)
