"""05 · Vakantiebijslag (docs/formulier/05_vakantiebijslag.md)."""

from ._basis import FormulierModel, veld
from .bouwstenen import BedragSoort, Bedragregel
from .codes import JaNee
from .voorwaarden import Als


class Vakantiebijslag(FormulierModel):
    ja_nee: JaNee | None = veld("vakantiebijslag/ja-nee", "Is er een vakantiebijslag?", vraagtype="radio")
    bedrag: Bedragregel | None = veld(
        "vakantiebijslag/…",
        "Hoeveel bedraagt de vakantiebijslag?",
        toon_als=Als("ja_nee", JaNee.JA), opties=[BedragSoort.PERCENTAGE],
    )
