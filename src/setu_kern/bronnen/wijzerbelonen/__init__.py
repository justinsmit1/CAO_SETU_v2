"""Bron wijzerbelonen.nl (standaard-uitvraag Gelijkwaardig Belonen, webform v2.1.0).

- ``formulier/``: het formulier van de tool als Python-model (interne weergave van deze bron, niet de standaard);
- ``koppeling/``: formulier → antwoorden (``__webform_data__``) → SETU-JSON, zoals de webform het doet;
- ``adapter``: het contract met de kern (``van_formulier``, ``van_export``, ``schrijf_upload``).
"""

from .adapter import BRON_EXPORT, BRON_FORMULIER, BRON_SETU, schrijf_upload, van_export, van_formulier

__all__ = ["BRON_EXPORT", "BRON_FORMULIER", "BRON_SETU", "schrijf_upload", "van_export", "van_formulier"]
