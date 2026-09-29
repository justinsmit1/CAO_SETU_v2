import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier, Vraagtype, vragen  # noqa: E402
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage, Tijd, VastBedrag  # noqa: E402
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Interval, JaNee, Loonbasis  # noqa: E402
from setu_kern.bronnen.wijzerbelonen.formulier.s01_algemeen import CaoOfRegeling  # noqa: E402
from setu_kern.bronnen.wijzerbelonen.formulier.s13_aanvullende_regelingen import AanvullendeRegelingMetDekking  # noqa: E402


def test_leeg_formulier_json_roundtrip():
    f = Formulier()
    assert Formulier.model_validate_json(f.model_dump_json()) == f


def test_enum_heeft_waarde_en_label():
    assert CaoOfRegeling.CAO == "cao-van-toepassing"
    assert CaoOfRegeling.CAO.label == "Er is een cao van toepassing"
    assert CaoOfRegeling("cao-van-toepassing") is CaoOfRegeling.CAO


def test_onbekende_optie_geweigerd():
    f = Formulier()
    with pytest.raises(ValidationError):
        f.algemeen.cao_of_regeling = "bestaat-niet"


def test_vakantiebijslag_alleen_percentage():
    f = Formulier()
    f.vakantiebijslag.ja_nee = JaNee.JA
    f.vakantiebijslag.bedrag = Bedragregel(soort=BedragSoort.PERCENTAGE, percentage=Percentage(percentage=8))
    with pytest.raises(ValidationError, match="niet toegestaan"):
        f.vakantiebijslag.bedrag = Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=500))


def test_bedragregel_alleen_gekozen_deel():
    with pytest.raises(ValidationError, match="Bedragregel.tijd mag alleen ingevuld worden als soort = tijd"):
        Bedragregel(soort=BedragSoort.PERCENTAGE, tijd=Tijd(uur=4))


def test_dekkingswaarde_zonder_per():
    AanvullendeRegelingMetDekking(ja_nee=JaNee.JA, dekkingswaarde=Bedragregel(soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=1)))
    with pytest.raises(ValidationError, match="geen 'per'"):
        AanvullendeRegelingMetDekking(
            ja_nee=JaNee.JA,
            dekkingswaarde=Bedragregel(
                soort=BedragSoort.VAST_BEDRAG, vast_bedrag=VastBedrag(bedrag=1, per=Interval.MAAND)
            )
        )


def test_cao_naam_pas_na_keuze_cao():
    f = Formulier()
    with pytest.raises(ValidationError, match="mag alleen ingevuld worden als cao_of_regeling"):
        f.algemeen.cao_naam = "Cao Bouw"
    assert f.algemeen.cao_naam is None

    f.algemeen.cao_of_regeling = CaoOfRegeling.CAO_EN_EIGEN_REGELING
    f.algemeen.cao_naam = "Cao Bouw"
    assert f.algemeen.cao_naam == "Cao Bouw"


def test_geweigerde_wijziging_laat_oude_waarde_staan():
    f = Formulier()
    f.algemeen.cao_of_regeling = CaoOfRegeling.CAO
    f.algemeen.cao_naam = "Cao Bouw"
    with pytest.raises(ValidationError):
        f.algemeen.cao_of_regeling = CaoOfRegeling.GEEN  # cao_naam zou dan verborgen zijn
    assert f.algemeen.cao_of_regeling == CaoOfRegeling.CAO
    assert f.controleer() == []


def test_inlezen_met_verborgen_veld_geweigerd():
    with pytest.raises(ValidationError):
        Formulier.model_validate({"algemeen": {"cao_of_regeling": "geen-cao-of-arbeidsvoorwaardenregeling", "cao_naam": "X"}})


def test_vragen_overzicht():
    alle = {v.pad: v for v in vragen(Formulier)}
    assert alle["algemeen.opdrachtgever_kvk_type"].vraagtype == Vraagtype.KEUZELIJST
    assert alle["algemeen.cao_of_regeling"].vraagtype == Vraagtype.RADIO
    assert alle["algemeen.cao_naam"].vraagtype == Vraagtype.TEKST
    vb = alle["vakantiebijslag.bedrag"]
    assert vb.vraagtype == Vraagtype.BEDRAGREGEL
    assert vb.opties == [("percentage", "Percentage van loon")]
    assert alle["vakantiebijslag.bedrag.percentage.percentage"].eenheid == "%"
    assert ("MonthlyRate", "Maandloon") in alle["vakantiebijslag.bedrag.percentage.basis"].opties
    assert Loonbasis.MAANDLOON.label == "Maandloon"

