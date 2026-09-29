"""01 · Algemeen (docs/formulier/01_algemeen.md)."""

import datetime as dt

from ._basis import FormulierModel, Keuze, veld
from .voorwaarden import Als


class TypeIdentificatienummer(Keuze):
    KVK = "KvK"
    OIN = "OIN"
    RSIN = "RSIN"


class CaoOfRegeling(Keuze):
    CAO = "cao-van-toepassing", "Er is een cao van toepassing"
    EIGEN_REGELING = "eigen-arbeidsvoorwaardenregeling", "Er is of zijn (een) eigen arbeidsvoorwaardenregeling(en) van toepassing"
    CAO_EN_EIGEN_REGELING = "cao-en-eigen-arbeidsvoorwaardenregeling", "Er is een cao van toepassing en wij hebben (een) eigen arbeidsvoorwaardenregeling(en)"
    GEEN = "geen-cao-of-arbeidsvoorwaardenregeling", "Er is geen cao of arbeidsvoorwaardenregeling van toepassing"


class CaoVanToepassingOmdat(Keuze):
    LID_BRANCHEORGANISATIE = "lid-brancheorganisatie", "Je onderneming is lid van de brancheorganisatie"
    ALGEMEEN_VERBINDEND = "algemeen-verbindend", "De cao is algemeen verbindend verklaard"
    IN_ARBEIDSOVEREENKOMST = "in-arbeidsovereenkomst", "De cao wordt van toepassing verklaard in de arbeidsovereenkomst van de werknemers"


_TOON_CAO = Als("cao_of_regeling", CaoOfRegeling.CAO, CaoOfRegeling.CAO_EN_EIGEN_REGELING)
_TOON_AVV = Als("cao_van_toepassing_omdat", CaoVanToepassingOmdat.ALGEMEEN_VERBINDEND)


class Algemeen(FormulierModel):
    # Arbeidsvoorwaardenregeling en toepassingsperiode
    naam_regeling: str | None = veld("id", "Geef je arbeidsvoorwaardenregeling een naam of nummer:")
    geldig_van: dt.date | None = veld("toepassingsperiode-van", "Geldig van")
    geldig_tot: dt.date | None = veld("toepassingsperiode-tot", "tot", optioneel=True)

    # Opdrachtgever
    opdrachtgever_naam: str | None = veld("opdrachtgever-naam", "Naam onderneming(en) / organisatie(s):")
    opdrachtgever_kvk: str | None = veld(
        "opdrachtgever-kvk",
        "Bijbehorende KvK of een ander identificatienummer van de onderneming(en) / organisatie(s) "
        "waarvoor dit uitvraagformulier geldt:",
    )
    opdrachtgever_kvk_type: TypeIdentificatienummer | None = veld("opdrachtgever-kvk-type", "Type identificatienummer", vraagtype="keuzelijst")
    sector: str | None = veld("sector", "In welke sector ben je actief?")

    # Hoe zijn de arbeidsvoorwaarden voor jouw eigen werknemers geregeld?
    cao_of_regeling: CaoOfRegeling | None = veld(
        "cao-of-regeling", "Hoe zijn de arbeidsvoorwaarden voor jouw eigen werknemers geregeld?", vraagtype="radio"
    )

    # Welke cao is van toepassing?
    cao_naam: str | None = veld("cao-naam", "Naam cao:", toon_als=_TOON_CAO)
    cao_nummer: str | None = veld("cao-nummer", "Nummer cao:", toon_als=_TOON_CAO)
    cao_van_toepassing_omdat: CaoVanToepassingOmdat | None = veld(
        "cao-van-toepassing-omdat", "Wat geldt er binnen jouw onderneming?", toon_als=_TOON_CAO, vraagtype="radio"
    )
    cao_van: dt.date | None = veld("cao-van", "van", toon_als=_TOON_AVV)
    cao_tot: dt.date | None = veld("cao-tot", "tot", toon_als=_TOON_AVV)
