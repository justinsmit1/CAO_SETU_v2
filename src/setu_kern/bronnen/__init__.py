"""Bronnen: alles wat gegevens aanlevert (formulieren, exports, later ook bijv. een LLM of Excel).

Elke bron heeft een adapter die naar het kernmodel gaat en een ``Resultaat`` teruggeeft. Wat de bron wel kent maar
SETU niet, of wat bij het omzetten is rechtgezet of weggelaten, staat in ``meldingen``: niets verdwijnt stil.
"""

from dataclasses import dataclass, field

from ..kern import InquiryPayEquity


@dataclass
class Resultaat:
    """Wat elke adapter teruggeeft: het SETU-bericht, de meldingen en waar het vandaan komt."""

    bericht: InquiryPayEquity
    meldingen: list[str] = field(default_factory=list)
    bron: str = ""  # bijv. "wijzerbelonen:formulier", "wijzerbelonen:export"

    @property
    def geldig(self) -> bool:
        """Voldoet het bericht aan het officiële SETU-schema?"""
        return not self.bericht.valideer()


__all__ = ["Resultaat"]
