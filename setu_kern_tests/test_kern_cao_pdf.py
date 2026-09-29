"""Het LLM-raamwerk (bron cao_pdf), getest met een nep-LLM: geen API-aanroepen."""

import datetime as dt
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator

from setu_kern.bronnen.cao_pdf import BLOKKEN, Blok, Fragment, MistralLLM, Parameters, van_cao_pdf, vul_formulier
from setu_kern.bronnen.cao_pdf.invullen.omzetten import naar_waarden, van_waarden
from setu_kern.bronnen.cao_pdf.invullen.schema import antwoord_schema, blok_schema
from setu_kern.bronnen.cao_pdf.llm import GeenModelGekozen, invul_model
from setu_kern.bronnen.cao_pdf.nep import LijstZoeker, NepLLM
from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage
from setu_kern.bronnen.wijzerbelonen.formulier.codes import Interval, JaNee, Loonbasis
from setu_kern.bronnen.wijzerbelonen.formulier.s02_beloning import (
    Beloning,
    BeloningInterval,
    NormaleArbeidsduur,
    Salarisschaal,
    Salaristabel,
    Stap,
)
from setu_kern.bronnen.wijzerbelonen.formulier.s05_vakantiebijslag import Vakantiebijslag

VAKANTIEBIJSLAG = "05 Vakantiebijslag"
CAO_TEKST = "De werknemer ontvangt jaarlijks een vakantiebijslag van 8% van het jaarloon."
SALARIS_TEKST = "Bijlage 1 Salaristabel bij een arbeidsduur van 40 uur per week, per maand: schaal A trede 0 € 2.450."
FRAGMENTEN = [
    Fragment("cao_test.pdf", 14, "Hoofdstuk 4 > Artikel 12 lid 1 - Vakantiebijslag", CAO_TEKST),
    Fragment("cao_test.pdf", 40, "Bijlage 1", SALARIS_TEKST),
    Fragment("cao_test.pdf", 3, "Artikel 2 - Werkingssfeer", "Deze cao geldt voor alle werknemers in de sector."),
]
BELONING = Blok("02 Beloning (test)", "beloning", velden=("beloningen",), zoektermen=("salaristabel schaal trede",))


def _onderbouwing(pad: str, citaat: str = CAO_TEKST, pagina: int = 14) -> dict:
    return {"pad": pad, "document": "cao_test.pdf", "pagina": pagina, "artikel": "Artikel 12 lid 1", "citaat": citaat}


def _antwoord(instantie, model, velden=None, onderbouwing=(), niet_gevonden=()) -> dict:
    """Een antwoord zoals het LLM het volgens het schema geeft."""
    return {
        "waarden": naar_waarden(instantie, model, velden),
        "onderbouwing": list(onderbouwing),
        "niet_gevonden": list(niet_gevonden),
    }


def _vakantiebijslag(ja_nee=JaNee.JA, percentage=8) -> Vakantiebijslag:
    bedrag = None
    if percentage is not None:
        bedrag = Bedragregel(
            soort=BedragSoort.PERCENTAGE,
            percentage=Percentage(percentage=percentage, basis=Loonbasis.JAARLOON, per=Interval.JAAR),
        )
    return Vakantiebijslag.model_construct(ja_nee=ja_nee, bedrag=bedrag)  # ook ongeldige combinaties, voor de tests


GOED = _antwoord(_vakantiebijslag(), Vakantiebijslag, onderbouwing=[_onderbouwing("ja_nee"), _onderbouwing("bedrag")])


def _vul(antwoorden, blokken=BLOKKEN, parameters=None):
    llm = NepLLM(antwoorden, blokken)
    formulier, rapport = vul_formulier(llm, LijstZoeker(FRAGMENTEN), parameters, blokken)
    return formulier, rapport, llm


# --- schema en omzetting
def _strikt(schema: dict) -> list[str]:
    """Objecten zonder additionalProperties: false of met velden die niet required zijn."""
    fouten = []
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            if schema.get("additionalProperties") is not False:
                fouten.append("additionalProperties")
            if set(schema.get("required", [])) != set(schema.get("properties", {})):
                fouten.append(f"required: {sorted(schema.get('properties', {}))}")
        for w in schema.values():
            fouten += _strikt(w)
    elif isinstance(schema, list):
        for w in schema:
            fouten += _strikt(w)
    return fouten


def test_schema_en_omzetting_voor_elke_sectie():
    """Elk sectieschema is geldig en strikt, en het volledige voorbeeld gaat er zonder verlies heen en terug."""
    pad = Path(__file__).parents[1] / "setu_kern_examples" / "maak_upload_full.py"
    spec = importlib.util.spec_from_file_location("maak_upload_full_llm", pad)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    formulier = module.vul_formulier()
    for naam, info in Formulier.model_fields.items():
        model = info.annotation
        schema = antwoord_schema(blok_schema(model))
        Draft202012Validator.check_schema(schema)
        assert _strikt(schema) == [], naam
        data = json.loads(json.dumps(_antwoord(getattr(formulier, naam), model)))
        assert list(Draft202012Validator(schema).iter_errors(data)) == [], naam
        assert model.model_validate(van_waarden(model, data["waarden"])) == getattr(formulier, naam), naam


def test_schema_van_de_vakantiebijslag_kent_alleen_een_percentage():
    bedrag = blok_schema(Vakantiebijslag)["properties"]["bedrag"]["anyOf"][0]
    assert bedrag["properties"]["soort"]["enum"] == ["percentage", None]
    assert set(bedrag["properties"]) == {"soort", "percentage"}


# --- invullen
def test_vakantiebijslag_met_citaat():
    formulier, rapport, llm = _vul({VAKANTIEBIJSLAG: GOED})
    vb = formulier.vakantiebijslag
    assert vb.ja_nee == JaNee.JA
    assert vb.bedrag.percentage.percentage == 8 and vb.bedrag.percentage.basis == Loonbasis.JAARLOON
    verslag = rapport.blokken[0]
    assert verslag.aanroepen == 1 and verslag.weggegooid == [] and verslag.niet_gevonden == []
    assert {i.pad for i in verslag.ingevuld} >= {"ja_nee", "bedrag.soort", "bedrag.percentage.percentage"}
    assert all(i.onderbouwing.pagina == 14 for i in verslag.ingevuld)
    # Het LLM kreeg de vraag en het gevonden fragment te zien, met het strikte schema.
    naam, berichten, schema = llm.aanroepen[0]
    assert naam == BLOKKEN[0].schema_naam
    assert "Is er een vakantiebijslag?" in berichten[1]["content"] and CAO_TEKST in berichten[1]["content"]
    assert "Hoeveel bedraagt de vakantiebijslag?" in json.dumps(schema, ensure_ascii=False)
    assert CAO_TEKST in rapport.naar_markdown()


def test_niet_gevonden_is_geen_nee():
    formulier, rapport, _ = _vul({})  # de nep-LLM geeft een leeg antwoord
    assert formulier.vakantiebijslag.ja_nee is None
    assert "ja_nee" in rapport.blokken[0].niet_gevonden
    assert any("ja_nee niet gevonden" in m for m in rapport.meldingen())


def test_waarde_zonder_onderbouwing_wordt_weggegooid():
    antwoord = _antwoord(_vakantiebijslag(), Vakantiebijslag, onderbouwing=[_onderbouwing("ja_nee")])
    formulier, rapport, _ = _vul({VAKANTIEBIJSLAG: antwoord})
    assert formulier.vakantiebijslag.ja_nee == JaNee.JA
    assert formulier.vakantiebijslag.bedrag is None
    weg = dict(rapport.blokken[0].weggegooid)
    assert "bedrag.percentage.percentage" in weg and "geen onderbouwing" in weg["bedrag.percentage.percentage"]


def test_verzonnen_citaat_telt_niet():
    antwoord = _antwoord(
        _vakantiebijslag(), Vakantiebijslag, onderbouwing=[_onderbouwing("", citaat="De vakantiebijslag is 10%.")]
    )
    antwoord["onderbouwing"][0]["pad"] = "ja_nee"
    formulier, rapport, _ = _vul({VAKANTIEBIJSLAG: antwoord})
    assert formulier.vakantiebijslag.ja_nee is None and formulier.vakantiebijslag.bedrag is None
    assert any("citaat staat niet in de fragmenten" in r for _, r in rapport.blokken[0].weggegooid)


def test_herkansing_na_een_ongeldig_antwoord():
    """Bedrag ingevuld terwijl ja_nee = nee: het model weigert; het LLM krijgt de fout terug en verbetert."""
    fout = _antwoord(_vakantiebijslag(JaNee.NEE), Vakantiebijslag, onderbouwing=[_onderbouwing("ja_nee"), _onderbouwing("bedrag")])
    formulier, rapport, llm = _vul({VAKANTIEBIJSLAG: [fout, GOED]})
    assert len(llm.aanroepen) == 2 and rapport.blokken[0].aanroepen == 2
    herstel = llm.aanroepen[1][1][-1]["content"]
    assert "voldoet niet aan de vragenlijst" in herstel and "mag alleen ingevuld worden" in herstel
    assert formulier.vakantiebijslag.ja_nee == JaNee.JA and formulier.vakantiebijslag.bedrag.percentage.percentage == 8
    assert any("herkansing" in m for m in rapport.blokken[0].meldingen)


def test_na_de_herkansing_worden_foute_velden_weggegooid():
    fout = _antwoord(_vakantiebijslag(JaNee.NEE), Vakantiebijslag, onderbouwing=[_onderbouwing("ja_nee"), _onderbouwing("bedrag")])
    formulier, rapport, _ = _vul({VAKANTIEBIJSLAG: [fout, fout]})
    assert formulier.vakantiebijslag.ja_nee == JaNee.NEE
    assert formulier.vakantiebijslag.bedrag is None
    assert any(p == "bedrag" and "voldoet niet aan het formulier" in r for p, r in rapport.blokken[0].weggegooid)
    assert not any(i.pad.startswith("bedrag") for i in rapport.blokken[0].ingevuld)


def test_antwoord_buiten_het_schema_geeft_een_herkansing():
    formulier, rapport, llm = _vul({VAKANTIEBIJSLAG: [{"waarden": {"ja_nee": "misschien"}}, GOED]})
    assert len(llm.aanroepen) == 2
    assert formulier.vakantiebijslag.ja_nee == JaNee.JA


def test_onbekende_secties_staan_in_het_rapport():
    _, rapport, _ = _vul({VAKANTIEBIJSLAG: GOED})
    assert "vakantiebijslag" not in rapport.niet_ondersteund and "toeslagen" in rapport.niet_ondersteund
    assert "algemeen" not in rapport.niet_ondersteund  # komt uit de parameters


# --- naar de kern
PARAMETERS = Parameters(
    naam_regeling="Test 2026",
    geldig_van=dt.date(2026, 1, 1),
    opdrachtgever_naam="Test B.V.",
    opdrachtgever_kvk="12345678",
    opdrachtgever_kvk_type="kvk",
)


def _salarissen() -> dict:
    beloning = Beloning(
        beloningen=[
            Salaristabel(
                naam="Salaristabel 2026",
                normale_arbeidsduur=NormaleArbeidsduur.UUR_40,
                beloning_vastgesteld=BeloningInterval.PER_MAAND,
                salarisschalen=[Salarisschaal(naam="A", stappen=[Stap(naam="0", bedrag=2450)])],
            )
        ]
    )
    return _antwoord(beloning, Beloning, ("beloningen",), [_onderbouwing("beloningen", SALARIS_TEKST, 40)])


def test_van_cao_pdf_naar_de_kern():
    blokken = (*BLOKKEN, BELONING)
    llm = NepLLM({VAKANTIEBIJSLAG: GOED, BELONING.naam: _salarissen()}, blokken)
    resultaat = van_cao_pdf(llm, LijstZoeker(FRAGMENTEN), PARAMETERS, blokken)
    assert resultaat.bron == "cao_pdf" and resultaat.geldig
    assert resultaat.bericht.customer.name == "Test B.V."
    assert resultaat.bericht.holiday_allowance[0].line[0].amount.value == 8
    assert [s.name for s in resultaat.bericht.remuneration[0].salary_scale] == ["A"]
    assert any("nog niet ondersteund" in m for m in resultaat.meldingen)
    assert any("'John Doe' ingevuld" in m for m in resultaat.meldingen)  # geen contactpersoon in de parameters


def test_zonder_salaristabel_kan_er_geen_kernmodel_zijn():
    with pytest.raises(ValueError, match="Beloning"):
        van_cao_pdf(NepLLM({VAKANTIEBIJSLAG: GOED}), LijstZoeker(FRAGMENTEN), PARAMETERS)


def _basis() -> Formulier:
    """Een basisformulier met alleen de salaristabel (de rest komt uit PARAMETERS en het LLM)."""
    basis = Formulier()
    basis.beloning = Beloning(
        beloningen=[
            Salaristabel(
                naam="Salaristabel 2026",
                normale_arbeidsduur=NormaleArbeidsduur.UUR_40,
                beloning_vastgesteld=BeloningInterval.PER_MAAND,
                salarisschalen=[Salarisschaal(naam="A", stappen=[Stap(naam="0", bedrag=2450)])],
            )
        ]
    )
    return basis


def test_basisformulier_plus_llm_naar_de_kern():
    basis = _basis()
    voor = basis.model_dump()
    resultaat = van_cao_pdf(NepLLM({VAKANTIEBIJSLAG: GOED}), LijstZoeker(FRAGMENTEN), PARAMETERS, basis=basis)
    assert resultaat.geldig
    assert resultaat.bericht.holiday_allowance[0].line[0].amount.value == 8  # van het LLM
    assert [s.name for s in resultaat.bericht.remuneration[0].salary_scale] == ["A"]  # uit de basis
    assert "sectie beloning: uit het basisformulier, niet uit de cao" in resultaat.meldingen
    assert not any("sectie beloning: nog niet ondersteund" in m for m in resultaat.meldingen)
    assert basis.model_dump() == voor  # de basis zelf is niet gewijzigd


def test_een_blok_overschrijft_de_basis():
    basis = _basis()
    basis.vakantiebijslag = Vakantiebijslag(ja_nee=JaNee.NEE)
    formulier, rapport = vul_formulier(NepLLM({VAKANTIEBIJSLAG: GOED}), LijstZoeker(FRAGMENTEN), basis=basis)
    assert formulier.vakantiebijslag.ja_nee == JaNee.JA
    assert "vakantiebijslag" not in rapport.uit_basis and basis.vakantiebijslag.ja_nee == JaNee.NEE


def test_parameters_uit_toml(tmp_path):
    pad = tmp_path / "organisatie.toml"
    pad.write_text('opdrachtgever_naam = "Test B.V."\ngeldig_van = 2026-01-01\ncontactpersonen = ["J. Jansen"]\n', encoding="utf-8")
    parameters = Parameters.lees(pad)
    formulier, rapport, _ = _vul({}, parameters=parameters)
    assert formulier.algemeen.opdrachtgever_naam == "Test B.V." and formulier.algemeen.geldig_van == dt.date(2026, 1, 1)
    assert formulier.ondertekenen.contactpersonen[0].naam == "J. Jansen"
    assert {i.pad for i in rapport.uit_parameters} >= {"algemeen.opdrachtgever_naam", "ondertekenen.contactpersonen[0].naam"}


# --- het echte LLM (zonder aanroep)
def test_er_is_nog_geen_model_gekozen(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('[defaults]\nmodel = "open-mistral-7b"\n', encoding="utf-8")
    with pytest.raises(GeenModelGekozen):
        invul_model(config)
    config.write_text('[invullen]\nmodel = "een-model"\n', encoding="utf-8")
    assert invul_model(config) == "een-model"


def test_mistral_llm_vraagt_een_strikt_schema():
    verzonden = {}

    def complete(**kwargs):
        verzonden.update(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(GOED)))])

    client = SimpleNamespace(chat=SimpleNamespace(complete=complete))
    formulier, _ = vul_formulier(MistralLLM("een-model", client=client), LijstZoeker(FRAGMENTEN))
    assert verzonden["model"] == "een-model"
    assert verzonden["response_format"]["type"] == "json_schema"
    assert verzonden["response_format"]["json_schema"]["strict"] is True
    assert formulier.vakantiebijslag.ja_nee == JaNee.JA
