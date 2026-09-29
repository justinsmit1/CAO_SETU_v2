"""Adapter cao-pdf → kern.

    formulier, rapport = vul_formulier(llm, zoeker, parameters)    # eerst zelf controleren (rapport met citaten)
    resultaat = van_cao_pdf(llm, zoeker, parameters)                # meteen naar de kern
    resultaat = van_cao_pdf(llm, zoeker, parameters, basis=basis)   # ontbrekende SETU-onderdelen uit een basis

De CAO-pdf is de bron; het LLM vult per blok het wijzerbelonen-``Formulier`` in (de vragenlijst), en de
wijzerbelonen-adapter brengt dat naar de kern. Zo komen een LLM-resultaat en een handmatig ingevulde
wijzerbelonen-download langs dezelfde weg in de kern, en zijn ze te vergelijken.

Een *uitgebreid* blok (``BLOKKEN_SETU``) vraagt ook de SETU-velden die de webform niet kent. Het Formulier krijgt dan
alleen de webform-vragen; de volledige regeling komt uit ``rapport.uitbreidingen`` en vervangt de regeling in de kern.

``llm`` is elk object met ``vraag_json`` (zie ``llm.py``): ``MistralLLM(model=...)`` of in tests ``nep.NepLLM``.
``zoeker`` zoekt in de cao: ``IndexZoeker.laad("index")`` of in tests ``nep.LijstZoeker``.
"""

from .. import Resultaat
from ..wijzerbelonen import van_formulier
from ..wijzerbelonen.formulier import Formulier
from .invullen.blokken import BLOKKEN, UIT_PARAMETERS, Blok
from .invullen.rapport import Rapport
from .invullen.uitvoeren import vul_blok
from .llm import LLM
from .parameters import Parameters
from .zoeken import Zoeker

BRON_CAO_PDF = "cao_pdf"


def vul_formulier(
    llm: LLM,
    zoeker: Zoeker,
    parameters: Parameters | None = None,
    blokken: tuple[Blok, ...] = BLOKKEN,
    top_k: int = 8,
    basis: Formulier | None = None,
) -> tuple[Formulier, Rapport]:
    """Vult het Formulier met het LLM, blok voor blok. Geeft het formulier en het rapport terug.

    ``basis``: een al (deels) ingevuld formulier om mee te beginnen, bijv. voor de SETU-verplichte onderdelen
    die het LLM nog niet invult (salaristabel). Het wordt niet gewijzigd. Een blok overschrijft zijn velden in de
    basis; de secties die uit de basis komen, staan in het rapport als "uit het basisformulier"."""
    formulier = basis.model_copy(deep=True) if basis is not None else Formulier()
    rapport = Rapport()
    if basis is not None:
        leeg, blok_secties = Formulier(), {b.sectie for b in blokken}
        rapport.uit_basis = [
            s for s in Formulier.model_fields if s not in blok_secties and getattr(basis, s) != getattr(leeg, s)
        ]
    if parameters:
        rapport.uit_parameters = parameters.toepassen(formulier)
    for blok in blokken:
        rapport.blokken.append(vul_blok(blok, formulier, llm, zoeker, top_k=top_k, uitbreidingen=rapport.uitbreidingen))
    gedekt = {b.sectie for b in blokken} | set(UIT_PARAMETERS) | set(rapport.uit_basis)
    rapport.niet_ondersteund = [s for s in Formulier.model_fields if s not in gedekt]
    rapport.controle = formulier.controleer()
    return formulier, rapport


def van_cao_pdf(
    llm: LLM,
    zoeker: Zoeker,
    parameters: Parameters | None = None,
    blokken: tuple[Blok, ...] = BLOKKEN,
    top_k: int = 8,
    basis: Formulier | None = None,
) -> Resultaat:
    """Het kernmodel uit de cao. ``ValueError`` als SETU-verplichte onderdelen ontbreken (bijv. een salaristabel
    zolang 02 Beloning nog niet door het LLM wordt ingevuld; geef die dan mee in ``basis``)."""
    formulier, rapport = vul_formulier(llm, zoeker, parameters, blokken, top_k, basis)
    return kern_uit_formulier(formulier, rapport, blokken)


def kern_uit_formulier(formulier: Formulier, rapport: Rapport, blokken: tuple[Blok, ...] = BLOKKEN) -> Resultaat:
    """Het kernmodel van een ingevuld formulier plus de uitbreidingen uit ``rapport`` (zie ``vul_formulier``).
    Zo hoeft het LLM niet opnieuw aangeroepen te worden als je het rapport al hebt."""
    omgezet = van_formulier(formulier)
    meldingen = rapport.meldingen() + omgezet.meldingen
    for blok in blokken:
        if blok.naar_kern and blok.sectie in rapport.uitbreidingen:
            meldingen += blok.naar_kern(rapport.uitbreidingen[blok.sectie], omgezet.bericht, formulier)
    return Resultaat(omgezet.bericht, meldingen, BRON_CAO_PDF)
