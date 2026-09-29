"""Bron CAO-pdf: een LLM vult het wijzerbelonen-Formulier in op basis van de cao, met een citaat per antwoord.

- ``adapter``: ``vul_formulier`` (Formulier + rapport) en ``van_cao_pdf`` (Resultaat voor de kern);
- ``llm``: het LLM-protocol en ``MistralLLM`` (het model is nog niet gekozen: ``[invullen] model`` in config.toml);
- ``zoeken``: het zoek-protocol en ``IndexZoeker`` (FAISS-index van de pijplijn);
- ``invullen/``: blokken, schema, omzetting, prompt, uitvoeren en rapport;
- ``pijplijn/``: KOPIE van cao_setu_v2/llm_pipeline (pdf inlezen, index, zoeken);
- ``nep``: ``NepLLM`` en ``LijstZoeker`` voor tests zonder API.
"""

from .adapter import BRON_CAO_PDF, van_cao_pdf, vul_formulier
from .invullen.blokken import BLOKKEN, BLOKKEN_SETU, Blok
from .invullen.rapport import Rapport
from .llm import LLM, MistralLLM
from .parameters import Parameters
from .zoeken import Fragment, IndexZoeker, Zoeker

__all__ = [
    "BLOKKEN",
    "BLOKKEN_SETU",
    "BRON_CAO_PDF",
    "Blok",
    "Fragment",
    "IndexZoeker",
    "LLM",
    "MistralLLM",
    "Parameters",
    "Rapport",
    "Zoeker",
    "van_cao_pdf",
    "vul_formulier",
]
