# Koppeling formuliermodel → wijzerbelonen-upload en SETU-JSON

*Stand: 25-09-2026, webform v2.1.0.*

## Gebruik

```powershell
.venv\Scripts\python.exe examples\maak_upload.py        # schrijft uitvoer\wijzerbelonen_upload.json
```

Pas `vul_formulier()` in `examples/maak_upload.py` aan met je eigen gegevens. Upload het bestand daarna op
https://standaard-uitvraag.wijzerbelonen.nl/ via **Importeren**.

In code:

```python
from cao_setu_v2.koppeling.wijzerbelonen import naar_setu

data = naar_setu.setu_json(formulier)             # SETU-JSON, precies zoals de tool hem exporteert
naar_setu.valideer(data)                          # [] = geldig volgens het officiële SETU-schema
naar_setu.setu_bericht(formulier)                 # als InquiryPayEquity (kernmodel); alleen bij geldige SETU
naar_setu.schrijf_export(formulier, "upload.json")  # SETU-JSON + __webform_data__
```

## Hoe het werkt

```
Formulier (Python)
   │  antwoorden.naar_antwoorden()     slug-sjablonen in veld(...) → de antwoorden van de tool
   ▼
__webform_data__.answers  ──────────►  dit leest wijzerbelonen bij Importeren (alléén dit)
   │  motor.naar_setu_json() + setu_s01 … setu_s16
   ▼
SETU-JSON (Inquiry Pay Equity v2.0)
```

- `src/cao_setu_v2/koppeling/wijzerbelonen/antwoorden.py` zet het `Formulier` om naar de antwoorden, in het
  formaat van de tool:
  - tekst en getallen als tekst;
  - datums als milliseconden;
  - de standaardlijsten altijd aanwezig, want zonder die lijsten loopt de import vast.
- `motor.py` is een Python-versie van `Store.toSetuStandard()`: pad-zetten op basis van het schema, de extra rijen,
  `clean()` en de standaardwaarden.
- `setu_s01_…` t/m `setu_s16_…` zijn per sectie een port van de `setuPath`/`convertSetuValue`-vragen, in dezelfde
  volgorde als in de tool.

## Hoe het getest is

De échte JavaScript-code van de tool (`tests/referentie/webform-2.1.0.js`) draait in de tests zonder browser, in
V8 (`mini-racer`, dev-afhankelijkheid). Per sectie worden meerdere scenario's (rijk, half ingevuld, leeg) op twee
manieren gecontroleerd:

1. **Elk antwoord hoort bij een bestaande, zichtbare vraag** en heeft een geldige waarde (`antwoord_problemen`).
2. **Onze SETU-JSON is gelijk aan die van de tool** (`vergelijk_setu`).

Daarnaast wordt de knop **Importeren** nagebootst op het uploadbestand: de tool leest het bestand zonder
waarschuwing in en exporteert daarna exact dezelfde SETU-JSON. Het volledige pakket telt 144 tests:
`.venv\Scripts\python.exe -m pytest -q tests`.

## Bewust nagedaan: fouten van de tool

De omzetting doet de tool exact na, fouten inbegrepen. Zo is onze uitvoer gelijk aan die van de tool. Een gevonden
fout kan later gericht verbeterd worden.

| Sectie | Wat de tool doet |
|---|---|
| algemeen | Ontbrekende antwoorden in teksten worden letterlijk `"null"`, bijv. `"Eenmalige uitkering: null"` en `"ADV dagen voor null% van null"` |
| algemeen | Vervolgvragen worden vaak gelezen zonder te kijken of ze zichtbaar zijn |
| algemeen | `clean()` verwijdert lege onderdelen, waardoor de vaste posities in lijsten opschuiven |
| 02 | Een afwijkend rooster zet de uren in `workDuration.amount.value` en in `valuePerWeek`, ook bij een interval van 4 weken |
| 02 | Rooster-kopieën worden gemaakt vóór sectie 03 en krijgen dus geen functieprofielen |
| 02 | Werkervaring (of een afwijkend rooster) zonder bestaande salaristabel in SETU laat de export **vastlopen** |
| 03 | Zonder code wordt de titel gebruikt als `positionId` |
| 04 | Toepassingsperiodes en afbouwregeling komen ook mee bij soorten waar dat blok verborgen is |
| 04 | Afbouwregeling "ja" zonder tekst geeft `phaseOutScheme: ""` |
| 04 | Waarneming, performance en anders delen typeCode EA300 |
| 06 | Tikfout `vergoeding-zorgerzekering-naar-rato`: "naar rato" bij de zorgverzekering komt nooit in SETU |
| 06 | OV "per rit" krijgt interval `Item` in plaats van `Trip` |
| 06 | Stand-by "anders" verliest de voorwaarden |
| 06 | Alle mobiliteitsregelingen krijgen `EA100` |
| 07 | De uitkeringsdatum (`payDate`) is een datum zonder tijd (`2026-12-15`), terwijl het schema een datum mét tijd eist. Andere datums schrijft de webform wel goed (`2026-07-01T00:00:00+02:00`). De website meldt dit zelf ook. |
| 09 | De leeftijd bij extra vakantiedagen staat als tekst (`"55"`) in plaats van als getal. De website meldt dit zelf ook. |
| 07 | Min/max = ja zonder bedrag bij eenmalig/variabel laat de export **vastlopen** |
| 07 | Jubileum "anders" laat de dienstverbandduur en de voorwaarden vallen |
| 07 | Eenmalig "anders" zonder voorwaarden krijgt geen `line` |
| 08 | Elke periode krijgt het percentage en de grondslag van rij 0 |
| 08 | Rij 0 zonder percentage geeft helemaal geen sickPay |
| 08 | `waitingDays` komt er ook bij wachtdagen = nee |
| 09 | ADV "anders, namelijk" wordt niet gelezen (verkeerde slug), dus de naam eindigt op `null` |
| 09 | De jaren bij extra vakantiedagen per dienstverband gaan verloren (`valueOf` zonder `()`). Daardoor is de voorwaarde in SETU ongeldig; de website meldt dit zelf ook. |
| 09 | Wazo-bedragen staan op 0 |
| 10–12 | Een regeling met naar rato/uitgekeerd/voorwaarden maar zonder budget laat de export **vastlopen** |
| 10–12 | Verplichte scholing krijgt interval `Item` |
| 13 | Andere sociale regelingen gaan ook mee bij ja/nee = nee; rijen zonder omschrijving vallen weg |
| 15 | De pensioen-grondslag verschijnt nooit via pensioen (verkeerde slug `pensioenregeling`) |
| 15 | Grondslagen worden ook gelezen uit verborgen of achtergebleven antwoorden |

**Vastlopen:** in de drie gevallen hierboven maakt ook de tool zelf geen SETU-JSON. `schrijf_export` schrijft dan een
bestand met alleen `__webform_data__` en een `error`. Importeren in de tool werkt dan nog steeds.

## Aandachtspunten

- **Keuzelijsten zonder lege optie.** Sommige keuzelijsten in de tool hebben geen lege optie (`blankOption: false`).
  De tool kiest daar bij het tonen zelf de eerste optie. Laat je zo'n vraag leeg, dan kan de tool na het importeren
  een waarde tonen die niet in het bestand stond.
- **"Geen"-vinkjes.** Het "Geen"-vinkje bij kostenvergoedingen wist in de tool de andere vinkjes. Het model doet dat
  niet.
- **Datums** gaan uit van de lokale tijdzone (Nederland), net als de datumkiezer van de tool.
- **Nieuwe versie van de tool.** Komt er een nieuwe webformversie, vervang dan de bundle in `tests/referentie/` en
  draai de tests: elk verschil wordt zichtbaar.
- **Niet gebouwd:** SETU-JSON of een export van de tool terug inlezen in het `Formulier`. Daarvoor is een omzetting
  van antwoorden naar `Formulier` nodig; dat is een logische volgende stap.
