"""09 · Verlof (docs/formulier/09_verlof.md).

Acht subsecties, elk een eigen submodel. Het ADV-toekenningsblok (``<p>/toekenning/...``) komt vier keer voor
en de Wazo-regel (``<r>`` + ``<r>/namelijk``) zeven keer; die staan als één veld per item op het submodel.
"""


from pydantic import Field

from ._basis import FormulierModel, Keuze, veld
from .codes import JaNee, Loonbasis
from .voorwaarden import Als


# Keuzelijsten


class AdvToekenningSoort(Keuze):
    TIJD_DAGEN = "tijd-dagen", "In tijd (dagen)"
    TIJD_UREN = "tijd-uren", "In tijd (uren)"
    GELD = "geld", "In geld"


class Tijdvak(Keuze):
    """Keuzelijst "per" (Dag / Week / Maand / Jaar), gebruikt bij ADV-toekenning en vakantiedagen."""

    DAG = "Day", "Dag"
    WEEK = "Week", "Week"
    MAAND = "Month", "Maand"
    JAAR = "Year", "Jaar"


class VakantiedagenType(Keuze):
    DAGEN = "Day", "dagen"
    UREN = "Hour", "uren"


class BijzonderVerlofEenheid(Keuze):
    UUR = "Hour", "Uur"
    DAGEN = "Day", "Dagen"
    WEKEN = "Week", "Weken"
    MAANDEN = "Month", "Maanden"
    JAREN = "Year", "Jaren"


_ADV = Als("adv_regeling", JaNee.JA)
_ADV_AANVULLEND = Als("aanvullende_regeling", JaNee.JA)
_LEEFTIJD = Als("dagen_leeftijd")
_DUUR = Als("dagen_duur_dienstverband")
_ANDERS = Als("dagen_anders")
_BIJZONDER = Als("aanwezig", JaNee.JA)
_WAZO = Als("wazo_aanvulling", JaNee.JA)
_VERPLICHT = Als("verplichte_aanwending", JaNee.JA)
_PERSOONLIJK = Als("persoonlijke_feestdagen", JaNee.JA)
_TIJD_DAGEN = Als("toekenning", AdvToekenningSoort.TIJD_DAGEN)
_TIJD_UREN = Als("toekenning", AdvToekenningSoort.TIJD_UREN)
_GELD = Als("toekenning", AdvToekenningSoort.GELD)
_OUDEREN = Als("ouderen")
_DUUR_DIENSTVERBAND = Als("duur_dienstverband")
_ADV_ANDERS = Als("anders")


# ADV of ATV in tijd of in geld


class AdvToekenning(FormulierModel):
    """ADV-toekenningsblok (makeAdvToegekend), aangeroepen met prefix ``<p>``."""

    toekenning: AdvToekenningSoort | None = veld("<p>/toekenning", "(bloktitel is de vraag)", vraagtype="radio")
    dagen_aantal: float | None = veld(
        "<p>/toekenning/tijd-dagen/aantal", "dagen", toon_als=_TIJD_DAGEN
    )
    dagen_tijdvak: Tijdvak | None = veld(
        "<p>/toekenning/tijd-dagen/tijdvak", "per", toon_als=_TIJD_DAGEN, vraagtype="keuzelijst"
    )
    uren_aantal: float | None = veld("<p>/toekenning/tijd-uren/aantal", "uren", toon_als=_TIJD_UREN)
    uren_tijdvak: Tijdvak | None = veld(
        "<p>/toekenning/tijd-uren/tijdvak", "per", toon_als=_TIJD_UREN, vraagtype="keuzelijst"
    )
    geld_percentage: float | None = veld(
        "<p>/toekenning/geld/percentage", "percentage (%)", toon_als=_GELD, eenheid="%"
    )
    geld_van: Loonbasis | None = veld("<p>/toekenning/geld/van", "van", toon_als=_GELD, vraagtype="keuzelijst")


class AdvAtv(FormulierModel):
    # ADV of ATV in tijd of in geld
    adv_regeling: JaNee | None = veld("adv-regeling", "Is er een betaalde ADV / ATV regeling van toepassing?", vraagtype="radio")
    namelijk: str | None = veld("adv-regeling_ja_namelijk", "(Ja,) namelijk:", toon_als=_ADV)

    # Hoe wordt ADV / ATV toegekend?
    toekenning: AdvToekenning | None = veld("adv-regeling", "Hoe wordt ADV / ATV toegekend?", toon_als=_ADV)

    # Geldt er een aanvullende ADV / ATV regeling voor specifieke werknemers?
    aanvullende_regeling: JaNee | None = veld(
        "adv-aanvullende-regeling",
        "Geldt er een aanvullende ADV / ATV regeling voor specifieke werknemers?",
        toon_als=_ADV, vraagtype="radio",
    )

    # Voor welke werknemers geldt een aanvullende ADV / ATV regeling?
    ouderen: bool | None = veld("adv-aanvullende-ouderen", "Ouderen, namelijk:", toon_als=_ADV_AANVULLEND)
    ouderen_namelijk: str | None = veld(
        "adv-aanvullende-ouderen_namelijk", "(namelijk)", toon_als=_OUDEREN
    )
    duur_dienstverband: bool | None = veld(
        "adv-aanvullende-duur-dienstverband", "Op basis van duur dienstverband, namelijk:", toon_als=_ADV_AANVULLEND
    )
    duur_dienstverband_namelijk: str | None = veld(
        "adv-aanvullende-duur-dienstverband_namelijk",
        "(namelijk)",
        toon_als=_DUUR_DIENSTVERBAND,
    )
    anders: bool | None = veld("adv-aanvullende-anders", "Anders, namelijk:", toon_als=_ADV_AANVULLEND)
    anders_namelijk: str | None = veld(
        "adv-aanvullende-anders-namelijk", "(namelijk)", toon_als=_ADV_ANDERS
    )

    # Aanvullende toekenningsblokken
    toekenning_ouderen: AdvToekenning | None = veld(
        "adv-aanvullende-ouderen",
        "Hoe wordt de aanvullende ADV / ATV voor ouderen toegekend?",
        toon_als=_OUDEREN,
    )
    toekenning_duur_dienstverband: AdvToekenning | None = veld(
        "adv-aanvullende-duur-dienstverband",
        "Hoe wordt de aanvullende ADV / ATV op basis van duur dienstverband toegekend?",
        toon_als=_DUUR_DIENSTVERBAND,
    )
    toekenning_anders: AdvToekenning | None = veld(
        "adv-aanvullende-anders",
        "Hoe wordt de aanvullende ADV / ATV op basis van andere voorwaarden toegekend?",
        toon_als=_ADV_ANDERS,
    )


# Vakantiedagen


class ExtraDagenLeeftijd(FormulierModel):
    leeftijd: int | None = veld("extra-vakantiedagen/leeftijd[i]/leeftijd", "vanaf … jaar oud", eenheid="jaar")
    dagen: float | None = veld("extra-vakantiedagen/leeftijd[i]/dagen", "in totaal … dagen", eenheid="dagen")


class ExtraDagenDuurDienstverband(FormulierModel):
    jaar: int | None = veld("extra-vakantiedagen/duur-dienstverband[i]/jaar", "vanaf … jaar dienstverband", eenheid="jaar")
    dagen: float | None = veld("extra-vakantiedagen/duur-dienstverband[i]/dagen", "in totaal … dagen", eenheid="dagen")


class ExtraDagenAnders(FormulierModel):
    dagen: float | None = veld("extra-vakantiedagen/anders[i]/dagen", "in totaal … dagen", eenheid="dagen")
    namelijk: str | None = veld("extra-vakantiedagen/anders[i]/namelijk", "voor")


class Vakantiedagen(FormulierModel):
    # Hoeveel vakantiedagen worden er toegekend bij een fulltime dienstverband?
    aantal: float | None = veld("vakantiedagen/aantal", "Aantal")
    type: VakantiedagenType | None = veld("vakantiedagen/type", "(dagen / uren)", vraagtype="keuzelijst")
    tijdvak: Tijdvak | None = veld("vakantiedagen/tijdvak", "per:", vraagtype="keuzelijst")

    # Gelden er extra vakantiedagen voor specifieke werknemers of omstandigheden? (blok optioneel)
    dagen_leeftijd: bool | None = veld(
        "extra-vakantiedagen-specifiek/dagen-leeftijd",
        "Ja, extra dagen vanaf een bepaalde leeftijd, namelijk:",
        optioneel=True,
    )
    leeftijd: list[ExtraDagenLeeftijd] = veld(
        "extra-vakantiedagen/leeftijd[i]", "Extra dagen per leeftijd", toon_als=_LEEFTIJD, lijst=True
    )
    dagen_duur_dienstverband: bool | None = veld(
        "extra-vakantiedagen-specifiek/duur-dienstverband",
        "Ja, extra dagen per duur dienstverband, namelijk:",
        optioneel=True,
    )
    duur_dienstverband: list[ExtraDagenDuurDienstverband] = veld(
        "extra-vakantiedagen/duur-dienstverband[i]", "Extra dagen per duur dienstverband", toon_als=_DUUR, lijst=True
    )
    dagen_anders: bool | None = veld("extra-vakantiedagen-specifiek/anders", "Ja, anders, namelijk:", optioneel=True)
    anders: list[ExtraDagenAnders] = veld(
        "extra-vakantiedagen/anders[i]", "Extra dagen anders", toon_als=_ANDERS, lijst=True
    )


# Bijzonder verlof


class BijzonderVerlofVariatie(FormulierModel):
    hoeveel: float | None = veld("bijzonder-verlof[i]/hoeveel", "Hoeveel")
    wat: BijzonderVerlofEenheid | None = veld("bijzonder-verlof[i]/wat", "wat", vraagtype="keuzelijst")
    voorwaarden: str | None = veld("bijzonder-verlof[i]/voorwaarden", "In welk geval")


class BijzonderVerlof(FormulierModel):
    aanwezig: JaNee | None = veld(
        "bijzonder-verlof-aanwezig",
        "Kent jouw onderneming bijzonder verlofregelingen, zoals bijvoorbeeld verlof voor een huwelijk, "
        "bij overlijden familielid, voor mantelzorg etc.", vraagtype="radio",
    )
    variaties: list[BijzonderVerlofVariatie] = veld(
        "bijzonder-verlof[i]", "Variaties bijzonder verlof", toon_als=_BIJZONDER, lijst=True
    )


# Tijd voor tijd


class TijdVoorTijd(FormulierModel):
    tijd_voor_tijd: JaNee | None = veld(
        "tijd-voor-tijd",
        "Ken je een regeling waarin gewerkte uren (bijvoorbeeld meeruren, overuren) niet tot uitkering komen, "
        "maar worden omgezet in tijd?", vraagtype="radio",
    )
    namelijk: str | None = veld("tijd-voor-tijd/ja/namelijk", "(Ja,) namelijk:", toon_als=Als("tijd_voor_tijd", JaNee.JA))


# Aanvulling Wazo


class WazoRegel(FormulierModel):
    """Eén regel uit ``wazoRows``, aangeroepen met slug ``<r>``."""

    aangevinkt: bool | None = veld("<r>", "(checkbox-label uit de lijst)")
    namelijk: str | None = veld("<r>/namelijk", "(namelijk)", toon_als=Als("aangevinkt"))


class AanvullingWazo(FormulierModel):
    wazo_aanvulling: JaNee | None = veld(
        "wazo-aanvulling",
        "Kent jouw onderneming aanvullende regelingen indien de werknemer een Wazo uitkering geniet, (...)", vraagtype="radio",
    )

    # Welke aanvullende regelingen gelden er?
    betaald_ouderschapsverlof: WazoRegel | None = veld(
        "wazo/betaald-ouderschapsverlof", "Een aanvulling op het betaalde ouderschapsverlof van", toon_als=_WAZO
    )
    onbetaald_ouderschapsverlof: WazoRegel | None = veld(
        "wazo/onbetaald-ouderschapsverlof", "Een aanvulling op het onbetaalde ouderschapsverlof van", toon_als=_WAZO
    )
    geboorteverlof: WazoRegel | None = veld(
        "wazo/geboorteverlof", "Een aanvulling op het aanvullend geboorteverlof", toon_als=_WAZO
    )
    kortdurend_zorgverlof: WazoRegel | None = veld(
        "wazo/kortdurend-zorgverlof", "Een aanvulling op het kortdurend zorgverlof", toon_als=_WAZO
    )
    langdurend_zorgverlof: WazoRegel | None = veld(
        "wazo/langdurend-zorgverlof", "Een tegemoetkoming bij langdurend zorgverlof", toon_als=_WAZO
    )
    langere_verlofduur: WazoRegel | None = veld("wazo/langere-verlofduur", "Een langere verlofduur:", toon_als=_WAZO)
    anders: WazoRegel | None = veld("wazo/anders", "Anders, namelijk:", toon_als=_WAZO)


# Verplichte aanwending verlof


class VerplichteAanwending(FormulierModel):
    verplichte_aanwending: JaNee | None = veld(
        "verplichte-aanwending-verlof",
        "Kent jouw onderneming periodes, dagen of uren waarbij sprake is van een bedrijfssluiting waarvoor "
        "de werknemer verplicht verlof moet aanwenden?", vraagtype="radio",
    )
    periode_dagen_uren: str | None = veld(
        "verplichte-aanwending-verlof/ja/periode-dagen-uren",
        "Geef aan voor welke periode/dagen/uren de werknemer verplicht verlof moet aanwenden",
        toon_als=_VERPLICHT,
    )
    welk_verlof: str | None = veld(
        "verplichte-aanwending-verlof_welk-verlof",
        "Welk verlof dient de werknemer te gebruiken voor de hiervoor genoemde verplichte vrije periodes, (...)",
        toon_als=_VERPLICHT,
    )


# Feestdagen


class Feestdagen(FormulierModel):
    aantal: float | None = veld("aantal-feestdagen", "Hoeveel feestdagen kent jouw onderneming?")
    welke: str | None = veld("welke-feestdagen", "Welke feestdagen kent jouw onderneming?")
    voorwaarden: str | None = veld(
        "voorwaarden-feestdagen", "Gelden er voorwaarden voor het genieten van een feestdag?", optioneel=True
    )
    niet_elk_jaar: JaNee | None = veld("feestdagen-niet-elk-jaar", "Ken je feestdagen die niet elk jaar worden toegekend?", vraagtype="radio")
    niet_elk_jaar_voorwaarden: str | None = veld(
        "feestdagen-niet-elk-jaar_voorwaarden",
        "Om welke feestdagen gaat het en wat zijn de voorwaarden voor toekenning?",
        toon_als=Als("niet_elk_jaar", JaNee.JA),
    )

    # Persoonlijke feestdagen
    persoonlijke_feestdagen: JaNee | None = veld("persoonlijke-feestdagen", "Ken je persoonlijke feestdagen?", vraagtype="radio")
    persoonlijk_aantal: float | None = veld(
        "persoonlijke-feestdagen/aantal", "Hoeveel persoonlijke feestdagen kent jouw onderneming?", toon_als=_PERSOONLIJK
    )
    persoonlijk_namelijk: str | None = veld(
        "persoonlijke-feestdagen/namelijk", "Welke persoonlijke feestdagen kent jouw onderneming?", toon_als=_PERSOONLIJK
    )
    persoonlijk_voorwaarden: str | None = veld(
        "persoonlijke-feestdagen/voorwaarden",
        "Welke voorwaarden gelden er voor de persoonlijke feestdagen?",
        toon_als=_PERSOONLIJK,
        optioneel=True,
    )


# Waarde van een (verlof)dag


class WaardeVerlofdag(FormulierModel):
    waarde_verlofdag: JaNee | None = veld(
        "waarde-verlofdag",
        "Kennen jouw arbeidsvoorwaardenregeling(en) en/of cao een regeling om de waarde van een (verlof)dag "
        "te bepalen? (nee = 0,385%)", vraagtype="radio",
    )
    percentage: float | None = veld(
        "waarde-verlofdag_ja_percentage", "(Ja, namelijk) percentage (%)", toon_als=Als("waarde_verlofdag", JaNee.JA), eenheid="%"
    )


class Verlof(FormulierModel):
    adv_atv: AdvAtv = Field(default_factory=AdvAtv)
    vakantiedagen: Vakantiedagen = Field(default_factory=Vakantiedagen)
    bijzonder_verlof: BijzonderVerlof = Field(default_factory=BijzonderVerlof)
    tijd_voor_tijd: TijdVoorTijd = Field(default_factory=TijdVoorTijd)
    aanvulling_wazo: AanvullingWazo = Field(default_factory=AanvullingWazo)
    verplichte_aanwending: VerplichteAanwending = Field(default_factory=VerplichteAanwending)
    feestdagen: Feestdagen = Field(default_factory=Feestdagen)
    waarde_verlofdag: WaardeVerlofdag = Field(default_factory=WaardeVerlofdag)
