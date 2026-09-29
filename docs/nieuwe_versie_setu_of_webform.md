# Stappenplan: nieuwe versie van SETU of van de wijzerbelonen-webform

*Voor wie het project onderhoudt. Stand: SETU Inquiry Pay Equity **2.0** (schema `2.0.0_draft`), webform **2.1.0**.*

## Wanneer is dit nodig?

Er zijn twee soorten updates. Ze komen vaak samen, maar niet altijd:

| Update | Voorbeeld | Waar merk je het aan? |
|---|---|---|
| **A. Nieuwe SETU-versie** | Inquiry Pay Equity 2.2 of 3.0 | Aankondiging van SETU / Semantic Treehouse, of een nieuw schema in de webform |
| **B. Nieuwe webformversie** | wijzerbelonen 2.2.0 | Andere vragen op de website; de website waarschuwt bij het importeren van ons bestand; het versienummer in een export (`__webform_data__.appVersion`) |

- **Bij A** doorloop je stap 1 t/m 5 en stap 9.
- **Bij B** doorloop je stap 1 en 6 t/m 9.
- **Bij beide** doorloop je alles, in deze volgorde.

**Kleine of grote versie?**
- Een kleine versie (2.0 → 2.2) voegt meestal velden of codes toe. Bestaande berichten blijven dan geldig.
- Een grote versie (2.x → 3.0) kan velden hernoemen of verwijderen. Beslis dan eerst of oude berichten nog
  ingelezen moeten worden (zie stap 3).

## Waar de versies nu vastliggen

| Wat | Bestand | Nu |
|---|---|---|
| SETU-schema (het bestand zelf) | `src/cao_setu_v2/setu/schema/inquiry_pay_equity_2.0.0_draft.json` | 2.0.0_draft |
| Pad naar het schema | `src/cao_setu_v2/setu/bericht.py` → `SCHEMA_PAD` | 2.0.0_draft |
| Schema ophalen uit de webform | `tools/extraheer_schema.py` → `MARKER`, `DOEL` | 2.0.0_draft |
| Webformversie in het formuliermodel | `src/cao_setu_v2/formulier/formulier.py` → `WEBFORM_APP_VERSION` | 2.1.0 |
| Formaat van de opgeslagen antwoorden | `src/cao_setu_v2/koppeling/wijzerbelonen/antwoorden.py` → `LOCAL_STORAGE_DATA_VERSION` | 4 |
| Beginwaarden van een leeg formulier | idem → `STANDAARD_ANTWOORDEN` | |
| De echte webform (voor de tests) | `tests/referentie/webform-2.1.0.js` en `tests/referentie/webform.py` (`BUNDLE`, `appVersion`) | 2.1.0 |
| Tests die de versie noemen | `tests/koppeling/test_export.py`, `tests/test_setu.py` | 2.1.0 / 4 |
| Docstrings met het versienummer | `setu/__init__.py`, `setu/bericht.py`, `setu/codes.py`, `koppeling/wijzerbelonen/motor.py` en `gedeeld.py` | |

Na de update kun je controleren dat er niets is achtergebleven: zoek in `src`, `tests` en `tools` op het oude
versienummer (`2.0.0`, `2.1.0`).

---

## Stap 1 · Nulmeting en nieuwe bron ophalen

1. Draai de tests op de huidige versie: `.venv\Scripts\python.exe -m pytest -q tests`. Alles moet slagen. Zo weet
   je zeker dat verschillen straks door de update komen.
2. Download de nieuwe webform-bundle en bewaar hem naast de oude, bijvoorbeeld als
   `tests/referentie/webform-2.2.0.js`:
   ```powershell
   Invoke-WebRequest https://standaard-uitvraag.wijzerbelonen.nl/index.js -OutFile tests\referentie\webform-2.2.0.js
   ```
3. Zoek het versienummer en de schemanaam in de bundle:
   - `var appVersion = "…"` (onderaan, bij `src/index.tsx`);
   - `localStorageDataVersion = …` (in `src/model/Store.ts`);
   - de regel `// src/setu_standard/json_schema_….json`.
4. Komt het nieuwe SETU-schema niet (of nog niet) via de webform? Download het dan rechtstreeks bij SETU /
   Semantic Treehouse.

**Klaar als:** je weet welke webformversie, welk schema en welke `localStorageDataVersion` je hebt.

## Stap 2 · Het nieuwe schema in het project zetten *(A)*

1. Pas in `tools/extraheer_schema.py` de `MARKER` en `DOEL` aan naar de nieuwe schemanaam, bijvoorbeeld
   `json_schema_2.2.0.json` → `inquiry_pay_equity_2.2.0.json`.
2. Draai het script: `.venv\Scripts\python.exe tools\extraheer_schema.py`. Het schrijft het schema naar
   `src/cao_setu_v2/setu/schema/` en meldt het aantal definities. Nu zijn dat er 87.
3. Heb je het schema los gedownload, zet het bestand dan zelf in die map.
4. Laat het oude schemabestand staan. Het is nodig als je oude berichten wilt blijven lezen (stap 3), en je kunt
   het ermee vergelijken.
5. Maak een overzicht van de verschillen tussen het oude en het nieuwe schema: nieuwe, verdwenen en gewijzigde
   definities, velden, verplichte velden en keuzelijsten. Schrijf dat overzicht in `docs/`. Het is de werklijst
   voor stap 4.

**Klaar als:** het nieuwe schema in `setu/schema/` staat en je een lijst met verschillen hebt.

## Stap 3 · Beslissen: één versie of meerdere *(A, vooral bij een grote versie)*

- **Eén versie (eenvoudigst).** Het kernmodel gaat over op de nieuwe versie. Oude berichten lees je via
  `lees_tolerant()`, met regels in `setu/tolerant.py` die oude veldnamen omzetten.
- **Meerdere versies naast elkaar.** Nodig als je tegelijk berichten van 2.x én 3.x moet kunnen maken of lezen,
  bijvoorbeeld omdat de ene afnemer al over is en de andere nog niet. Dan komt er per versie een kernmodel
  (`setu/v2/`, `setu/v3/`). `lees()` kiest de versie op basis van het schema of van herkenbare velden.

Leg de keuze vast in `docs/` voordat je verder gaat.

## Stap 4 · Het SETU-kernmodel bijwerken *(A)*

1. Zet `SCHEMA_PAD` in `src/cao_setu_v2/setu/bericht.py` op het nieuwe schema.
2. Draai de conformiteitscontrole. Die vergelijkt het model veld voor veld met het schema:
   ```powershell
   .venv\Scripts\python.exe -c "from cao_setu_v2.setu.conformiteit import verschillen; print('\n'.join(verschillen()) or 'conform')"
   ```
3. Werk elk gemeld verschil weg, in de module waar het hoort:

   | Soort verschil | Module |
   |---|---|
   | keuzelijst (codes, bijv. nieuwe toeslagcodes) | `setu/codes.py` |
   | identificatie, bedragen, intervallen, regels | `setu/basis.py` |
   | datums (Single / Recurring / Relative) | `setu/tijd.py` |
   | condities | `setu/condities.py` |
   | opdrachtgever en contactpersonen | `setu/partij.py` |
   | salaristabellen, functies, grondslagen | `setu/beloning.py` |
   | regelingen (toeslagen, verlof, pensioen, …) | `setu/regelingen.py` |
   | het bericht zelf (hoofdniveau) | `setu/bericht.py` |

4. Kijk de lijst met bewuste afwijkingen na: `BEWUST` in `setu/conformiteit.py`. Staat de fout in het schema bij
   `Recurring` (`interval` / `recurringInterval`) er nog in? Dan blijft de uitzondering. Is die fout opgelost, dan
   halen we de uitzondering weg en schrijven we niet meer onder beide namen weg (`tijd.py`).
5. Kijk de formaatcontroles na in `bericht.py` → `_formaten()`, en de controle op `Single.date` in `tijd.py`.
   Controleren die nog dezelfde velden (`date-time`, `date`)?
6. Controleer bij een grote versie de regels in `setu/tolerant.py`: zijn ze nog geldig, en zijn er regels nodig om
   oude berichten om te zetten?
7. Werk de docstrings met het versienummer bij.

**Klaar als:** de conformiteitscontrole `conform` geeft en `tests/test_setu.py` slaagt. Vervang het officiële
voorbeeld in `docs/setu_bron/` als er een nieuw voorbeeld is, en pas de test daarop aan.

## Stap 5 · Nagaan of de koppeling nog geldige SETU maakt *(A)*

Maakt de webform nog berichten volgens het oude schema, dan is de koppeling hetzelfde gebleven, want die doet de
webform exact na. Het verschil zie je dan alleen in de schemacontrole:
```powershell
.venv\Scripts\python.exe examples\maak_upload_full.py
```
Bekijk de punten bij *SETU-controle tegen het officiële schema*. Komt een nieuw punt door het nieuwe schema en niet
door een bekende fout van de webform? Noteer het dan in `docs/koppeling_wijzerbelonen.md`. De upload naar
wijzerbelonen blijft hoe dan ook werken, want die gebruikt alleen `__webform_data__`.

## Stap 6 · De nieuwe webform als referentie *(B)*

1. Zet in `tests/referentie/webform.py` `BUNDLE` op het nieuwe bestand en `var appVersion` in `_HARNAS` op de nieuwe
   versie.
2. Het harnas knipt het opstartdeel van de bundle af bij de marker `_MARKER`, nu
   `"  // src/index.tsx\n  var import_jsx_runtime23"`. Het nummer in `import_jsx_runtime23` kan per versie
   veranderen. Zoek in de nieuwe bundle naar `// src/index.tsx` en neem de regel eronder over.
3. Heeft de nieuwe bundle andere browsermogelijkheden nodig, dan geeft het laden een fout zoals `X is not defined`.
   Vul die aan in `_STUBS`, net als nu `localStorage`, `document` en `crypto`.
4. Test het harnas:
   ```powershell
   .venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'tests'); from referentie.webform import Webform; wf=Webform(); print(len(wf.vragen()), 'vragen'); print(wf.standaard_antwoorden()); wf.close()"
   ```
   Het aantal vragen staat nu op 689 bij een leeg formulier.

**Klaar als:** het harnas laadt en vragen en standaardantwoorden teruggeeft.

## Stap 7 · Formuliermodel en antwoorden bijwerken *(B)*

1. Werk de versienummers bij:
   - `WEBFORM_APP_VERSION` in `formulier/formulier.py`;
   - `LOCAL_STORAGE_DATA_VERSION` in `koppeling/wijzerbelonen/antwoorden.py`.

   Klopt het tweede nummer niet, dan waarschuwt de website bij elk geïmporteerd bestand.
2. Neem de nieuwe beginwaarden over in `STANDAARD_ANTWOORDEN`. Die staan in de uitvoer van
   `wf.standaard_antwoorden()` uit stap 6.
3. Zoek uit welke vragen er zijn bijgekomen, verdwenen of veranderd. Vergelijk daarvoor de vragenlijsten van de oude
   en de nieuwe bundle:
   ```python
   from referentie.webform import Webform, BUNDLE
   oud = {tuple(v["slug"]) for v in Webform(BUNDLE.with_name("webform-2.1.0.js")).vragen()}
   nieuw = {tuple(v["slug"]) for v in Webform(BUNDLE.with_name("webform-2.2.0.js")).vragen()}
   print("nieuw:", nieuw - oud); print("weg:", oud - nieuw)
   ```
   Kijk ook naar de opties van keuzevragen (`options`) en naar de zichtbaarheidsregels. Vergelijk daarvoor de
   stukken `// src/definition/…` van beide bundles.
4. Werk voor elke wijziging het volgende bij:
   - de inventaris in `docs/formulier/NN_*.md`;
   - het formuliermodel in `src/cao_setu_v2/formulier/sNN_*.py`: vraag, slug, opties en `toon_als`.
5. Draai `tests/test_formulier.py`.

**Klaar als:** elke nieuwe vraag een veld heeft en `antwoord_problemen` geen onbekende slugs meer meldt (zie stap 8).

## Stap 8 · De SETU-omzetting van de webform bijwerken *(B)*

1. Draai de hele testsuite: `.venv\Scripts\python.exe -m pytest -q tests`. De tests vergelijken per sectie onze
   uitvoer met die van de nieuwe webform. Twee soorten meldingen kunnen voorkomen:
   - **`antwoord_problemen`**: een antwoord hoort bij geen bestaande of zichtbare vraag. Repareer het formuliermodel
     (stap 7).
   - **`vergelijk_setu`**: onze SETU verschilt van die van de webform. Pas de omzetting aan in
     `koppeling/wijzerbelonen/setu_sNN_*.py`, naar de nieuwe `convertSetuValue`-code in de bundle. Constanten
     (vaste posities zoals `ALLOWANCE_*` en `LEAVE_*`) staan in `gedeeld.py`; algemene logica
     (`toSetuStandard`, `clean`) in `motor.py`.
2. Voeg tests toe voor nieuwe vragen, in `tests/koppeling/test_sNN_*.py`, in dezelfde vorm als de bestaande
   scenario's (rijk, half, leeg).
3. Kijk in `docs/koppeling_wijzerbelonen.md` welke fouten van de webform zijn opgelost en welke nieuw zijn.

**Klaar als:** alle tests slagen tegen de nieuwe webform.

## Stap 9 · Voorbeelden, documentatie en afronding

1. Maak de invulhulp opnieuw: `.venv\Scripts\python.exe examples\invulhulp.py`. Zo krijgt `INVULHULP.md` de nieuwe
   vragen en keuzes.
2. Werk de voorbeelden bij:
   - `examples/maak_upload.py`: neem nieuwe verplichte of belangrijke vragen op.
   - `examples/maak_upload_full.py`: voeg elke nieuwe vraag toe.
3. Draai beide scripts. Onderaan moet `0` staan bij *antwoorden die de webform niet kent* en `0` bij *verschillen
   met de SETU-export van de webform*.
4. **Echte controle:** upload `uitvoer\wijzerbelonen_upload_full.json` op de website. Controleer dat er geen
   versiewaarschuwing komt en dat de nieuwe vragen ingevuld zijn.
5. Werk de versie en datum bij bovenaan in:
   - `docs/koppeling_wijzerbelonen.md`;
   - dit stappenplan;
   - `README.md` (indien nodig).
6. Zoek naar het oude versienummer (zie *Waar de versies nu vastliggen*). Haal de oude bundle en het oude schema
   pas weg als je ze niet meer nodig hebt (stap 3).
7. Laat collega's weten dat er een nieuwe versie is. Bestaande `maak_upload.py`-bestanden moeten mogelijk worden
   aangepast als vragen zijn veranderd; de melding van het script zegt welke.

## Controlelijst

- [ ] 1 · Tests slagen op de oude versie; nieuwe bundle of nieuw schema opgehaald
- [ ] 2 · Nieuw schema in `setu/schema/`, verschillenlijst gemaakt *(A)*
- [ ] 3 · Besloten: één versie of meerdere *(A)*
- [ ] 4 · Kernmodel conform het nieuwe schema; `test_setu.py` slaagt *(A)*
- [ ] 5 · Schemacontrole van de voorbeelden bekeken *(A)*
- [ ] 6 · Harnas laadt de nieuwe webform *(B)*
- [ ] 7 · Versienummers, standaardantwoorden en formuliermodel bijgewerkt *(B)*
- [ ] 8 · Alle tests slagen tegen de nieuwe webform *(B)*
- [ ] 9 · Invulhulp, voorbeelden en docs bijgewerkt; echte upload gecontroleerd
