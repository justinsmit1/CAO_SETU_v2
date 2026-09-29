"""SETU-kernmodel: Inquiry Pay Equity v2.0 (Gelijkwaardig Belonen), onafhankelijk van welk formulier dan ook.

Snelstart::

    from setu_kern.kern import InquiryPayEquity
    bericht = InquiryPayEquity.lees("bestand.json")
    bericht.valideer()          # [] = geldig volgens het officiële schema
    bericht.schrijf("uit.json")
"""

from . import basis, beloning, codes, condities, partij, regelingen, tijd
from .bericht import InquiryPayEquity, officieel_schema, valideer_json

__all__ = [
    "InquiryPayEquity",
    "basis",
    "beloning",
    "codes",
    "condities",
    "officieel_schema",
    "partij",
    "regelingen",
    "tijd",
    "valideer_json",
]
