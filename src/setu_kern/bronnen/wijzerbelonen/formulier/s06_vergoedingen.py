"""06 · Vergoedingen (docs/formulier/06_vergoedingen.md).

Zeven subsecties, elk een eigen submodel: reiskosten, reisuren, stand-by, zorgverzekering, thuiswerk,
mobiliteit en kosten. Herhaalbaar zijn alleen de twee "eigen vervoer"-blokken (variaties ``<p>[i]``);
OV-blokken, mobiliteitsregelingen en kostenvergoedingen zijn vaste items met elk een eigen veld.
"""


from pydantic import Field

from ._basis import FormulierModel, Keuze, veld
from .codes import Interval, JaNee, Loonbasis
from .voorwaarden import Als, Niet

# ---------------------------------------------------------------------------
# Keuzelijsten (tijdvakken): deelverzamelingen van B2 Interval, per vraag verschillend
# ---------------------------------------------------------------------------


class Tijdvak(Keuze):
    """Standaard tijdvak-keuzelijst van deze sectie."""

    UUR = "Hour", "Uur"
    DAG = "Day", "Dag"
    DAGDEEL = "DayPart", "Dagdeel"
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    JAAR = "Year", "Jaar"


class TijdvakReisuren(Keuze):
    """Tijdvak bij de vaste reisurenvergoeding."""

    KILOMETER = "Kilometer", "Kilometer"
    ROUTE = "Route", "Route"
    UUR = "Hour", "Uur"
    DAG = "Day", "Dag"
    DAGDEEL = "DayPart", "Dagdeel"
    MAAND = "Month", "Maand"
    WEEK = "Week", "Week"
    JAAR = "Year", "Jaar"


class TijdvakStandBy(Keuze):
    """Tijdvak bij de stand-byvergoeding."""

    UUR = "Hour", "Uur"
    DAG = "Day", "Dag"
    DAGDEEL = "DayPart", "Dagdeel"
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    JAAR = "Year", "Jaar"
    DIENST = "Shift", "Dienst"


class TijdvakKosten(Keuze):
    """Tijdvak bij de kostenvergoedingen."""

    ITEM = "Item", "Item"
    UUR = "Hour", "Uur"
    DAG = "Day", "Dag"
    DAGDEEL = "DayPart", "Dagdeel"
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    JAAR = "Year", "Jaar"


# ---------------------------------------------------------------------------
# Keuzelijsten (soort vergoeding)
# ---------------------------------------------------------------------------


class EigenVervoerType(Keuze):
    STANDAARD_TARIEF = "standaard-tarief", "€ 0,23 per kilometer"
    ANDER_TARIEF_PER_KM = "ander-tarief-per-km", "Andere vergoeding per kilometer"
    PER_TIJDVAK = "per-tijdvak", "Vergoeding per tijdvak"
    ANDERS = "anders", "Anders, namelijk:"


class OvType(Keuze):
    VOLLEDIGE_VERGOEDING = "volledige-vergoeding", "Volledige vergoeding van de gemaakte kosten"
    PER_KILOMETER = "per-kilometer", "Vergoeding per kilometer, namelijk:"
    PER_RIT = "per-rit", "Vergoeding per rit, namelijk:"
    PER_TRAJECT = "per-traject", "Vergoeding per traject, namelijk:"
    ANDERS = "anders", "Anders, namelijk:"


class ReistijdVergoeding(Keuze):
    PERCENTAGE = "percentage", "Ja, namelijk percentage van"
    VASTE_VERGOEDING = "vaste-vergoeding", "Ja, namelijk een vaste vergoeding van"
    ANDERS = "anders", "Ja, namelijk:"
    NEE = "nee", "Nee"


class StandByType(Keuze):
    VERGOEDING_PER_TIJDVAK = "vergoeding-per-tijdvak", "Vaste vergoeding per tijdvak, namelijk:"
    PERCENTAGE_PER_TIJDVAK = "percentage-per-tijdvak", "Percentage per tijdvak, namelijk:"
    ANDERS = "anders", "Anders, namelijk:"


class ZorgverzekeringType(Keuze):
    VERGOEDING_PER_TIJDSEENHEID = "vergoeding-per-tijdseenheid", "Vergoeding per tijdseenheid, namelijk:"
    ANDERS = "anders", "Anders, namelijk:"


# ---------------------------------------------------------------------------
# Reiskostenvergoedingen
# ---------------------------------------------------------------------------

_WELKE = "welke-reiskostenvergoedingen-kent-jouw-onderneming"


class EigenVervoerVariatie(FormulierModel):
    """Eén variatie van een eigen-vervoerblok (``<p>`` = reiskostenvergoeding-eigen-vervoer / -zakelijke-kilometers).

    Let op: behalve ``type`` beginnen de sleutels in de webform met een slash (``[<p>, i, "/voorwaarden"]``);
    vandaar ``<p>[i]//…`` (scheidingsteken + de voorloop-slash van de sleutel).
    """

    type: EigenVervoerType | None = veld("<p>[i]/type", "(bloktitel is de vraag)", vraagtype="radio")
    ander_tarief_per_km_bedrag: float | None = veld(
        "<p>[i]//ander-tarief-per-km/bedrag", "namelijk … per kilometer (€)", toon_als=Als("type", EigenVervoerType.ANDER_TARIEF_PER_KM), eenheid="€"
    )
    per_tijdvak_bedrag: float | None = veld(
        "<p>[i]//per-tijdvak/bedrag", "namelijk (€)", toon_als=Als("type", EigenVervoerType.PER_TIJDVAK), eenheid="€"
    )
    per_tijdvak_type: Tijdvak | None = veld("<p>[i]//per-tijdvak/type", "per", toon_als=Als("type", EigenVervoerType.PER_TIJDVAK), vraagtype="keuzelijst")
    anders_namelijk: str | None = veld("<p>[i]//anders/namelijk", "Anders, namelijk:", toon_als=Als("type", EigenVervoerType.ANDERS))
    voorwaarden: str | None = veld("<p>[i]//voorwaarden", "Voor deze vergoeding gelden de volgende voorwaarden:")


class OvVergoeding(FormulierModel):
    """Een OV-blok (``<p>`` = reiskostenvergoeding-ov / reiskostenvergoeding-zakelijke-kilometers-ov)."""

    type: OvType | None = veld("<p>-type", "(bloktitel is de vraag)", vraagtype="radio")
    per_kilometer_bedrag: float | None = veld(
        "<p>-type/per-kilometer/bedrag", "Bedrag per kilometer (€)", toon_als=Als("type", OvType.PER_KILOMETER), eenheid="€"
    )
    per_rit_bedrag: float | None = veld("<p>-type/per-rit/bedrag", "Bedrag per rit (€)", toon_als=Als("type", OvType.PER_RIT), eenheid="€")
    per_traject_bedrag: float | None = veld(
        "<p>-type/per-traject/bedrag", "Bedrag per traject (€)", toon_als=Als("type", OvType.PER_TRAJECT), eenheid="€"
    )
    anders_namelijk: str | None = veld("<p>-type/anders/namelijk", "Anders, namelijk:", toon_als=Als("type", OvType.ANDERS))
    voorwaarden: str | None = veld("<p>-voorwaarden", "Voor deze vergoeding gelden de volgende voorwaarden:")


class Reiskosten(FormulierModel):
    # Welke reiskostenvergoeding(en) kent jouw onderneming? (meerdere opties mogelijk)
    kent_eigen_vervoer: bool | None = veld(
        f"{_WELKE}/eigen-vervoer", "Reiskostenvergoeding woon- werk verkeer eigen auto / fiets etc."
    )
    kent_ov: bool | None = veld(f"{_WELKE}/ov", "Reiskostenvergoeding woon- werk verkeer OV")
    kent_zakelijke_kilometers: bool | None = veld(
        f"{_WELKE}/zakelijke-kilometers", "Reiskostenvergoeding zakelijke kilometers (werk – werk)"
    )
    kent_zakelijke_kilometers_ov: bool | None = veld(
        f"{_WELKE}/zakelijke-kilometers-ov", "Reiskostenvergoeding zakelijke kilometers OV (werk – werk)"
    )
    kent_andere: bool | None = veld(f"{_WELKE}/andere-reiskostenvergoeding", "Andere reiskostenvergoeding")

    # Eigen vervoer woon-werk (variaties)
    eigen_vervoer: list[EigenVervoerVariatie] = veld(
        "reiskostenvergoeding-eigen-vervoer[i]",
        "Reiskostenvergoeding woon- werk verkeer eigen auto / fiets / bromfiets / anders.",
        toon_als=Als("kent_eigen_vervoer"),
        lijst=True,
    )

    # OV woon-werk
    ov: OvVergoeding | None = veld(
        "reiskostenvergoeding-ov",
        "Reiskostenvergoeding woon- werk verkeer OV",
        toon_als=Als("kent_ov"),
    )

    # Eigen vervoer werk-werk (variaties)
    zakelijke_kilometers: list[EigenVervoerVariatie] = veld(
        "reiskostenvergoeding-zakelijke-kilometers[i]",
        "Reiskostenvergoeding zakelijke kilometers (werk – werk) eigen vervoer",
        toon_als=Als("kent_zakelijke_kilometers"),
        lijst=True,
    )

    # OV werk-werk
    zakelijke_kilometers_ov: OvVergoeding | None = veld(
        "reiskostenvergoeding-zakelijke-kilometers-ov",
        "Reiskostenvergoeding werk-werk verkeer OV",
        toon_als=Als("kent_zakelijke_kilometers_ov"),
    )

    # Andere reiskostenvergoeding
    andere_namelijk: str | None = veld(
        "andere-reiskostenvergoeding-namelijk",
        "Andere reiskostenvergoedingen, namelijk:",
        toon_als=Als("kent_andere"),
    )


# ---------------------------------------------------------------------------
# Vergoeding voor reisuren en -tijd
# ---------------------------------------------------------------------------

_REISTIJD_PCT = Als("vergoeding", ReistijdVergoeding.PERCENTAGE)
_REISTIJD_VAST = Als("vergoeding", ReistijdVergoeding.VASTE_VERGOEDING)


class Reisuren(FormulierModel):
    vergoeding: ReistijdVergoeding | None = veld(
        "vergoeding-reistijd", "Ken je een vergoeding voor reisuren of reistijd?", vraagtype="radio"
    )
    percentage: float | None = veld("vergoeding-reistijd/percentage/percentage", "Percentage (%)", toon_als=_REISTIJD_PCT, eenheid="%")
    percentage_van: Loonbasis | None = veld("vergoeding-reistijd/percentage/van", "van", toon_als=_REISTIJD_PCT, vraagtype="keuzelijst")
    percentage_tijdvak: Tijdvak | None = veld("vergoeding-reistijd/percentage/tijdvak", "per", toon_als=_REISTIJD_PCT, vraagtype="keuzelijst")
    vaste_vergoeding_bedrag: float | None = veld(
        "vergoeding-reistijd/vaste-vergoeding/value", "Bedrag (€)", toon_als=_REISTIJD_VAST, eenheid="€"
    )
    vaste_vergoeding_per: TijdvakReisuren | None = veld(
        "vergoeding-reistijd/vaste-vergoeding/per", "per", toon_als=_REISTIJD_VAST, vraagtype="keuzelijst"
    )
    anders_namelijk: str | None = veld(
        "vergoeding-reistijd/anders/namelijk", "Ja, namelijk:", toon_als=Als("vergoeding", ReistijdVergoeding.ANDERS)
    )

    # Voorwaarden
    voorwaarden: str | None = veld(
        "vergoeding-reistijd_voorwaarden",
        "Voor deze vergoeding gelden de volgende voorwaarden:",
        toon_als=Niet(Als("vergoeding", ReistijdVergoeding.NEE)),
    )


# ---------------------------------------------------------------------------
# Vergoeding voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten
# ---------------------------------------------------------------------------

_STANDBY = Als("ja_nee", JaNee.JA)
_STANDBY_VAST = Als("type", StandByType.VERGOEDING_PER_TIJDVAK)
_STANDBY_PCT = Als("type", StandByType.PERCENTAGE_PER_TIJDVAK)


class StandBy(FormulierModel):
    ja_nee: JaNee | None = veld(
        "vergoeding-stand-by-piket-consignatie-bereikbaarheidsdiensten",
        "Kent je een vergoeding voor de tijd die de werknemer stand-by of bereikbaar moet zijn?", vraagtype="radio",
    )

    # Welke vergoeding kent jouw onderneming voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten?
    type: StandByType | None = veld(
        "type-vergoeding-stand-by",
        "Welke vergoeding kent jouw onderneming voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten?",
        toon_als=_STANDBY, vraagtype="radio",
    )
    vast_bedrag: float | None = veld(
        "type-vergoeding-stand-by/vergoeding-per-tijdvak/bedrag", "Bedrag (€)", toon_als=_STANDBY_VAST, eenheid="€"
    )
    vast_tijdvak: TijdvakStandBy | None = veld(
        "type-vergoeding-stand-by/vergoeding-per-tijdvak/tijdvak", "per", toon_als=_STANDBY_VAST, vraagtype="keuzelijst"
    )
    percentage: float | None = veld(
        "type-vergoeding-stand-by/percentage-per-tijdvak/percentage", "Percentage (%)", toon_als=_STANDBY_PCT, eenheid="%"
    )
    percentage_van: Loonbasis | None = veld(
        "type-vergoeding-stand-by/percentage-per-tijdvak/van", "van:", toon_als=_STANDBY_PCT, vraagtype="keuzelijst"
    )
    percentage_tijdvak: TijdvakStandBy | None = veld(
        "type-vergoeding-stand-by/percentage-per-tijdvak/tijdvak", "per", toon_als=_STANDBY_PCT, vraagtype="keuzelijst"
    )
    anders_namelijk: str | None = veld(
        "type-vergoeding-stand-by/anders/namelijk", "Anders, namelijk:", toon_als=Als("type", StandByType.ANDERS)
    )

    # Voorwaarden
    voorwaarden: str | None = veld(
        "voorwaarden-vergoeding-stand-by", "Voor deze vergoeding gelden de volgende voorwaarden:", toon_als=_STANDBY
    )


# ---------------------------------------------------------------------------
# Vergoeding voor de (aanvullende) zorgverzekering
# ---------------------------------------------------------------------------

_ZORG_PER_TIJD = Als("type", ZorgverzekeringType.VERGOEDING_PER_TIJDSEENHEID)
_ZORG_MIN_MAX = Als("min_max", JaNee.JA)


class Zorgverzekering(FormulierModel):
    ja_nee: JaNee | None = veld(
        "vergoeding-zorgverzekering", "Ken je een vergoeding voor de (aanvullende) zorgverzekering?", vraagtype="radio"
    )

    # Hoe ziet deze vergoeding eruit?
    type: ZorgverzekeringType | None = veld(
        "vergoeding-zorgverzekering-type", "Hoe ziet deze vergoeding eruit?", toon_als=Als("ja_nee", JaNee.JA), vraagtype="radio"
    )
    bedrag: float | None = veld(
        "vergoeding-zorgverzekering-type/vergoeding-per-tijdseenheid/bedrag", "Bedrag (€)", toon_als=_ZORG_PER_TIJD, eenheid="€"
    )
    tijdvak: Tijdvak | None = veld(
        "vergoeding-zorgverzekering-type/vergoeding-per-tijdseenheid/tijdvak", "per", toon_als=_ZORG_PER_TIJD, vraagtype="keuzelijst"
    )
    anders_namelijk: str | None = veld(
        "vergoeding-zorgverzekering-type/anders/namelijk",
        "Anders, namelijk:",
        toon_als=Als("type", ZorgverzekeringType.ANDERS),
    )

    # Minimum/maximum, naar rato en voorwaarden
    min_max: JaNee | None = veld(
        "vergoeding-zorgverzekering-min-max",
        "Geldt er een minimum- of een maximumbedrag voor de vergoeding?",
        toon_als=_ZORG_PER_TIJD, vraagtype="radio",
    )
    minimum: float | None = veld(
        "vergoeding-zorgverzekering-min-max/ja/minimum", "Minimum (€)", toon_als=_ZORG_MIN_MAX, optioneel=True, eenheid="€"
    )
    maximum: float | None = veld(
        "vergoeding-zorgverzekering-min-max/ja/maximum", "Maximum (€)", toon_als=_ZORG_MIN_MAX, optioneel=True, eenheid="€"
    )
    naar_rato: JaNee | None = veld(
        "vergoeding-zorgverzekering-naar-rato",
        "Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?",
        toon_als=_ZORG_PER_TIJD, vraagtype="radio",
    )
    voorwaarden: str | None = veld(
        "vergoeding-zorgverzekering-voorwaarden",
        "Voor deze vergoeding gelden verder de volgende voorwaarden:",
        toon_als=_ZORG_PER_TIJD,
    )


# ---------------------------------------------------------------------------
# Thuiswerkvergoedingen
# ---------------------------------------------------------------------------

_THUIS = Als("ja_nee", JaNee.JA)
_INTERNET = Als("extra_internet", JaNee.JA)


class Thuiswerk(FormulierModel):
    ja_nee: JaNee | None = veld("thuiswerkvergoeding", "Ken je een thuiswerkvergoeding?", vraagtype="radio")

    # Vergoeding per tijdseenheid, namelijk:
    bedrag: float | None = veld("thuiswerkvergoeding/ja/vergoeding-tijdseenheid", "Bedrag (€)", toon_als=_THUIS, eenheid="€")
    tijdvak: Tijdvak | None = veld("thuiswerkvergoeding/ja/tijdvak", "per", toon_als=_THUIS, vraagtype="keuzelijst")
    voorwaarden: str | None = veld(
        "thuiswerkvergoeding/ja/voorwaarden",
        "Voor deze vergoeding gelden de volgende voorwaarden:",
        toon_als=_THUIS,
        optioneel=True,
    )
    naar_rato: JaNee | None = veld(
        "thuiswerkvergoeding/ja/naar-rato",
        "Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?",
        toon_als=_THUIS, vraagtype="radio",
    )
    internet_inbegrepen: JaNee | None = veld(
        "thuiswerkvergoeding/ja/internetvergoeding-inbegrepen",
        "Zit er een internetvergoeding besloten in de thuiswerkvergoeding?",
        toon_als=_THUIS, vraagtype="radio",
    )
    extra_internet: JaNee | None = veld(
        "thuiswerkvergoeding/ja/extra-internetvergoeding",
        "Wordt er naast de thuiswerkvergoeding ook (aanvullend) een internetvergoeding verstrekt?",
        toon_als=Als("internet_inbegrepen", JaNee.NEE), vraagtype="radio",
    )

    # Aanvullende internetvergoeding
    internet_bedrag: float | None = veld(
        "thuiswerkvergoeding/ja/extra-internetvergoeding/ja/vergoeding-tijdseenheid", "Bedrag (€)", toon_als=_INTERNET, eenheid="€"
    )
    internet_tijdvak: Tijdvak | None = veld(
        "thuiswerkvergoeding/ja/extra-internetvergoeding/ja/tijdvak", "tijdvak", toon_als=_INTERNET, vraagtype="keuzelijst"
    )
    internet_voorwaarden: str | None = veld(
        "thuiswerkvergoeding/ja/extra-internetvergoeding/ja/voorwaarden",
        "Voor deze vergoeding gelden verder de volgende voorwaarden:",
        toon_als=_INTERNET,
    )
    internet_naar_rato: JaNee | None = veld(
        "thuiswerkvergoeding/ja/extra-internetvergoeding/ja/naar-rato",
        "Wordt de internetvergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur (...)",
        toon_als=_INTERNET, vraagtype="radio",
    )


# ---------------------------------------------------------------------------
# Mobiliteitsvergoeding
# ---------------------------------------------------------------------------

_REGELING = Als("aangevinkt")
_ALTERNATIEF = Als("alternatief")


class MobiliteitsRegeling(FormulierModel):
    """Vragenset per mobiliteitsregeling (``<r>`` = slug van de regeling)."""

    aangevinkt: bool | None = veld("mobiliteit/<r>", "<label> (aangevinkt = regeling van toepassing)")
    bedrag: float | None = veld(
        "mobiliteit/<r>/bedrag", "Wat is de hoogte van de vergoeding / het leasebedrag? (€)", toon_als=_REGELING, eenheid="€"
    )
    tijdvak: Interval | None = veld("mobiliteit/<r>/tijdvak", "Per tijdvak", toon_als=_REGELING, vraagtype="keuzelijst")
    voorwaarden: str | None = veld(
        "mobiliteit/<r>/voorwaarden",
        "Voor deze regeling gelden de volgende voorwaarden:",
        toon_als=_REGELING,
        optioneel=True,
    )
    naar_rato: JaNee | None = veld(
        "mobiliteit/<r>/naar-rato",
        "Wordt de vergoeding naar rato uitgekeerd wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?",
        toon_als=_REGELING, vraagtype="radio",
    )


class MobiliteitsRegelingMetAlternatief(MobiliteitsRegeling):
    """Regeling met een mogelijke alternatieve vergoeding (leaseauto, leasefiets, OV-vergoeding)."""

    alternatief: bool | None = veld(
        "mobiliteit/<r>/alternatief", "Er is een alternatieve vergoeding voor <label>", toon_als=_REGELING
    )
    alternatief_bedrag: float | None = veld("mobiliteit/<r>/alternatief/bedrag", "Bedrag (€)", toon_als=_ALTERNATIEF, eenheid="€")
    alternatief_tijdvak: Interval | None = veld(
        "mobiliteit/<r>/alternatief/tijdvak", "per tijdvak van", toon_als=_ALTERNATIEF, vraagtype="keuzelijst"
    )
    alternatief_voorwaarden: str | None = veld(
        "mobiliteit/<r>/alternatief/voorwaarden",
        "Voor deze vergoeding gelden de volgende voorwaarden:",
        toon_als=_ALTERNATIEF,
        optioneel=True,
    )
    alternatief_naar_rato: JaNee | None = veld(
        "mobiliteit/<r>/alternatief/naar-rato",
        "Wordt de vergoeding naar rato uitgekeerd wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?",
        toon_als=_ALTERNATIEF, vraagtype="radio",
    )


class Mobiliteit(FormulierModel):
    # Ken je een mobiliteitsregeling, bijvoorbeeld een regeling voor een leaseauto of -fiets of OV, (...)?
    mobiliteitsvergoeding: MobiliteitsRegeling | None = veld("mobiliteit/mobiliteitsvergoeding", "Mobiliteitsvergoeding")
    regeling_leaseauto: MobiliteitsRegelingMetAlternatief | None = veld(
        "mobiliteit/regeling-leaseauto", "Regeling leaseauto"
    )
    regeling_leasefiets: MobiliteitsRegelingMetAlternatief | None = veld(
        "mobiliteit/regeling-leasefiets", "Regeling leasefiets"
    )
    regeling_ov_vergoeding: MobiliteitsRegelingMetAlternatief | None = veld(
        "mobiliteit/regeling-ov-vergoeding", "Regeling OV vergoeding"
    )
    fietsregeling: MobiliteitsRegeling | None = veld("mobiliteit/fietsregeling", "Fietsregeling")


# ---------------------------------------------------------------------------
# Kostenvergoedingen
# ---------------------------------------------------------------------------

_KOSTEN = Als("aangevinkt")


class KostenVergoeding(FormulierModel):
    """Vragenset per kostenvergoeding (``<k>`` = kostenvergoedingen/<slug>)."""

    aangevinkt: bool | None = veld("<k>", "<label> (aangevinkt = vergoeding van toepassing)")
    bedrag: float | None = veld("<k>/per-tijdvak/bedrag", "Bedrag (€)", toon_als=_KOSTEN, eenheid="€")
    tijdvak: TijdvakKosten | None = veld("<k>/tijdvak", "per", toon_als=_KOSTEN, vraagtype="keuzelijst")
    voorwaarden: str | None = veld(
        "<k>/voorwaarden", "Voor deze vergoeding gelden de volgende voorwaarden:", toon_als=_KOSTEN, optioneel=True
    )
    naar_rato: JaNee | None = veld(
        "<k>/naar-rato",
        "Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt?",
        toon_als=_KOSTEN, vraagtype="radio",
    )


class Kosten(FormulierModel):
    # Welke kostenvergoedingen ken je verder? (meerdere opties mogelijk)
    koffiegeld: KostenVergoeding | None = veld("kostenvergoedingen/koffiegeld", "Koffiegeld")
    maaltijdvergoeding: KostenVergoeding | None = veld("kostenvergoedingen/maaltijdvergoeding", "Maaltijdvergoeding")
    wasvergoeding: KostenVergoeding | None = veld("kostenvergoedingen/wasvergoeding", "Wasvergoeding")
    bedrijfskleding_schoenen: KostenVergoeding | None = veld(
        "kostenvergoedingen/vergoeding-bedrijfskleding-schoenen", "Vergoeding voor bedrijfskleding of schoenen"
    )
    arbo_vergoeding: KostenVergoeding | None = veld("kostenvergoedingen/arbo-vergoeding", "Arbo-vergoeding")
    byod_vergoeding: KostenVergoeding | None = veld(
        "kostenvergoedingen/byod-vergoeding", "BYOD (Bring Your Own Device) vergoeding"
    )
    anders: bool | None = veld("kostenvergoedingen/anders", "Anders, namelijk:")
    anders_namelijk: str | None = veld(
        "kostenvergoedingen/anders/namelijk", "(namelijk)", toon_als=Als("anders")
    )
    geen: bool | None = veld("kostenvergoedingen/geen", "Geen (wist de zes vergoedingen hierboven)")


# ---------------------------------------------------------------------------
# Sectie
# ---------------------------------------------------------------------------


class Vergoedingen(FormulierModel):
    reiskosten: Reiskosten = Field(default_factory=Reiskosten)
    reisuren: Reisuren = Field(default_factory=Reisuren)
    stand_by: StandBy = Field(default_factory=StandBy)
    zorgverzekering: Zorgverzekering = Field(default_factory=Zorgverzekering)
    thuiswerk: Thuiswerk = Field(default_factory=Thuiswerk)
    mobiliteit: Mobiliteit = Field(default_factory=Mobiliteit)
    kosten: Kosten = Field(default_factory=Kosten)
