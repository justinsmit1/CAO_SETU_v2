"""Gap-analyse: SETU-standaard (Excel) tegenover het kernmodel en de Wijzerbelonen-webform.

Draaien vanuit de projectmap:

    .venv\\Scripts\\python.exe tools\\gap_analyse.py [pad\\naar\\SETU-Inquiry-Pay-Equity.xlsx]

Schrijft ``docs/gap_analyse_setu.md``.

- Norm: elk elementpad uit de Excel (SETU Inquiry Pay Equity 2.1).
- Kern: het pad staat in het JSON-schema waar het kernmodel conform aan is (``setu/schema``).
- Wijzerbelonen: het pad komt voor in de SETU-uitvoer van het VOLLEDIGE voorbeeld (``examples/maak_upload_full.py``),
  met de omzetting die tegen de echte webform is getest. Paden zonder array-indices.

De Excel is een overzicht: een paar delen (o.a. ``conditions`` en ``occurrence``) vouwt hij niet uit. Een pad dat in
het schema staat maar niet in de Excel, telt hier dus niet mee.
"""

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "examples"))

STANDAARD_EXCEL = Path.home() / "Downloads" / "SETU-Inquiry-Pay-Equity-v2-1-InquiryPayEquity (6).xlsx"
SCHEMA = PROJECT / "src" / "cao_setu_v2" / "setu" / "schema" / "inquiry_pay_equity_2.0.0_draft.json"
RAPPORT = PROJECT / "docs" / "gap_analyse_setu.md"
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Terugkerende velden: dezelfde gaten komen in bijna elke regeling voor. Sleutel = laatste padonderdeel(en).
FAMILIES = {
    "id/description": ("id", "description"),
    "effectivePeriod": ("effectivePeriod", "validFrom", "validTo"),
    "payDate / occurrence": ("payDate", "occurrence", "occurrenceType", "recurringInterval", "offset", "event", "eventName", "date"),
    "lineId": ("lineId",),
    "min/maxValue": ("minValue", "maxValue"),
    "proportional": ("proportional", "partTimePercentage", "employmentDuration"),
    "conditions": ("conditions",),
    "contributionSource": ("contributionSource",),
    "ikbReference": ("ikbReference", "relationType"),
    "origin": ("origin", "type"),
}


def lees_excel(pad: Path) -> list[dict]:
    """Alle elementen als ``{pad, mult, type, definitie}``; pad zonder het hoofdelement."""
    z = zipfile.ZipFile(pad)
    strings = [
        "".join(t.text or "" for t in si.iter(M + "t"))
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M + "si")
    ]
    rijen = []
    for row in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(M + "row"):
        cel = {}
        for c in row.findall(M + "c"):
            v = c.find(M + "v")
            if v is not None:
                cel[re.match("[A-Z]+", c.get("r")).group()] = strings[int(v.text)] if c.get("t") == "s" else v.text
        rijen.append(cel)
    uit, stapel = [], []
    for r in rijen[2:]:  # rij 1 = kopjes, rij 2 = hoofdelement
        m = re.match(r"((?:\|--)+)\s*(.+)", r.get("B", ""))
        if not m:
            continue
        diepte = m.group(1).count("|--")
        naam = r.get("C") or m.group(2).strip()
        stapel = stapel[: diepte - 1] + [naam]
        uit.append({"pad": "/".join(stapel), "mult": r.get("A", ""), "type": r.get("D", ""), "definitie": r.get("F", "")})
    return uit


def schema_paden() -> set[str]:
    s = json.loads(SCHEMA.read_text(encoding="utf-8"))
    defs = s["definitions"]
    uit: set[str] = set()

    def loop(node: dict, pad: str, gezien: tuple[str, ...]) -> None:
        if "$ref" in node:
            naam = node["$ref"].split("/")[-1]
            if naam in gezien:
                return
            node, gezien = defs[naam], gezien + (naam,)
        for k in ("oneOf", "anyOf", "allOf"):
            for sub in node.get(k, []):
                loop(sub, pad, gezien)
        if node.get("type") == "array" and "items" in node:
            loop(node["items"], pad, gezien)
        for k, v in node.get("properties", {}).items():
            p = f"{pad}/{k}" if pad else k
            uit.add(p)
            loop(v, p, gezien)

    loop(s, "", ())
    return uit


def uitvoer_paden(data, pad: str = "") -> set[str]:
    uit: set[str] = set()
    if isinstance(data, dict):
        for k, v in data.items():
            p = f"{pad}/{k}" if pad else k
            uit.add(p)
            uit |= uitvoer_paden(v, p)
    elif isinstance(data, list):
        for v in data:
            uit |= uitvoer_paden(v, pad)
    return uit


def wijzerbelonen_paden() -> set[str]:
    from maak_upload_full import vul_formulier

    from cao_setu_v2.koppeling.wijzerbelonen import naar_setu

    return uitvoer_paden(naar_setu.setu_json(vul_formulier()))


def familie(pad: str) -> str:
    delen = pad.split("/")
    for naam, sleutels in FAMILIES.items():
        if any(d in sleutels for d in delen[1:]):
            return naam
    return "regelingspecifiek"


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "-"


def schrijf(excel: Path) -> None:
    elementen = lees_excel(excel)
    kern, wb = schema_paden(), wijzerbelonen_paden()
    for e in elementen:
        e["kern"], e["wb"] = e["pad"] in kern, e["pad"] in wb
        e["sectie"] = e["pad"].split("/")[0]
        e["verplicht"] = e["mult"].startswith("1")

    r: list[str] = ["# Gap-analyse: SETU-standaard tegenover kern en Wijzerbelonen", ""]
    r += [
        f"*Bron: `{excel.name}` ({len(elementen)} elementpaden). Gemaakt met `tools/gap_analyse.py`.*",
        "",
        "- **Kern**: het pad staat in het schema waar het kernmodel conform aan is.",
        "- **Wijzerbelonen**: het pad komt voor in de SETU-uitvoer van het volledige voorbeeld "
        "(`examples/maak_upload_full.py`).",
        "",
    ]

    nk = sum(e["kern"] for e in elementen)
    nw = sum(e["wb"] for e in elementen)
    r += [
        "## Samenvatting",
        "",
        f"Van de {len(elementen)} elementen dekt de kern er {nk} ({pct(nk, len(elementen))}) "
        f"en vult Wijzerbelonen er {nw} ({pct(nw, len(elementen))}).",
        "",
        "| Sectie | Elementen | Kern | Wijzerbelonen | Ontbreekt bij Wijzerbelonen | Waarvan verplicht (1..x) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    per_sectie: dict[str, list[dict]] = defaultdict(list)
    for e in elementen:
        per_sectie[e["sectie"]].append(e)
    for s, es in per_sectie.items():
        mis = [e for e in es if not e["wb"]]
        r.append(
            f"| `{s}` | {len(es)} | {sum(e['kern'] for e in es)} | {sum(e['wb'] for e in es)} "
            f"| {len(mis)} | {sum(e['verplicht'] for e in mis)} |"
        )
    r.append("")

    r += ["## Gaten per familie", "", "Dezelfde gaten keren in veel regelingen terug; per familie één keer oplossen.", ""]
    fam: dict[str, Counter] = defaultdict(Counter)
    for e in elementen:
        if not e["wb"]:
            fam[familie(e["pad"])][e["sectie"]] += 1
    r += ["| Familie | Ontbrekende elementen | Secties |", "|---|---:|---|"]
    for f, c in sorted(fam.items(), key=lambda kv: -sum(kv[1].values())):
        r.append(f"| {f} | {sum(c.values())} | " + ", ".join(f"`{s}` {n}" for s, n in c.most_common()) + " |")
    r.append("")

    r += ["## Vakantiebijslag (`holidayAllowance`) in detail", "", "| Pad | Mult | Type | Kern | Wijzerbelonen |", "|---|---|---|:-:|:-:|"]
    for e in per_sectie.get("holidayAllowance", []):
        r.append(
            f"| `{e['pad'].split('/', 1)[-1]}` | {e['mult']} | {e['type']} | {'ja' if e['kern'] else 'nee'} | "
            f"{'ja' if e['wb'] else 'nee'} |"
        )
    r.append("")

    r += ["## Volledige lijst: niet gevuld door Wijzerbelonen", ""]
    for s, es in per_sectie.items():
        mis = [e for e in es if not e["wb"]]
        if not mis:
            continue
        r += [f"### `{s}` ({len(mis)})", "", "| Pad | Mult | Familie | In kern |", "|---|---|---|:-:|"]
        for e in mis:
            r.append(f"| `{e['pad'].split('/', 1)[-1]}` | {e['mult']} | {familie(e['pad'])} | {'ja' if e['kern'] else 'nee'} |")
        r.append("")

    buiten = sorted(e["pad"] for e in elementen if not e["kern"])
    r += [
        "## Afwijkingen tussen Excel en schema",
        "",
        "Elementen uit de Excel die niet in het schema staan (kern kan ze niet dragen): "
        + (", ".join(f"`{p}`" for p in buiten) or "geen")
        + ".",
        "",
    ]
    RAPPORT.write_text("\n".join(r), encoding="utf-8")
    print(f"Geschreven: {RAPPORT}\n{nk}/{len(elementen)} in kern, {nw}/{len(elementen)} bij Wijzerbelonen")


if __name__ == "__main__":
    schrijf(Path(sys.argv[1]) if len(sys.argv) > 1 else STANDAARD_EXCEL)
