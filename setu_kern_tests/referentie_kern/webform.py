"""De echte wijzerbelonen-webform (v2.1.0) als referentie, zonder browser.

De JavaScript-bundle van de webform wordt in V8 geladen (``mini-racer``, dev-afhankelijkheid). Alleen het
opstartdeel (React-weergave, localStorage-autoruns) wordt vervangen door een klein harnas; de formulierdefinitie
en ``Store.toSetuStandard()`` zijn de originele code. Zo kunnen tests onze Python-uitvoer vergelijken met wat de
tool zelf zou exporteren.

    with Webform() as wf:
        wf.standaard_antwoorden()        # de beginwaarden van een leeg formulier
        wf.vragen(antwoorden)            # alle vragen (slug, type, opties, zichtbaar) bij deze antwoorden
        wf.setu(antwoorden)              # de SETU-JSON die de webform van deze antwoorden maakt
"""

import json
from pathlib import Path
from typing import Any

BUNDLE = Path(__file__).with_name("webform-2.1.0.js")
_MARKER = "  // src/index.tsx\n  var import_jsx_runtime23"

_STUBS = r"""
var __opslag = () => { const d = {}; return { getItem: k => (k in d ? d[k] : null), setItem: (k, v) => { d[k] = String(v); },
  removeItem: k => { delete d[k]; }, clear: () => { for (const k in d) delete d[k]; } }; };
var window = globalThis; var self = globalThis;
var localStorage = __opslag(); var sessionStorage = __opslag();
var document = { location: { search: "" } };
var location = document.location;
var navigator = { userAgent: "harnas" };
var console = { log() {}, warn() {}, error() {}, info() {}, debug() {} };
var setTimeout = (f) => 0; var clearTimeout = () => {}; var queueMicrotask = (f) => f();
var MessageChannel = function () { this.port1 = {}; this.port2 = { postMessage() {} }; };
var crypto = { getRandomValues(a) { for (let i = 0; i < a.length; i++) a[i] = Math.floor(Math.random() * 256); return a; } };
"""

_HARNAS = r"""
  configure({ enforceActions: "never" });
  var appVersion = "2.1.0";
  var __vast = (d) => JSON.parse(JSON.stringify(d, (k, v) => (v === undefined ? null : v)));
  globalThis.__wb = {
    store(antwoorden) {
      const store = new Store();
      store.fromDefinition(makeSectionDefs(store));
      if (antwoorden) {
        store.answers = { ...store.answers, ...JSON.parse(antwoorden) };
        store.fromDefinition(makeSectionDefs(store));  // herhaalbare blokken hangen af van de antwoorden
      }
      return store;
    },
    standaard() { return JSON.stringify(this.store().answers); },
    setu(antwoorden, vasteId) {
      const data = this.store(antwoorden).toSetuStandard();
      if (vasteId) { data.documentId.value = data.documentId.value; data.issued = "vast"; }
      return JSON.stringify(data);
    },
    importeer(bestand) {
      // Zoals Store.importFromFile: alleen __webform_data__ wordt gelezen, via fromLocalStorage(..., true).
      const d = JSON.parse(bestand);
      if (!d.__webform_data__) return JSON.stringify({ fout: "Je upload is geen geldige oude export van dit webformulier." });
      const store = new Store();
      store.fromDefinition(makeSectionDefs(store));
      const versieWaarschuwing = d.__webform_data__.localStorageDataVersion !== store.localStorageDataVersion;
      store.fromLocalStorage(d.__webform_data__, true);
      store.fromDefinition(makeSectionDefs(store));
      const setu = store.toSetuStandard();
      delete setu.issued;
      return JSON.stringify({ versieWaarschuwing, antwoorden: store.answers, setu });
    },
    vragen(antwoorden) {
      const store = this.store(antwoorden);
      return JSON.stringify(store.allQuestions.map(q => __vast({
        slug: q.slug, type: q.type, shown: q.isShown, optional: q.optional ?? false,
        options: q.options ? q.options.map(o => o.value) : null,
        restrictTo: q.restrictTo ?? null, setuPath: q.setuPath ?? null,
      })));
    },
  };
})();
"""


class Webform:
    def __init__(self, bundle: Path = BUNDLE):
        from py_mini_racer import MiniRacer

        kop, _ = bundle.read_text(encoding="utf-8").split(_MARKER)
        self._ctx = MiniRacer()
        self._ctx.eval(_STUBS + kop + _HARNAS)

    def _roep(self, functie: str, *args: Any) -> Any:
        return json.loads(self._ctx.call(f"__wb.{functie}.bind(__wb)", *args))

    def standaard_antwoorden(self) -> dict:
        return self._roep("standaard")

    def vragen(self, antwoorden: dict | None = None) -> list[dict]:
        return self._roep("vragen", json.dumps(antwoorden) if antwoorden else None)

    def setu(self, antwoorden: dict) -> dict:
        """SETU-JSON zoals de webform hem exporteert (zonder ``__webform_data__``); ``issued`` wordt weggelaten."""
        data = self._roep("setu", json.dumps(antwoorden), False)
        data.pop("issued", None)
        return data

    def importeer(self, bestand: dict) -> dict:
        """Wat de knop "Importeren" van de tool met dit bestand doet: ``versieWaarschuwing``, de ingelezen
        ``antwoorden`` en de SETU-JSON die de tool daarna zou exporteren (zonder ``issued``); of ``fout``."""
        return self._roep("importeer", json.dumps(bestand))

    def close(self) -> None:
        self._ctx.close()

    def __enter__(self) -> "Webform":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
