"""Vul het formulier in vanuit een cao met een LLM, en maak (als dat al kan) het SETU-kernmodel.

Draaien vanuit de projectmap:

    # Demo zonder API: nep-LLM met een vast antwoord en een paar vaste cao-fragmenten
    .venv\\Scripts\\python.exe setu_kern_examples\\vul_met_llm.py --nep

    # Echt: eerst de cao indexeren, dan invullen (model: [invullen] model = "..." in config.toml)
    .venv\\Scripts\\python.exe -m setu_kern.bronnen.cao_pdf.pijplijn.cli ingest data\\cao.pdf --index-dir index
    .venv\\Scripts\\python.exe setu_kern_examples\\vul_met_llm.py --index index --parameters organisatie.toml

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
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from setu_kern.bronnen.cao_pdf import IndexZoeker, MistralLLM, Parameters, vul_formulier  # noqa: E402
from setu_kern.bronnen.cao_pdf.llm import GeenModelGekozen  # noqa: E402
from setu_kern.bronnen.cao_pdf.nep import LijstZoeker, NepLLM  # noqa: E402
from setu_kern.bronnen.cao_pdf.zoeken import Fragment  # noqa: E402
from setu_kern.bronnen.wijzerbelonen import van_formulier  # noqa: E402

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
    else:
        try:
            llm = MistralLLM(args.model) if args.model else MistralLLM.uit_config()
        except GeenModelGekozen as fout:
            raise SystemExit(str(fout)) from fout
        zoeker = IndexZoeker.laad(args.index)

    formulier, rapport = vul_formulier(llm, zoeker, parameters, basis=basis)
    UITVOER.mkdir(parents=True, exist_ok=True)
    (UITVOER / "llm_formulier.json").write_text(formulier.model_dump_json(indent=2, exclude_defaults=True), encoding="utf-8")
    rapport.schrijf(UITVOER)
    print(rapport.naar_markdown())
    print(f"Geschreven: {UITVOER / 'llm_formulier.json'} en {UITVOER / 'llm_rapport.md'}")

    try:
        resultaat = van_formulier(formulier)
    except ValueError as fout:
        print(f"\nNog geen kernmodel: {fout}")
        return
    bericht = resultaat.bericht
    for bijslag in bericht.holiday_allowance or []:
        bedrag = bijslag.line[0].amount if bijslag.line else None
        print(f"\nVakantiebijslag in het kernmodel: {bedrag.value if bedrag else '?'} {bedrag.unit_code if bedrag else ''}")
    if not bericht.holiday_allowance:
        print("\nGeen vakantiebijslag in het kernmodel (zie het rapport).")
    print(f"Geldig volgens het officiële schema: {'ja' if not bericht.valideer() else 'nee'}")
    bericht.schrijf(UITVOER / "setu_kernmodel_llm.json", met_extensies=False)
    print(f"Kernmodel geschreven: {UITVOER / 'setu_kernmodel_llm.json'}")


if __name__ == "__main__":
    main()
