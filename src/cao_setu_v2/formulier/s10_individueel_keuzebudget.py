"""10 · Individueel keuzebudget (docs/formulier/10_individueel-keuzebudget.md)."""


from ._basis import FormulierModel, Keuze, veld
from .bouwstenen import BedragSoort, Bedragregel
from .codes import JaNee
from .voorwaarden import Als, En


class IkbVan(Keuze):
    """Keuzelijst "van" (vanOptions, alleen in deze sectie); Nederlandse formulierwaarden, geen SETU-codes."""

    UURLOON = "uurloon", "uurloon"
    WEEKLOON = "weekloon", "weekloon"
    MAANDLOON = "maandloon", "maandloon"
    PERIODELOON = "periodeloon", "periodeloon"
    MINIMUMLOON = "minimumloon", "minimumloon"


_IKB = Als("ja_nee", JaNee.JA)
_OPGENOMEN = En(_IKB, Als("arbeidsvoorwaarden_opgenomen", JaNee.JA))
_VAKANTIEDAGEN = Als("bovenwettelijke_vakantiedagen")
_ADV = Als("adv_dagen")
_EINDEJAARSUITKERING = Als("eindejaarsuitkering")
_VAKANTIEBIJSLAG = Als("vakantiebijslag")


class IndividueelKeuzebudget(FormulierModel):
    # Individueel keuze budget
    ja_nee: JaNee | None = veld(
        "individueel-keuzebudget",
        "Ken je een individueel keuze budget (IKB) of een vergelijkbaar budget waarbij de werknemer kan kiezen "
        "uit door de werkgever bepaalde keuzes?", vraagtype="radio",
    )

    # Waarde van het budget
    waarde: Bedragregel | None = veld(
        "individueel-keuzebudget/…",
        "Wat is de waarde van dit budget?",
        toon_als=_IKB, opties=[BedragSoort.VAST_BEDRAG, BedragSoort.PERCENTAGE],
    )

    # Zijn er bepaalde arbeidsvoorwaarden in het budget opgenomen?
    arbeidsvoorwaarden_opgenomen: JaNee | None = veld(
        "ikb-arbeidsvoorwaarden-opgenomen",
        "Zijn er bepaalde arbeidsvoorwaarden in het budget opgenomen?",
        toon_als=_IKB, vraagtype="radio",
    )

    # Welke arbeidsvoorwaarden zijn in het budget opgenomen?
    bovenwettelijke_vakantiedagen: bool | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/bovenwettelijke-vakantiedagen",
        "Bovenwettelijke vakantiedagen voor",
        toon_als=_OPGENOMEN,
    )
    bovenwettelijke_vakantiedagen_percentage: float | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/bovenwettelijke-vakantiedagen/percentage",
        "percentage (%)",
        toon_als=_VAKANTIEDAGEN, eenheid="%",
    )
    bovenwettelijke_vakantiedagen_van: IkbVan | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/bovenwettelijke-vakantiedagen/van", "van", toon_als=_VAKANTIEDAGEN, vraagtype="keuzelijst"
    )
    adv_dagen: bool | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/adv-dagen", "ADV dagen voor", toon_als=_OPGENOMEN
    )
    adv_dagen_percentage: float | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/adv-dagen/percentage", "percentage (%)", toon_als=_ADV, eenheid="%"
    )
    adv_dagen_van: IkbVan | None = veld("ikb-opgenomen-arbeidsvoorwaarden/adv-dagen/van", "van", toon_als=_ADV, vraagtype="keuzelijst")
    eindejaarsuitkering: bool | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/eindejaarsuitkering", "Eindejaarsuitkering voor", toon_als=_OPGENOMEN
    )
    eindejaarsuitkering_percentage: float | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/eindejaarsuitkering/percentage",
        "percentage (%)",
        toon_als=_EINDEJAARSUITKERING, eenheid="%",
    )
    eindejaarsuitkering_van: IkbVan | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/eindejaarsuitkering/van", "van", toon_als=_EINDEJAARSUITKERING, vraagtype="keuzelijst"
    )
    vakantiebijslag: bool | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/vakantiebijslag", "Vakantiebijslag voor", toon_als=_OPGENOMEN
    )
    vakantiebijslag_percentage: float | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/vakantiebijslag/percentage", "percentage (%)", toon_als=_VAKANTIEBIJSLAG, eenheid="%"
    )
    vakantiebijslag_van: IkbVan | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/vakantiebijslag/van", "van", toon_als=_VAKANTIEBIJSLAG, vraagtype="keuzelijst"
    )
    anders: bool | None = veld("ikb-opgenomen-arbeidsvoorwaarden/anders", "Anders, namelijk:", toon_als=_OPGENOMEN)
    anders_namelijk: str | None = veld(
        "ikb-opgenomen-arbeidsvoorwaarden/anders/namelijk",
        "(namelijk)",
        toon_als=Als("anders"),
    )
