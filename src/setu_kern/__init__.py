"""setu_kern: één SETU-kern (``InquiryPayEquity``) met per bron een adapter ernaartoe. Zie README.md.

    from setu_kern.bronnen.wijzerbelonen import van_export
    resultaat = van_export("download.json")
    resultaat.bericht, resultaat.meldingen
"""

from .bronnen import Resultaat
from .kern import InquiryPayEquity

__all__ = ["InquiryPayEquity", "Resultaat"]
