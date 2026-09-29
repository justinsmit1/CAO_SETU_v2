"""07 · Bijzondere uitkeringen (docs/formulier/07_bijzondere-uitkeringen.md).

Vier subsecties, elk met een ja/nee-vraag en bij ``ja`` een herhaalbare lijst variaties.
"""

import datetime as dt

from ._basis import FormulierModel, Keuze, veld
from .codes import JaNee, Loonbasis, Peildatum
from .voorwaarden import Als


class HoeToegekend(Keuze):
    """Hoe wordt de uitkering toegekend? (eenmalig, jubileum, variabel)."""

    PERCENTAGE_LOON = "percentage-loon", "Vast percentage van het loon"
    VAST_BEDRAG = "vast-bedrag", "Vast bedrag, namelijk:"
    ANDERS = "anders", "Anders, namelijk:"


class HoeToegekendVast(Keuze):
    """Hoe wordt de uitkering toegekend? (vaste uitkeringen)."""

    DERTIENDE_MAAND = "dertiende-maand", "Als dertiende maand"
    PERCENTAGE_LOON = "percentage-loon", "Vast percentage van het loon"
    VAST_BEDRAG = "vast-bedrag", "Vast bedrag, namelijk:"
    ANDERS = "anders", "Anders, namelijk:"


class SoortVariabeleUitkering(Keuze):
    PERFORMANCE = "performance", "Performance uitkering"
    BONUS = "bonus", "Bonusuitkering"
    WINST = "winst", "Winstuitkering"
    ANDERS = "anders", "Anders, namelijk:"


_PCT = Als("hoe_toegekend", HoeToegekend.PERCENTAGE_LOON)
_VAST = Als("hoe_toegekend", HoeToegekend.VAST_BEDRAG)
_ANDERS = Als("hoe_toegekend", HoeToegekend.ANDERS)
_MIN_DUUR = Als("min_duur_dienstverband")
_OP_DATUM = Als("dienstverband_op_datum")
_VW_ANDERS = Als("voorwaarde_anders")
_MIN_MAX = Als("min_max", JaNee.JA)
_NAAR_RATO = (
    "Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband en/of afhankelijk van de duur "
    "van het dienstverband?"
)


# Eenmalige uitkeringen


class EenmaligeUitkering(FormulierModel):
    """Variatie ``eenmalige-uitkeringen[i]`` (zichtbaar als eenmalige-uitkeringen-bekend = ja)."""

    naam: str | None = veld("eenmalige-uitkeringen[i]/namelijk", 'Naam (bij >1 variatie: "Naam (variatie {num})")')

    # Welke voorwaarden zijn van toepassing?
    min_duur_dienstverband: bool | None = veld(
        "eenmalige-uitkeringen[i]/voorwaarden/min-duur-dienstverband",
        "Afhankelijk minimale duur dienstverband, namelijk:",
    )
    dienstverband_op_datum: bool | None = veld(
        "eenmalige-uitkeringen[i]/voorwaarden/dienstverband-op-datum",
        "Afhankelijk van dienstverband op bepaalde datum, namelijk:",
    )
    voorwaarde_anders: bool | None = veld("eenmalige-uitkeringen[i]/voorwaarden/anders", "Anders, namelijk:")
    min_duur_namelijk: str | None = veld(
        "eenmalige-uitkeringen[i]/voorwaarden_min-duur_namelijk", "(geen vraagtekst)", toon_als=_MIN_DUUR
    )
    dienstverband_datum_namelijk: str | None = veld(
        "eenmalige-uitkeringen[i]/voorwaarden_dienstverband-datum_namelijk", "(geen vraagtekst)", toon_als=_OP_DATUM
    )
    voorwaarde_anders_namelijk: str | None = veld(
        "eenmalige-uitkeringen[i]/voorwaarden_anders_namelijk", "(geen vraagtekst)", toon_als=_VW_ANDERS
    )

    # Uitkeringsmoment
    toekenning_datum: dt.date | None = veld(
        "eenmalige-uitkeringen[i]/toekenning-datum", "Op welk moment wordt de uitkering uitgekeerd?"
    )

    # Hoe wordt de uitkering toegekend?
    hoe_toegekend: HoeToegekend | None = veld(
        "eenmalige-uitkeringen[i]/hoe-toegekend", "Hoe wordt de uitkering toegekend?", vraagtype="radio"
    )
    percentage: float | None = veld(
        "eenmalige-uitkeringen[i]/type_ander-percentage_percentage", "Percentage (%) (geen vraagtekst)", toon_als=_PCT, eenheid="%"
    )
    percentage_van: Loonbasis | None = veld(
        "eenmalige-uitkeringen[i]/type_ander-percentage_van", "van", toon_als=_PCT, vraagtype="keuzelijst"
    )
    vast_bedrag: float | None = veld(
        "eenmalige-uitkeringen[i]/vast-bedrag_namelijk", "Bedrag (€) (geen vraagtekst)", toon_als=_VAST, eenheid="€"
    )
    anders: str | None = veld("eenmalige-uitkeringen[i]/anders", "(geen vraagtekst)", toon_als=_ANDERS)
    naar_rato_deeltijd: JaNee | None = veld(
        "eenmalige-uitkeringen[i]/naar-rato-deeltijd",
        "Wordt dit bedrag naar rato toegepast ingeval van een deeltijd dienstverband?",
        toon_als=_VAST, vraagtype="radio",
    )
    naar_rato_duur_dienstverband: JaNee | None = veld(
        "eenmalige-uitkeringen[i]/naar-rato-duur-dienstverband",
        "Wordt dit bedrag toegepast naar rato van de duur van het dienstverband?",
        toon_als=_VAST, vraagtype="radio",
    )

    # Minimum / maximum
    min_max: JaNee | None = veld(
        "eenmalige-uitkeringen[i]/min-max",
        "Geldt er een minimum- of een maximumbedrag?",
        toon_als="eenmalige-uitkering-hoe-toegekend ≠ anders (slug bestaat niet: in de praktijk altijd zichtbaar)",  # niet controleerbaar: webform-showIf verwijst naar niet-bestaande slug
        vraagtype="radio",
    )
    minimum: float | None = veld(
        "eenmalige-uitkeringen[i]/min-max/ja/minimum", "Minimum (€)", toon_als=_MIN_MAX, optioneel=True, eenheid="€"
    )
    maximum: float | None = veld(
        "eenmalige-uitkeringen[i]/min-max/ja/maximum", "Maximum (€)", toon_als=_MIN_MAX, optioneel=True, eenheid="€"
    )


# Vaste (onvoorwaardelijke) uitkeringen


class VasteUitkering(FormulierModel):
    """Variatie ``vaste-uitkeringen[i]`` (zichtbaar als vaste-uitkering-van-toepassing = ja)."""

    naam: str | None = veld("vaste-uitkeringen[i]/namelijk", 'Naam (bij >1 variatie: "Naam (variatie {num})")')

    # Welke voorwaarden zijn van toepassing?
    min_duur_dienstverband: bool | None = veld(
        "vaste-uitkeringen[i]/voorwaarden/min-duur-dienstverband",
        "Afhankelijk minimale duur dienstverband, namelijk:",
    )
    dienstverband_op_datum: bool | None = veld(
        "vaste-uitkeringen[i]/voorwaarden/dienstverband-op-datum",
        "Afhankelijk van dienstverband op bepaalde datum, namelijk:",
    )
    voorwaarde_anders: bool | None = veld("vaste-uitkeringen[i]/voorwaarden/anders", "Anders, namelijk:")
    min_duur_namelijk: str | None = veld(
        "vaste-uitkeringen[i]/voorwaarden_min-duur_namelijk", "(geen vraagtekst)", toon_als=_MIN_DUUR
    )
    dienstverband_datum_namelijk: str | None = veld(
        "vaste-uitkeringen[i]/voorwaarden_dienstverband-datum_namelijk", "(geen vraagtekst)", toon_als=_OP_DATUM
    )
    voorwaarde_anders_namelijk: str | None = veld(
        "vaste-uitkeringen[i]/voorwaarden_anders_namelijk", "(geen vraagtekst)", toon_als=_VW_ANDERS
    )

    # Uitkeringsmoment
    toekenning_datum: dt.date | None = veld(
        "vaste-uitkeringen[i]/toekenning-datum", "Op welk moment wordt de uitkering uitgekeerd?"
    )

    # Hoe wordt de uitkering toegekend?
    hoe_toegekend: HoeToegekendVast | None = veld(
        "vaste-uitkeringen[i]/hoe-toegekend", "Hoe wordt de uitkering toegekend?", vraagtype="radio"
    )
    percentage: float | None = veld(
        "vaste-uitkeringen[i]/type_ander-percentage_percentage", "namelijk (%)", toon_als=_PCT, eenheid="%"
    )
    percentage_van: Loonbasis | None = veld("vaste-uitkeringen[i]/type_ander-percentage_van", "van", toon_als=_PCT, vraagtype="keuzelijst")
    vast_bedrag: float | None = veld(
        "vaste-uitkeringen[i]/vast-bedrag_namelijk", "Bedrag (€) (geen vraagtekst)", toon_als=_VAST, eenheid="€"
    )
    anders: str | None = veld("vaste-uitkeringen[i]/anders", "(geen vraagtekst)", toon_als=_ANDERS)
    naar_rato: JaNee | None = veld("vaste-uitkeringen[i]/naar-rato", _NAAR_RATO, toon_als=_VAST, vraagtype="radio")


# Jubileumuitkering


class Jubileumuitkering(FormulierModel):
    """Variatie ``jubileumuitkeringen[i]`` (zichtbaar als jubileumuitkering-van-toepassing = ja)."""

    naam: str | None = veld("jubileumuitkeringen[i]/namelijk", 'Naam (bij >1 variatie: "Naam (variatie {num})")')

    # Hoe wordt de uitkering toegekend?
    hoe_toegekend: HoeToegekend | None = veld(
        "jubileumuitkeringen[i]/hoe-toegekend", "Hoe wordt de uitkering toegekend?", vraagtype="radio"
    )
    percentage: float | None = veld(
        "jubileumuitkeringen[i]/type_ander-percentage_percentage", "namelijk (%)", toon_als=_PCT, eenheid="%"
    )
    percentage_van: Loonbasis | None = veld("jubileumuitkeringen[i]/type_ander-percentage_van", "van", toon_als=_PCT, vraagtype="keuzelijst")
    vast_bedrag: float | None = veld(
        "jubileumuitkeringen[i]/vast-bedrag_namelijk", "Bedrag (€) (geen vraagtekst)", toon_als=_VAST, eenheid="€"
    )
    naar_rato: JaNee | None = veld("jubileumuitkeringen[i]/naar-rato", _NAAR_RATO, toon_als=_VAST, vraagtype="radio")
    anders: str | None = veld("jubileumuitkeringen[i]/anders", "(geen vraagtekst)", toon_als=_ANDERS)

    # Na hoeveel jaar dienstverband ontstaat recht op een jubileumuitkering?
    dienstverband_jaren: int | None = veld("jubileumuitkeringen[i]/dienstverband-duur/jaren", "Aantal jaren")
    dienstverband_maanden: int | None = veld(
        "jubileumuitkeringen[i]/dienstverband-duur/maanden", "Aantal maanden", optioneel=True
    )
    referentiedatum: Peildatum | None = veld(
        "jubileumuitkeringen[i]/dienstverband-duur/referentiedatum", "Referentiedatum", vraagtype="keuzelijst"
    )

    # Uitkeringsmoment en voorwaarden
    toekenning_datum: dt.date | None = veld(
        "jubileumuitkeringen[i]/toekenning-datum", "Op welk moment wordt de uitkering uitgekeerd?"
    )
    voorwaarden: str | None = veld(
        "jubileumuitkeringen[i]/voorwaarden", "Welke voorwaarden zijn van toepassing?", optioneel=True
    )


# Variabele (voorwaardelijke) uitkeringen


class VariabeleUitkering(FormulierModel):
    """Variatie ``variabele-uitkeringen[i]`` (zichtbaar als variabele-uitkering-van-toepassing = ja)."""

    soort: SoortVariabeleUitkering | None = veld(
        "variabele-uitkeringen[i]/soort", "Wat voor soort uitkering gaat het om?", vraagtype="radio"
    )
    soort_anders_namelijk: str | None = veld(
        "variabele-uitkeringen[i]/soort_anders_namelijk", "(geen vraagtekst)", toon_als=Als("soort", SoortVariabeleUitkering.ANDERS)
    )

    # Welke voorwaarden zijn van toepassing?
    prestatie: bool | None = veld(
        "variabele-uitkeringen[i]/voorwaarden/prestatie", "Bepaalde prestatie (performance), namelijk:"
    )
    resultaat: bool | None = veld("variabele-uitkeringen[i]/voorwaarden/resultaat", "Bepaald resultaat (winst), namelijk:")
    min_duur_dienstverband: bool | None = veld(
        "variabele-uitkeringen[i]/voorwaarden/min-duur-dienstverband",
        "Afhankelijk minimale duur dienstverband, namelijk:",
    )
    dienstverband_op_datum: bool | None = veld(
        "variabele-uitkeringen[i]/voorwaarden/dienstverband-op-datum",
        "Afhankelijk van dienstverband op bepaalde datum, namelijk:",
    )
    voorwaarde_anders: bool | None = veld("variabele-uitkeringen[i]/voorwaarden/anders", "Anders, namelijk:")
    prestatie_namelijk: str | None = veld(
        "variabele-uitkeringen[i]/voorwaarden_prestatie_namelijk",
        "(geen vraagtekst)",
        toon_als=Als("prestatie"),
    )
    resultaat_namelijk: str | None = veld(
        "variabele-uitkeringen[i]/voorwaarden_resultaat_namelijk",
        "(geen vraagtekst)",
        toon_als=Als("resultaat"),
    )
    min_duur_namelijk: str | None = veld(
        "variabele-uitkeringen[i]/voorwaarden_min-duur_namelijk", "(geen vraagtekst)", toon_als=_MIN_DUUR
    )
    dienstverband_datum_namelijk: str | None = veld(
        "variabele-uitkeringen[i]/voorwaarden_dienstverband-datum_namelijk", "(geen vraagtekst)", toon_als=_OP_DATUM
    )
    voorwaarde_anders_namelijk: str | None = veld(
        "variabele-uitkeringen[i]/voorwaarden_anders_namelijk", "(geen vraagtekst)", toon_als=_VW_ANDERS
    )

    # Uitkeringsmoment
    toekenning_datum: dt.date | None = veld(
        "variabele-uitkeringen[i]/toekenning-datum", "Op welk moment wordt de uitkering uitgekeerd?"
    )

    # Hoe wordt de uitkering toegekend?
    hoe_toegekend: HoeToegekend | None = veld(
        "variabele-uitkeringen[i]/hoe-toegekend", "Hoe wordt de uitkering toegekend?", vraagtype="radio"
    )
    percentage: float | None = veld(
        "variabele-uitkeringen[i]/type_ander-percentage_percentage", "namelijk (%)", toon_als=_PCT, eenheid="%"
    )
    percentage_van: Loonbasis | None = veld(
        "variabele-uitkeringen[i]/type_ander-percentage_van", "van", toon_als=_PCT, vraagtype="keuzelijst"
    )
    vast_bedrag: float | None = veld(
        "variabele-uitkeringen[i]/vast-bedrag_namelijk", "Bedrag (€) (geen vraagtekst)", toon_als=_VAST, eenheid="€"
    )
    anders: str | None = veld("variabele-uitkeringen[i]/anders", "(geen vraagtekst)", toon_als=_ANDERS)
    naar_rato: JaNee | None = veld("variabele-uitkeringen[i]/naar-rato", _NAAR_RATO, toon_als=_VAST, vraagtype="radio")

    # Minimum / maximum
    min_max: JaNee | None = veld("variabele-uitkeringen[i]/min-max", "Geldt er een minimum- of een maximumbedrag?", vraagtype="radio")
    minimum: float | None = veld("variabele-uitkeringen[i]/min-max/ja/minimum", "minimum (€)", toon_als=_MIN_MAX, eenheid="€")
    maximum: float | None = veld("variabele-uitkeringen[i]/min-max/ja/maximum", "maximum (€)", toon_als=_MIN_MAX, eenheid="€")


class BijzondereUitkeringen(FormulierModel):
    # Eenmalige uitkeringen
    eenmalige_uitkeringen_bekend: JaNee | None = veld(
        "eenmalige-uitkeringen-bekend", "Zijn er eenmalige uitkeringen bekend?", vraagtype="radio"
    )
    eenmalige_uitkeringen: list[EenmaligeUitkering] = veld(
        "eenmalige-uitkeringen[i]",
        "Variaties eenmalige uitkering",
        toon_als=Als("eenmalige_uitkeringen_bekend", JaNee.JA),
        lijst=True,
    )

    # Vaste (onvoorwaardelijke) uitkeringen
    vaste_uitkering_van_toepassing: JaNee | None = veld(
        "vaste-uitkering-van-toepassing", "Is er een vaste (onvoorwaardelijke) uitkering van toepassing?", vraagtype="radio"
    )
    vaste_uitkeringen: list[VasteUitkering] = veld(
        "vaste-uitkeringen[i]",
        "Variaties vaste uitkering",
        toon_als=Als("vaste_uitkering_van_toepassing", JaNee.JA),
        lijst=True,
    )

    # Jubileumuitkering
    jubileumuitkering_van_toepassing: JaNee | None = veld(
        "jubileumuitkering-van-toepassing",
        "Is er een jubileumuitkering of een vergelijkbare uitkering van toepassing?", vraagtype="radio",
    )
    jubileumuitkeringen: list[Jubileumuitkering] = veld(
        "jubileumuitkeringen[i]",
        "Variaties jubileumuitkering",
        toon_als=Als("jubileumuitkering_van_toepassing", JaNee.JA),
        lijst=True,
    )

    # Variabele (voorwaardelijke) uitkeringen
    variabele_uitkering_van_toepassing: JaNee | None = veld(
        "variabele-uitkering-van-toepassing", "Is er een variabele (voorwaardelijke) uitkering van toepassing?", vraagtype="radio"
    )
    variabele_uitkeringen: list[VariabeleUitkering] = veld(
        "variabele-uitkeringen[i]",
        "Variaties variabele uitkering",
        toon_als=Als("variabele_uitkering_van_toepassing", JaNee.JA),
        lijst=True,
    )
