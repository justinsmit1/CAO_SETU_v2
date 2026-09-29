"""Vul het formulier in vanuit een cao met een LLM, en maak (als dat al kan) het SETU-kernmodel.

Draaien vanuit de projectmap:

    # Demo zonder API: nep-LLM met een vast antwoord en een paar vaste cao-fragmenten
    .venv\\Scripts\\python.exe setu_kern_examples\\vul_met_llm.py --nep

    # Echt: eerst de cao indexeren, dan invullen (model: [invullen] model = "..." in config.toml)
    .venv\\Scripts\\python.exe -m setu_kern.bronnen.cao_pdf.pijplijn.cli ingest data\\cao.pdf --index-dir index
    .venv\\Scripts\\python.exe setu_kern_examples\\vul_met_llm.py --index index --parameters organisatie.toml

    # Met de SETU-velden die de webform niet kent (geldigheid, uitbetaling, minimum/maximum, naar rato, voorwaarden)
    .venv\\Scripts\\python.exe setu_kern_examples\\vul_met_llm.py --index index --basis-voorbeeld --setu

    # Proef tot in het kernmodel: algemeen, salaristabel en contactpersoon uit het voorbeeld in maak_upload.py,
    # de vakantiebijslag van het LLM
    .venv\\Scripts\\python.exe setu_kern_examples\\vul_met_llm.py --index index --basis-voorbeeld

Schrijft in ``uitvoer\\setu_kern``:
- ``llm_formulier.json``: het ingevulde Formulier (``Formulier.model_validate_json`` leest het weer in);
- ``llm_rapport.md`` / ``.json``: per antwoord artikel, pagina en citaat; wat niet gevonden of weggegooid is;
- ``setu_kernmodel_llm.json``: het kernmodel, zodra de SETU-verplichte onderdelen er zijn (salaristabel!).

Nu vult het LLM alleen 05 Vakantiebijslag in; de andere secties staan in het rapport als "nog niet ondersteund".
"""

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from setu_kern.bronnen.cao_pdf import BLOKKEN, BLOKKEN_SETU, IndexZoeker, MistralLLM, Parameters, vul_formulier  # noqa: E402
from setu_kern.bronnen.cao_pdf.adapter import kern_uit_formulier  # noqa: E402
from setu_kern.bronnen.cao_pdf.llm import GeenModelGekozen  # noqa: E402
from setu_kern.bronnen.cao_pdf.nep import LijstZoeker, NepLLM  # noqa: E402
from setu_kern.bronnen.cao_pdf.zoeken import Fragment  # noqa: E402

UITVOER = PROJECT / "uitvoer" / "setu_kern"

_DEMO_TEKST = "De werknemer ontvangt jaarlijks een vakantiebijslag van 8% van het jaarloon."
_DEMO_ANTWOORD = {
    "waarden": {
        "ja_nee": "ja",
        "bedrag": {
            "soort": "percentage",
            "percentage": {"percentage": 8, "basis": "YearlyRate", "per": "Year", "grondslag": None},
        },
    },
    "onderbouwing": [
        {"pad": "ja_nee", "document": "demo_cao.pdf", "pagina": 14, "artikel": "Artikel 12 lid 1", "citaat": _DEMO_TEKST},
        {"pad": "bedrag", "document": "demo_cao.pdf", "pagina": 14, "artikel": "Artikel 12 lid 1", "citaat": _DEMO_TEKST},
    ],
    "niet_gevonden": [],
}


class LoggendeLLM:
    """Geeft alles door aan ``llm`` en print direct wat er gevraagd en geantwoord wordt (exact zoals verstuurd)."""

    def __init__(self, llm):
        self.llm = llm
        self.gesprek: list[dict] = []

    def vraag_json(self, berichten, schema, naam):
        nummer = len(self.gesprek) + 1
        print()
        print("=" * 100)
        print(f"AANROEP {nummer} - schema '{naam}'")
        print("=" * 100)
        for bericht in berichten:
            print()
            print(f"--- {bericht['role'].upper()} ---")
            print(bericht["content"])
        antwoord = None
        try:
            antwoord = self.llm.vraag_json(berichten, schema, naam)
            return antwoord
        finally:
            print()
            print(f"--- ANTWOORD VAN HET LLM (aanroep {nummer}) ---")
            print(json.dumps(antwoord, indent=2, ensure_ascii=False) if antwoord is not None else "(geen antwoord: fout bij de aanroep)")
            self.gesprek.append({"aanroep": nummer, "schema_naam": naam, "berichten": berichten, "schema": schema, "antwoord": antwoord})



def _demo():
    zoeker = LijstZoeker([Fragment("demo_cao.pdf", 14, "Artikel 12 lid 1 - Vakantiebijslag", _DEMO_TEKST)])
    return NepLLM({"05 Vakantiebijslag": _DEMO_ANTWOORD}), zoeker


def _basis_voorbeeld():
    """Het voorbeeld uit maak_upload.py, maar alleen wat SETU verplicht stelt: algemeen, beloning, ondertekenen.
    De vakantiebijslag blijft leeg; die komt van het LLM."""
    from maak_upload import vul_algemeen, vul_beloning, vul_ondertekenen

    from setu_kern.bronnen.wijzerbelonen.formulier import Formulier

    basis = Formulier()
    for vul in (vul_algemeen, vul_beloning, vul_ondertekenen):
        vul(basis)
    return basis


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nep", action="store_true", help="demo met een nep-LLM (geen API)")
    parser.add_argument("--index", default="index", help="map met de FAISS-index van de cao")
    parser.add_argument("--parameters", help="TOML met gegevens die niet in de cao staan (naam, KvK, ...)")
    parser.add_argument("--model", help="model voor het invullen (anders [invullen] model in config.toml)")
    parser.add_argument("--setu", action="store_true", help="ook de SETU-velden die de webform niet kent (BLOKKEN_SETU)")
    parser.add_argument(
        "--basis-voorbeeld",
        action="store_true",
        help="begin met algemeen, salaristabel en contactpersoon uit maak_upload.py (zodat er een kernmodel komt)",
    )
    args = parser.parse_args()

    parameters = Parameters.lees(args.parameters) if args.parameters else None
    basis = _basis_voorbeeld() if args.basis_voorbeeld else None
    if args.nep:
        llm, zoeker = _demo()
        if args.setu:
            raise SystemExit("--nep werkt alleen met het standaardblok; --setu heeft een echt LLM nodig")
    else:
        try:
            llm = MistralLLM(args.model) if args.model else MistralLLM.uit_config()
        except GeenModelGekozen as fout:
            raise SystemExit(str(fout)) from fout
        zoeker = IndexZoeker.laad(args.index)

    blokken = BLOKKEN_SETU if args.setu else BLOKKEN
    llm = LoggendeLLM(llm)
    UITVOER.mkdir(parents=True, exist_ok=True)
    try:
        formulier, rapport = vul_formulier(llm, zoeker, parameters, blokken, basis=basis)
    finally:  # ook bij een fout van de API blijft het gesprek bewaard
        (UITVOER / "llm_gesprek.json").write_text(json.dumps(llm.gesprek, indent=2, ensure_ascii=False), encoding="utf-8")
        print()
        print(f"Gesprek (met het volledige JSON-schema) geschreven: {UITVOER / 'llm_gesprek.json'}")
    print()
    print("=" * 100)
    print("RAPPORT")
    print("=" * 100)
    (UITVOER / "llm_formulier.json").write_text(formulier.model_dump_json(indent=2, exclude_defaults=True), encoding="utf-8")
    rapport.schrijf(UITVOER)
    print(rapport.naar_markdown())
    print(f"Geschreven: {UITVOER / 'llm_formulier.json'} en {UITVOER / 'llm_rapport.md'}")

    try:
        resultaat = kern_uit_formulier(formulier, rapport, blokken)
    except ValueError as fout:
        print(f"\nNog geen kernmodel: {fout}")
        return
    bericht = resultaat.bericht
    for bijslag in bericht.holiday_allowance or []:
        bedrag = bijslag.line[0].amount if bijslag.line else None
        print(f"\nVakantiebijslag in het kernmodel: {bedrag.value if bedrag else '?'} {bedrag.unit_code if bedrag else ''}")
    if not bericht.holiday_allowance:
        print("\nGeen vakantiebijslag in het kernmodel (zie het rapport).")
    for m in resultaat.meldingen:
        if m.startswith("vakantiebijslag:"):
            print(f"Melding: {m}")
    print(f"Geldig volgens het officiële schema: {'ja' if not bericht.valideer() else 'nee'}")
    bericht.schrijf(UITVOER / "setu_kernmodel_llm.json", met_extensies=False)
    print(f"Kernmodel geschreven: {UITVOER / 'setu_kernmodel_llm.json'}")


if __name__ == "__main__":
    main()
