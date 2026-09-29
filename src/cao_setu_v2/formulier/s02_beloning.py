"""02 · Beloning (docs/formulier/02_beloning.md).

Genest en herhaalbaar: ``beloningen[i]`` (salaristabel) → ``salarisschalen[j]`` → ``stappen[k]``,
en daarnaast ``beloningen[i]/afwijkende-roosters[r]``. Per salaristabel zijn er vijf subsecties.
"""

import datetime as dt
from enum import Enum

from ._basis import FormulierModel, Keuze, veld
from .codes import JaNee
from .voorwaarden import Als, En, Niet


class NormaleArbeidsduur(Enum):
    """Let op: de webform slaat de uren op als getal (``40``), alleen "Anders, namelijk:" als tekst.

    Daarom geen ``Keuze`` (tekst-enum): met ``"40"`` herkent de webform de optie niet en komt er geen
    ``workDuration`` in de SETU.
    """

    label: str

    UUR_40 = 40, "40 uur"
    UUR_38 = 38, "38 uur"
    UUR_36 = 36, "36 uur"
    ANDERS = "anders", "Anders, namelijk:"

    def __new__(cls, waarde: int | str, label: str) -> "NormaleArbeidsduur":
        obj = object.__new__(cls)
        obj._value_ = waarde
        obj.label = label
        return obj

    def __str__(self) -> str:
        return str(self.value)


class BeloningInterval(Keuze):
    """Hoe is de beloning vastgesteld? / Per (afwijkend rooster)."""

    PER_MAAND = "per-maand", "Per maand"
    PER_VIER_WEKEN = "per-vier-weken", "Per vier weken"
    PER_WEEK = "per-week", "Per week"
    PER_UUR = "per-uur", "Per uur"


class WerkervaringInschaling(Keuze):
    JA_SECTOR = "ja-sector", "Ja, relevante werkervaring in de sector wordt als volgt meegenomen"
    JA_ONDERNEMING = "ja-onderneming", "Ja, relevante werkervaring bij onze onderneming wordt als volgt meegenomen"
    JA_FUNCTIE = "ja-functie", "Ja, relevante werkervaring in dezelfde functie (ongeacht de sector) wordt als volgt meegenomen"
    JA_ALS_VOLGT = "ja-als-volgt", "Ja, namelijk als volgt"
    NEE = "nee", "Nee"


class VerhogingWanneer(Keuze):
    VAST_MOMENT = "vast-moment", "Op een vast moment, namelijk:"
    GEWERKT_JAAR = "gewerkt-jaar", "Per gewerkt jaar"
    ANDERS = "anders", "Anders, namelijk:"


class VerhogingBerekening(Keuze):
    VAST_PERCENTAGE = "vast-percentage", "Vast percentage van het loon, namelijk:"
    VAST_BEDRAG = "vast-bedrag", "Vast bedrag, namelijk:"
    TREDEN = "treden", "Overeenkomstig de treden in de salaristabellen, namelijk:"
    ANDERS = "anders", "Anders, namelijk:"


class EenmaligeVerhogingType(Keuze):
    EURO = "Euro", "Een vast bedrag"
    PERCENTAGE = "Percentage", "Een percentage"


_UURLONEN_BLOK = Niet(Als("beloning_vastgesteld", BeloningInterval.PER_UUR))  # ook als er nog niets gekozen is
_PERIODIEKEN_BLOK = Als("periodieke_verhogingen", JaNee.JA)
_EENMALIG_JA = Als("initiele_eenmalige_verhogingen", JaNee.JA)
_ROOSTERS_BLOK = Als("afwijkende_arbeidsduur", JaNee.JA)
_ROOSTERS_RIJ = Als("../afwijkende_arbeidsduur", JaNee.JA)  # vanuit een rij van afwijkende_roosters
_RIJ_AANGEVINKT = Als("aangevinkt")


# Welke salarisschalen kent de onderneming?


class Stap(FormulierModel):
    naam: str | None = veld("beloningen[i]/salarisschalen[j]/stappen[k]/naam", "Stap / Trede")
    bedrag: float | None = veld("beloningen[i]/salarisschalen[j]/stappen[k]/bedrag", "Bedrag (€)", eenheid="€")


class Salarisschaal(FormulierModel):
    naam: str | None = veld("beloningen[i]/salarisschalen[j]/naam", "Schaal")
    minimaal_bedrag: float | None = veld(
        "beloningen[i]/salarisschalen[j]/minimaal-bedrag", "Minimaal bedrag (€)", optioneel=True, eenheid="€"
    )
    maximaal_bedrag: float | None = veld(
        "beloningen[i]/salarisschalen[j]/maximaal-bedrag", "Maximaal bedrag (€)", optioneel=True, eenheid="€"
    )
    stappen: list[Stap] = veld("beloningen[i]/salarisschalen[j]/stappen[k]", "Stappen", lijst=True)


# Periodieken: dezelfde vragenset voor elk van de vier vaste rijen (<rij>)


class PeriodiekeVerhoging(FormulierModel):
    aangevinkt: bool | None = veld("beloningen[i]/<rij>", "(label van de rij)", toon_als=Als("../periodieke_verhogingen", JaNee.JA))
    wanneer: VerhogingWanneer | None = veld(
        "beloningen[i]/<rij>/wanneer",
        "Wanneer wordt de periodieke of andere verhoging toegekend?",
        toon_als=_RIJ_AANGEVINKT, vraagtype="radio",
    )
    wanneer_vast_moment: dt.date | None = veld(
        "beloningen[i]/<rij>/wanneer/vast-moment/namelijk",
        "Op een vast moment, namelijk: (datum)",
        toon_als=Als("wanneer", VerhogingWanneer.VAST_MOMENT),
    )
    wanneer_anders: str | None = veld(
        "beloningen[i]/<rij>/wanneer/anders/namelijk",
        "Anders, namelijk: (tekstvak)",
        toon_als=Als("wanneer", VerhogingWanneer.ANDERS),
    )
    berekening: VerhogingBerekening | None = veld(
        "beloningen[i]/<rij>/berekening",
        "Hoe wordt de periodieke of andere verhoging berekend?",
        toon_als=_RIJ_AANGEVINKT, vraagtype="radio",
    )
    berekening_vast_percentage: float | None = veld(
        "beloningen[i]/<rij>/berekening/vast-percentage/namelijk",
        "Vast percentage van het loon, namelijk: (%)",
        toon_als=Als("berekening", VerhogingBerekening.VAST_PERCENTAGE), eenheid="%",
    )
    berekening_vast_bedrag: float | None = veld(
        "beloningen[i]/<rij>/berekening/vast-bedrag/namelijk",
        "Vast bedrag, namelijk: (€)",
        toon_als=Als("berekening", VerhogingBerekening.VAST_BEDRAG), eenheid="€",
    )
    berekening_treden: float | None = veld(
        "beloningen[i]/<rij>/berekening/treden/namelijk",
        "Overeenkomstig de treden in de salaristabellen, namelijk: (trede(n) per jaar)",
        toon_als=Als("berekening", VerhogingBerekening.TREDEN), eenheid="jaar",
    )
    berekening_anders: str | None = veld(
        "beloningen[i]/<rij>/berekening/anders/namelijk",
        "Anders, namelijk: (tekstvak)",
        toon_als=Als("berekening", VerhogingBerekening.ANDERS),
    )


# Afwijkende roosters


class AfwijkendRooster(FormulierModel):
    arbeidsduur: float | None = veld(
        "beloningen[i]/afwijkende-roosters[r]/arbeidsduur", "Arbeidsduur (uur)", toon_als=_ROOSTERS_RIJ, eenheid="uur"
    )
    arbeidsduur_per: BeloningInterval | None = veld(
        "beloningen[i]/afwijkende-roosters[r]/arbeidsduur-per", "Per", toon_als=_ROOSTERS_RIJ, vraagtype="keuzelijst"
    )
    in_situatie: str | None = veld(
        "beloningen[i]/afwijkende-roosters[r]/in-situatie",
        "in de volgende situatie: (bijvoorbeeld bij werken in een vijf of drie ploegendienst)",
        toon_als=_ROOSTERS_RIJ,
    )
    uurloon_factor_vastgelegd: JaNee | None = veld(
        "beloningen[i]/afwijkende-roosters[r]/uurloon-factor-vastgelegd",
        "Zijn in jouw arbeidsvoorwaardenregeling of cao uurlonen vastgelegd of kent jouw cao (...) een eenduidige "
        "berekeningsmethodiek om het maand-/periodeloon terug te rekenen naar een uurloon voor de werknemer "
        "waarvoor een afwijkende arbeidsduur geldt?",
        toon_als=_ROOSTERS_RIJ, vraagtype="radio",
    )
    uurloon_factor: float | None = veld(
        "beloningen[i]/afwijkende-roosters[r]/uurloon-factor",
        "Ja, namelijk: (%)",
        toon_als=En(_ROOSTERS_RIJ, Als("uurloon_factor_vastgelegd", JaNee.JA)), eenheid="%",
    )


# Salaristabel (beloningen[i])


class Salaristabel(FormulierModel):
    # Salaristabellen
    naam: str | None = veld("beloningen[i]/naam", "Naam")

    # Geldende periodeloon in de schalen › Deze salaristabel is geldig
    geldig_vanaf: dt.date | None = veld("beloningen[i]/geldig-vanaf", "van", optioneel=True)
    geldig_per: dt.date | None = veld("beloningen[i]/geldig-per", "tot", optioneel=True)
    voorwaarden: str | None = veld(
        "beloningen[i]/voorwaarden",
        "Deze salaristabel is van toepassing in de volgende situatie: "
        "(bijvoorbeeld bij werken in een vijf of drie ploegendienst)",
        toon_als="alleen bij de 2e salaristabel en verder (i > 0)",  # niet controleerbaar: hangt af van de rij-index
        optioneel=True,
    )

    # Geldende periodeloon in de schalen
    normale_arbeidsduur: NormaleArbeidsduur | None = veld(
        "beloningen[i]/normale-arbeidsduur",
        "Wat is de normale arbeidsduur per week? Hiermee wordt de arbeidsomvang per week bedoeld (...)", vraagtype="radio",
    )
    normale_arbeidsduur_anders: float | None = veld(
        "beloningen[i]/normale-arbeidsduur-anders-namelijk",
        "Anders, namelijk: (uur)",
        toon_als=Als("normale_arbeidsduur", NormaleArbeidsduur.ANDERS), eenheid="uur",
    )

    # Hoe is de beloning vastgesteld?
    beloning_vastgesteld: BeloningInterval | None = veld(
        "beloningen[i]/beloning-vastgesteld", "Hoe is de beloning vastgesteld?", vraagtype="radio"
    )

    # Uurlonen vastgelegd / eenduidige berekeningsmethodiek?
    uurlonen_vastgelegd: JaNee | None = veld(
        "beloningen[i]/uurlonen-vastgelegd",
        "Zijn in jouw arbeidsvoorwaardenregeling of cao uurlonen voor eigen werknemers vastgelegd of kent (...) "
        "een eenduidige berekeningsmethodiek om het maand-/periodeloon terug te rekenen naar een uurloon?",
        toon_als=_UURLONEN_BLOK, vraagtype="radio",
    )
    uurlonen_percentage: float | None = veld(
        "beloningen[i]/uurlonen-vastgelegd/ja/namelijk",
        "Ja, namelijk: (%)",
        toon_als=En(_UURLONEN_BLOK, Als("uurlonen_vastgelegd", JaNee.JA)), eenheid="%",
    )

    # Welke salarisschalen kent de onderneming?
    salarisschalen: list[Salarisschaal] = veld(
        "beloningen[i]/salarisschalen[j]", "Welke salarisschalen kent de onderneming?", lijst=True
    )

    # Inschaling
    werkervaring_inschaling: WerkervaringInschaling | None = veld(
        "beloningen[i]/werkervaring-inschaling", "Wordt werkervaring bij de inschaling meegenomen?", vraagtype="radio"
    )
    werkervaring_sector: str | None = veld(
        "beloningen[i]/werkervaring-inschaling/ja-sector/namelijk",
        "Relevante werkervaring in de sector wordt als volgt meegenomen: (tekstvak)",
        toon_als=Als("werkervaring_inschaling", WerkervaringInschaling.JA_SECTOR),
    )
    werkervaring_onderneming: str | None = veld(
        "beloningen[i]/werkervaring-inschaling/ja-onderneming/namelijk",
        "Relevante werkervaring bij onze onderneming wordt als volgt meegenomen: (tekstvak)",
        toon_als=Als("werkervaring_inschaling", WerkervaringInschaling.JA_ONDERNEMING),
    )
    werkervaring_functie: str | None = veld(
        "beloningen[i]/werkervaring-inschaling/ja-functie/namelijk",
        "Relevante werkervaring in dezelfde functie (ongeacht de sector) wordt als volgt meegenomen: (tekstvak)",
        toon_als=Als("werkervaring_inschaling", WerkervaringInschaling.JA_FUNCTIE),
    )
    werkervaring_als_volgt: str | None = veld(
        "beloningen[i]/werkervaring-inschaling/ja-als-volgt/namelijk",
        "Ja, namelijk als volgt: (tekstvak)",
        toon_als=Als("werkervaring_inschaling", WerkervaringInschaling.JA_ALS_VOLGT),
    )

    # Periodieken
    periodieke_verhogingen: JaNee | None = veld(
        "beloningen[i]/periodieke-verhogingen", "Zijn er periodieke verhogingen?", vraagtype="radio"
    )
    minimale_duur_dienstverband: PeriodiekeVerhoging | None = veld(
        "beloningen[i]/periodieke-verhogingen-minimale-duur-dienstverband",
        "Ja, deze zijn afhankelijk van een minimale duur dienstverband",
        toon_als=_PERIODIEKEN_BLOK,
    )
    beoordeling_werknemer: PeriodiekeVerhoging | None = veld(
        "beloningen[i]/periodieke-verhogingen-beoordeling-werknemer",
        "Ja, deze zijn afhankelijk van de beoordeling van de werknemer",
        toon_als=_PERIODIEKEN_BLOK,
    )
    periodiek_ja: PeriodiekeVerhoging | None = veld(
        "beloningen[i]/periodieke-verhogingen-ja", "Ja", toon_als=_PERIODIEKEN_BLOK
    )
    andere_verhogingen: PeriodiekeVerhoging | None = veld(
        "beloningen[i]/periodieke-verhogingen-andere-verhogingen",
        "Nee, maar wij geven wel andere verhogingen (niet zijnde initiële / eenmalige verhogingen) (...)",
        toon_als=_PERIODIEKEN_BLOK,
    )

    # Initiële / eenmalige verhogingen
    initiele_eenmalige_verhogingen: JaNee | None = veld(
        "beloningen[i]/initiele-eenmalige-verhogingen", "Zijn er initiële / eenmalige verhogingen bekend?", vraagtype="radio"
    )
    eenmalig_type: EenmaligeVerhogingType | None = veld(
        "beloningen[i]/initiele-eenmalige-verhogingen/ja/type", "Type verhoging", toon_als=_EENMALIG_JA, vraagtype="radio"
    )
    eenmalig_euro: float | None = veld(
        "beloningen[i]/initiele-eenmalige-verhogingen/ja/euro", "Een vast bedrag (€)", toon_als=Als("eenmalig_type", EenmaligeVerhogingType.EURO), eenheid="€"
    )
    eenmalig_percentage: float | None = veld(
        "beloningen[i]/initiele-eenmalige-verhogingen/ja/percentage",
        "Een percentage (%)",
        toon_als=Als("eenmalig_type", EenmaligeVerhogingType.PERCENTAGE), eenheid="%",
    )
    eenmalig_geldig_vanaf: dt.date | None = veld(
        "beloningen[i]/initiele-eenmalige-verhogingen/ja/geldig-vanaf",
        "Ingangsdatum",
        toon_als=_EENMALIG_JA,
        optioneel=True,
    )
    eenmalig_beschrijving: str | None = veld(
        "beloningen[i]/initiele-eenmalige-verhogingen/ja/beschrijving",
        "Voorwaarden voor toekenning",
        toon_als=_EENMALIG_JA,
    )

    # Afwijkende roosters
    afwijkende_arbeidsduur: JaNee | None = veld(
        "beloningen[i]/afwijkende-arbeidsduur",
        "Zijn er werknemers waarvoor een afwijkende arbeidsduur geldt, bijvoorbeeld omdat zij in een "
        "ploegendienst werken of een wisselend arbeidspatroon kennen?", vraagtype="radio",
    )
    afwijkende_roosters: list[AfwijkendRooster] = veld(
        "beloningen[i]/afwijkende-roosters[r]",
        "Namelijk de volgende arbeidsduur:",
        toon_als=_ROOSTERS_BLOK,
        lijst=True,
    )


class Beloning(FormulierModel):
    # Salaristabellen
    beloningen: list[Salaristabel] = veld(
        "beloningen[i]", "Welke salaristabellen kent de onderneming?", lijst=True
    )

    # Betaalde rusttijden en pauzes
    betaalde_rusttijden_en_pauzes: JaNee | None = veld(
        "betaalde-rusttijden-en-pauzes", "Kent jouw onderneming doorbetaalde pauzes of rusttijden?", vraagtype="radio"
    )
    betaalde_rusttijden_namelijk: str | None = veld(
        "betaalde-rusttijden-en-pauzes/ja/namelijk",
        "Ja, namelijk: (tekstvak)",
        toon_als=Als("betaalde_rusttijden_en_pauzes", JaNee.JA),
    )
