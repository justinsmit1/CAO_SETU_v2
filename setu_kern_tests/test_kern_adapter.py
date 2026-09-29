"""De wijzerbelonen-adapter: Formulier en download komen via hetzelfde contract (Resultaat) in de kern."""

import importlib.util
import json
from pathlib import Path

from setu_kern import InquiryPayEquity, Resultaat
from setu_kern.bronnen.wijzerbelonen import (
    BRON_EXPORT,
    BRON_FORMULIER,
    BRON_SETU,
    schrijf_upload,
    van_export,
    van_formulier,
)
from setu_kern.bronnen.wijzerbelonen.adapter import STANDAARD_CONTACTPERSOON, STANDAARD_REFERENTIEDATUM
from setu_kern.bronnen.wijzerbelonen.formulier.s09_verlof import ExtraDagenDuurDienstverband
from setu_kern.bronnen.wijzerbelonen.koppeling import naar_setu

SCRIPT = Path(__file__).parents[1] / "setu_kern_examples" / "maak_upload.py"


def _voorbeeld():
    spec = importlib.util.spec_from_file_location("maak_upload_kern", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.vul_formulier()


def _zonder_issued(bericht: InquiryPayEquity) -> dict:
    data = bericht.naar_dict(met_extensies=False)
    data.pop("issued", None)
    return data


def test_van_formulier():
    resultaat = van_formulier(_voorbeeld())
    assert isinstance(resultaat, Resultaat)
    assert resultaat.bron == BRON_FORMULIER
    assert resultaat.geldig
    assert resultaat.bericht.customer.name == "Voorbeeld Bouw B.V."
    # Alleen rechtgezette webform-fouten: datum zonder tijd en leeftijd als tekst (zie test_kern_export).
    assert resultaat.meldingen and all("Single.date" in m or ".age: tekst" in m for m in resultaat.meldingen)


def test_download_geeft_hetzelfde_bericht_als_het_formulier(tmp_path):
    formulier = _voorbeeld()
    pad = tmp_path / "download.json"
    schrijf_upload(formulier, pad)
    uit_export = van_export(pad)
    uit_formulier = van_formulier(formulier)
    assert uit_export.bron == BRON_EXPORT
    assert uit_export.meldingen == uit_formulier.meldingen  # geen versiemeldingen: de export is v2.1.0 / versie 4
    assert _zonder_issued(uit_export.bericht) == _zonder_issued(uit_formulier.bericht)


def test_download_na_import_in_de_echte_tool(webform):
    """Wat de tool na importeren als antwoorden bewaart, geeft via de adapter hetzelfde bericht."""
    formulier = _voorbeeld()
    export = naar_setu.export(formulier)
    antwoorden = webform.importeer(export)["antwoorden"]
    download = {**export, "__webform_data__": {**export["__webform_data__"], "answers": antwoorden}}
    assert _zonder_issued(van_export(download).bericht) == _zonder_issued(van_formulier(formulier).bericht)


def test_bestand_met_alleen_setu(tmp_path):
    export = naar_setu.export(_voorbeeld())
    alleen_setu = {k: v for k, v in export.items() if k != "__webform_data__"}
    pad = tmp_path / "setu.json"
    pad.write_text(json.dumps(alleen_setu), encoding="utf-8")
    resultaat = van_export(pad)
    assert resultaat.bron == BRON_SETU
    assert resultaat.meldingen[0].startswith("geen __webform_data__")
    assert resultaat.geldig
    assert resultaat.bericht.customer.name == "Voorbeeld Bouw B.V."


def test_zonder_contactpersoon_wordt_john_doe_ingevuld():
    f = _voorbeeld()
    f.ondertekenen.contactpersonen = []
    resultaat = van_formulier(f)
    assert resultaat.geldig
    assert [c.name.formatted_name for c in resultaat.bericht.customer.person_contacts] == [STANDAARD_CONTACTPERSOON]
    assert any("geen contactpersoon" in m for m in resultaat.meldingen)
    # Hetzelfde via een download.
    contact = van_export(naar_setu.export(f)).bericht.customer.person_contacts[0]
    assert contact.name.formatted_name == STANDAARD_CONTACTPERSOON


def test_duur_dienstverband_wordt_hersteld():
    """De webform laat duration en referenceDateType weg; de adapter vult ze aan in plaats van de conditie te verliezen."""
    f = _voorbeeld()
    f.verlof.vakantiedagen.dagen_duur_dienstverband = True
    f.verlof.vakantiedagen.duur_dienstverband = [
        ExtraDagenDuurDienstverband(jaar=10, dagen=1),
        ExtraDagenDuurDienstverband(jaar=20, dagen=2),
    ]
    resultaat = van_formulier(f)
    assert resultaat.geldig
    assert not any("weggelaten" in m for m in resultaat.meldingen)
    condities = [
        c
        for verlof in resultaat.bericht.leave
        for regel in verlof.paid_leave or []
        for c in regel.conditions or []
        if c.condition_type == "EmploymentDuration"
    ]
    assert [(c.duration, c.reference_date_type) for c in condities] == [
        ("P10Y", STANDAARD_REFERENTIEDATUM),
        ("P20Y", STANDAARD_REFERENTIEDATUM),
    ]
    assert sum("aangenomen" in m for m in resultaat.meldingen) == 2


def test_afwijkende_versie_geeft_een_melding():
    export = naar_setu.export(_voorbeeld())
    export["__webform_data__"]["localStorageDataVersion"] = 3
    export["__webform_data__"]["appVersion"] = "2.0.0"
    meldingen = van_export(export).meldingen
    assert any("localStorageDataVersion is 3" in m for m in meldingen)
    assert any("webform-versie '2.0.0'" in m for m in meldingen)
