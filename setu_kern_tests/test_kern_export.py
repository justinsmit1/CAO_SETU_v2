"""Het uploadbestand voor wijzerbelonen (SETU-JSON + __webform_data__) en het voorbeeldscript."""

import importlib.util
import json
from pathlib import Path

import pytest

from setu_kern.bronnen.wijzerbelonen.formulier import Formulier
from setu_kern.bronnen.wijzerbelonen.formulier.bouwstenen import Bedragregel, BedragSoort, Percentage
from setu_kern.bronnen.wijzerbelonen.formulier.codes import JaNee
from setu_kern.bronnen.wijzerbelonen.formulier.s02_beloning import Salaristabel, WerkervaringInschaling
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu
from setu_kern.bronnen.wijzerbelonen.koppeling.antwoorden import STANDAARD_ANTWOORDEN, naar_antwoorden
from referentie_kern.controle import antwoord_problemen, setu_verschillen, vergelijk_setu

SCRIPT = Path(__file__).parents[1] / "setu_kern_examples" / "maak_upload.py"


def _script():
    spec = importlib.util.spec_from_file_location("maak_upload", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_export_heeft_webform_data_zoals_de_import_verwacht(tmp_path):
    formulier = _script().vul_formulier()
    pad = tmp_path / "upload.json"
    # Het SETU-deel is geldig, op bekende webform-fouten na (die meldt de website zelf ook):
    # - de leeftijd bij extra vakantiedagen is tekst;
    # - de uitkeringsdatum (payDate) is een datum zonder tijd, terwijl het schema date-time eist.
    problemen = naar_setu.schrijf_export(formulier, pad)
    assert problemen
    assert all(("paidLeave" in p and "'age': '" in p) or "/payDate:" in p for p in problemen)
    data = json.loads(pad.read_text(encoding="utf-8"))
    webform_data = data["__webform_data__"]
    assert webform_data["localStorageDataVersion"] == 4  # anders waarschuwt de import
    assert webform_data["appVersion"] == "2.1.0"
    assert set(STANDAARD_ANTWOORDEN) <= set(webform_data["answers"])  # zonder deze lijsten loopt de import vast
    assert data["documentId"]["value"] == "Voorbeeld Bouw 2026"


def test_voorbeeldscript_gelijk_aan_webform(webform):
    antwoorden = naar_antwoorden(_script().vul_formulier())
    assert antwoord_problemen(webform, antwoorden) == []
    assert vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden)) == []


def test_volledig_voorbeeld_gelijk_aan_webform(webform):
    """setu_kern_examples/maak_upload_full.py gebruikt (bijna) elke vraag; ook dan is alles gelijk aan de webform."""
    spec = importlib.util.spec_from_file_location("maak_upload_full", SCRIPT.with_name("maak_upload_full.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    formulier = module.vul_formulier()
    assert formulier.controleer() == []
    antwoorden = naar_antwoorden(formulier)
    assert antwoord_problemen(webform, antwoorden) == []
    assert vergelijk_setu(webform, antwoorden, naar_setu.setu_json(antwoorden)) == []
    assert webform.importeer(naar_setu.export(formulier))["versieWaarschuwing"] is False


def test_upload_wordt_door_de_tool_ingelezen(webform, tmp_path):
    """De importfunctie van de tool leest het bestand zonder waarschuwing en exporteert daarna dezelfde SETU-JSON."""
    pad = tmp_path / "upload.json"
    naar_setu.schrijf_export(_script().vul_formulier(), pad)
    bestand = json.loads(pad.read_text(encoding="utf-8"))
    resultaat = webform.importeer(bestand)
    assert "fout" not in resultaat
    assert resultaat["versieWaarschuwing"] is False
    assert resultaat["antwoorden"] == bestand["__webform_data__"]["answers"]
    ons_setu = {k: v for k, v in bestand.items() if k not in ("issued", "__webform_data__")}
    assert setu_verschillen(resultaat["setu"], ons_setu) == []


def test_kernmodel_van_het_voorbeeld():
    bericht, meldingen = naar_setu.kernmodel(_script().vul_formulier())
    # Alleen rechtgezette webform-fouten: datum zonder tijd en leeftijd als tekst.
    assert meldingen and all("Single.date" in m or ".age: tekst" in m for m in meldingen)
    assert bericht.valideer() == []
    assert bericht.customer.name == "Voorbeeld Bouw B.V."
    assert [s.name for s in bericht.remuneration[0].salary_scale] == ["A", "B"]


def test_kernmodel_ook_bij_onvolledige_webform_setu():
    """Verplichte onderdelen compleet, de rest half: het kernmodel komt er tolerant uit, met meldingen."""
    f = _script().vul_formulier()
    # Overwerk als percentage zonder "van": SETU vereist baseAmount.unitCode, dus deze toeslag is ongeldig.
    f.toeslagen.overwerktoeslag[0].bedrag = Bedragregel(soort=BedragSoort.PERCENTAGE, percentage=Percentage(percentage=125))
    bericht, meldingen = naar_setu.kernmodel(f)
    assert bericht.customer.name == "Voorbeeld Bouw B.V."
    # Alleen de ongeldige bedragregel valt weg; de toeslag zelf blijft staan.
    weggelaten = [m for m in meldingen if "weggelaten" in m]
    assert len(weggelaten) == 1 and weggelaten[0].endswith(".line.0: weggelaten (Field required)")
    # De overige meldingen: de leeftijd bij extra vakantiedagen staat als tekst in de webform-SETU.
    assert all(".age: tekst" in m or "Single.date" in m for m in meldingen if m not in weggelaten)
    overwerk = next(a for a in bericht.allowance if a.name == "Overwerk")
    assert overwerk.line == []
    assert bericht.valideer() == []


def test_kernmodel_noemt_wat_setu_verplicht_stelt():
    f = Formulier()
    f.algemeen.opdrachtgever_naam = "Half B.V."
    with pytest.raises(ValueError) as fout:
        naar_setu.kernmodel(f)
    tekst = str(fout.value)
    assert "Algemeen › Geldig van" in tekst and "Ondertekenen › een contactpersoon met naam" in tekst


def test_export_ook_als_de_setu_omzetting_vastloopt(tmp_path):
    """De webform zelf loopt hier ook vast; de antwoorden (en dus de upload) blijven bruikbaar."""
    f = Formulier()
    f.beloning.beloningen = [Salaristabel(naam="Leeg", werkervaring_inschaling=WerkervaringInschaling.JA_SECTOR)]
    f.vakantiebijslag.ja_nee = JaNee.NEE
    problemen = naar_setu.schrijf_export(f, tmp_path / "upload.json")
    data = json.loads((tmp_path / "upload.json").read_text(encoding="utf-8"))
    assert problemen and "error" in data
    assert data["__webform_data__"]["answers"]["vakantiebijslag/ja-nee"] == "nee"
