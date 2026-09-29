"""Haalt het officiële SETU-schema uit de wijzerbelonen-webform en slaat het op als JSON.

Gebruik (vanuit de projectmap):  .venv\\Scripts\\python.exe tools\\extraheer_schema.py

De webform bundelt `src/setu_standard/json_schema_2.0.0_draft.json` als JavaScript-object in index.js.
Dit script knipt dat object eruit, zet het om naar JSON en schrijft het naar het setu-pakket.
"""

import json
import re
import urllib.request
from pathlib import Path

BUNDLE_URL = "https://standaard-uitvraag.wijzerbelonen.nl/index.js"
MARKER = "// src/setu_standard/json_schema_2.0.0_draft.json"
DOEL = Path(__file__).resolve().parents[1] / "src/cao_setu_v2/setu/schema/inquiry_pay_equity_2.0.0_draft.json"


def js_object_naar_json(js: str) -> str:
    """Zet een door esbuild gegenereerd JS-objectliteral om naar JSON (sleutels zonder aanhalingstekens)."""
    uit, i, in_string = [], 0, False
    while i < len(js):
        c = js[i]
        if in_string:
            uit.append(c)
            if c == "\\":
                uit.append(js[i + 1])
                i += 1
            elif c == '"':
                in_string = False
        elif c == '"':
            in_string = True
            uit.append(c)
        else:
            m = re.match(r"[A-Za-z_$][\w$-]*(?=\s*:)", js[i:])
            if m and (not uit or re.search(r"[{,]\s*$", "".join(uit[-20:]))):
                uit.append(f'"{m.group(0)}"')
                i += len(m.group(0))
                continue
            uit.append(c)
        i += 1
    return "".join(uit)


def main() -> None:
    bundle = urllib.request.urlopen(BUNDLE_URL).read().decode("utf-8")
    start = bundle.index(MARKER)
    begin = bundle.index("{", start)
    eind = bundle.index("\n  };", begin) + len("\n  }")  # einde van `var json_schema_... = { ... };`
    schema = json.loads(js_object_naar_json(bundle[begin:eind]))
    DOEL.parent.mkdir(parents=True, exist_ok=True)
    DOEL.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{schema.get('title')} — {len(schema['definitions'])} definities → {DOEL}")


if __name__ == "__main__":
    main()
