"""Lees een download van https://standaard-uitvraag.wijzerbelonen.nl/ in als SETU-kernmodel.

Draaien vanuit de projectmap:

    .venv\\Scripts\\python.exe setu_kern_examples\\lees_export.py pad\\naar\\download.json
    .venv\\Scripts\\python.exe setu_kern_examples\\lees_export.py pad\\naar\\download.json pad\\naar\\kernmodel.json

Een download bevat de SETU-JSON en ``__webform_data__`` (de antwoorden). De adapter gaat uit van de antwoorden, net
als de import van de tool; een bestand met alleen SETU wordt rechtstreeks ingelezen. Het script toont de meldingen
(wat is rechtgezet of weggelaten), een korte samenvatting, en schrijft het kernmodel naar
``uitvoer\\setu_kern\\setu_kernmodel_export.json``.
"""

import sys
from pathlib import Path

from setu_kern_examples.maak_upload import STANDAARD_UITVOER

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from maak_upload import toon_kernmodel, toon_meldingen  # noqa: E402

from setu_kern.bronnen.wijzerbelonen import van_export  # noqa: E402

STANDAARD_UITVOER = PROJECT / "uitvoer" / "setu_kern" / "setu_kernmodel_export_2.json"
STANDAARD_INVOER = r"C:\Users\JustinSmit\Downloads\ingevuld_wijzerbelonen.json"

def main() -> None:
    # if len(sys.argv) < 2:
    #     print(__doc__)
    #     raise SystemExit(1)
    bron = Path(STANDAARD_INVOER)
    uitvoer = Path(sys.argv[2]) if len(sys.argv) > 2 else STANDAARD_UITVOER

    print(f"Inlezen: {bron}")
    try:
        resultaat = van_export(bron)
    except ValueError as fout:
        print(f"  {fout}")
        raise SystemExit(1) from fout
    toon_meldingen(resultaat)

    print("\nSETU-kernmodel (InquiryPayEquity):")
    toon_kernmodel(resultaat.bericht)
    for fout in resultaat.bericht.valideer():
        print(f"    - {fout}")

    uitvoer.parent.mkdir(parents=True, exist_ok=True)
    resultaat.bericht.schrijf(uitvoer, met_extensies=False)
    print(f"\nGeschreven: {uitvoer}")


if __name__ == "__main__":
    main()
