# Inventaris webformulier "Standaard uitvraag Gelijkwaardig Belonen"

Fase 1 van het project: het webformulier van https://standaard-uitvraag.wijzerbelonen.nl/ volledig uitgeschreven,
als basis voor het Python-datamodel (fase 2) en de JSON-mapping (latere fases).

- **Bron:** de formulierdefinitie in de JavaScript-bundle van de webform (`index.js`, **appVersion 2.1.0**, opgehaald
  2026-09-24), bestanden `src/definition/*.tsx`. Alles is 1-op-1 uit de code afgeleid, niet uit de documentatie.
- **Controle:** alle ~480 slugs uit de broncode (letterlijk, in arrays en in templates) komen in deze documenten voor.

## Opbouw per document

Per sectie: `##` = subsectie (menu-item links in de tool), `###` = kopje/blok. Per blok een tabel:

| Kolom | Betekenis |
|---|---|
| Vraag | Letterlijke Nederlandse tekst uit de tool. `↳` = subvraag van de regel erboven |
| Slug | Interne sleutel van het antwoord. `[i]`/`[j]`/`[k]` = rij-index bij herhaalbare blokken; `<p>`/`<r>` = plaatshouder voor een lus-item |
| Type | tekst · getal · datum · tijd · radio · keuzelijst (radio als dropdown) · checkbox · *Bedragregel* (zie B1) |
| Opties | `label → waarde` (→ SETU-waarde als die afwijkt) |
| Toon als | Voorwaarde (`showIf`) waaronder de vraag zichtbaar is; "(blok)" = voorwaarde op het hele blok |
| Opt. | Vraag is optioneel |
| Herh. | Vraag zit in een herhaalbaar blok |
| SETU | Waar de webform het antwoord in de SETU-JSON zet (ter informatie voor de latere mapping) |

Onder de tabellen staan **Let op**-notities: verlies van informatie, vaste waarden en bugs in de webform.
Elk document eindigt met een **Telling**.

## Secties (volgorde zoals in de tool)

| # | Document | Vragen ¹ | Bijzonderheden |
|---|---|---|---|
| 00 | [Gedeelde bouwstenen](00_bouwstenen.md) | — | Bedragregel, keuzelijsten, vaste SETU-waarden en -indexen |
| 01 | [Algemeen](01_algemeen.md) | 13 | cao / eigen regeling, opdrachtgever |
| 02 | [Beloning](02_beloning.md) | 70 | herhaalbaar: salaristabellen → schalen → stappen; afwijkende roosters |
| 03 | [Functiegroepen](03_functiegroepen.md) | 3 per rij | koppeling functie ↔ salarisschaal |
| 04 | [Toeslagen](04_toeslagen.md) | 116 + 9 Bedragregels | toeslagrijen met varianten en toepassingsperiodes |
| 05 | [Vakantiebijslag](05_vakantiebijslag.md) | 1 + 1 Bedragregel | alleen percentage |
| 06 | [Vergoedingen](06_vergoedingen.md) | 142 | reiskosten, reisuren, stand-by, zorgverzekering, thuiswerk, mobiliteit, kosten |
| 07 | [Bijzondere uitkeringen](07_bijzondere-uitkeringen.md) | 70 | eenmalig, vast, jubileum, variabel |
| 08 | [Loondoorbetaling bij ziekte](08_loondoorbetaling-bij-ziekte.md) | 14 per rij | herhaalbare periodes |
| 09 | [Verlof](09_verlof.md) | 84 | ADV/ATV, vakantie, bijzonder verlof, Wazo, feestdagen |
| 10 | [Individueel keuzebudget](10_individueel-keuzebudget.md) | 17 (incl. 1 Bedragregel) | |
| 11 | [Pensioen](11_pensioen.md) | 5 | |
| 12 | [Duurzaam werken en leven](12_duurzaam-werken-en-leven.md) | 223 | 12 regelingen × dezelfde vragenset |
| 13 | [Aanvullende regelingen](13_aanvullende-regelingen.md) | 12 + 16 Bedragregels | PAWW, PAZW, RVU, WGA-hiaat, ongevallen, andere (herhaalbaar) |
| 14 | [Overig](14_overig.md) | 3 + 1 Bedragregel per rij | vrije regelingen |
| 15 | [Grondslagen](15_grondslagen.md) | 5 + toeslagrijen per grondslag | dynamisch: alleen gebruikte grondslagen |
| 16 | [Ondertekenen](16_ondertekenen.md) | 5 | contactpersonen (herhaalbaar), akkoord |

¹ Na het uitvouwen van lussen, bij herhaalbare blokken geteld voor één rij. Totaal ≈ 780 vragen en ≈ 27
Bedragregels van elk 3 tot 9 velden.

## Belangrijkste bevindingen voor het datamodel en de mapping

1. **Import leest alleen de formulierantwoorden.** De export van de webform is SETU-JSON plus `__webform_data__`
   (antwoorden per slug). Bij import negeert de webform de SETU-inhoud. Het Python-model moet dus op de slugs
   aansluiten, niet op SETU.
2. **De stap formulier → SETU verliest informatie.** Voorbeelden:
   - de vier cao-keuzes worden één boolean;
   - de naam van de salaristabel wordt niet geëxporteerd;
   - `origin` is altijd `Unknown`;
   - veel typeCodes zijn de algemene `EA100`/`EA300`/`EA903`;
   - Wazo-bedragen staan op 0 en de echte inhoud staat alleen in `name`;
   - lege posities verdwijnen door `clean()`, dus de vaste indexen gaan verloren.

   SETU → formulier kan daardoor alleen "best effort" zijn.
3. **Bugs in de webform zelf**, van belang om het gedrag straks exact na te bootsen of bewust te verbeteren:
   - pensioen-grondslag verschijnt nooit (verkeerde slug);
   - de naar-rato-vraag bij de zorgverzekering wordt nooit gelezen (typfout in de slug);
   - loondoorbetaling bij ziekte gebruikt voor elke rij het percentage van rij 0;
   - ADV "anders, namelijk" wordt niet gelezen;
   - de jaren bij vakantiedagen per duur dienstverband gaan verloren;
   - de aanvullende regelingen (13) staan in `supplementaryArrangement`, maar met `OTHER_*`-indexen;
   - diverse conversies lopen vast bij half ingevulde bedragen.

   Details staan in de Let op-notities per sectie.
4. **Het officiële JSON-schema is zelf niet helemaal consistent.** `Recurring` vereist `interval`, maar
   definieert alleen `recurringInterval`. Zie [15 Grondslagen](15_grondslagen.md).
