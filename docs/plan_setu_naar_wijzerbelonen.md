# Plan: SETU-model als enige invoer, met een upload voor wijzerbelonen

*Status: concept, wacht op akkoord van Justin.*

## Doel

Je vult alleen het **SETU-kernmodel** (`InquiryPayEquity`) in. Daaruit komt:

1. **SETU-JSON.** Dit werkt al: `bericht.schrijf()`. Het bestand wordt gevalideerd tegen het officiële schema.
2. **Een uploadbestand voor wijzerbelonen.** Dit is nieuw: de SETU wordt omgezet naar de antwoorden van de tool
   (`__webform_data__`).

```
Jouw applicatie
   │  vult
   ▼
InquiryPayEquity (SETU-kernmodel)                 ← de enige invullaag
   ├─► SETU-JSON                                     bestaat al
   └─► van_setu.naar_formulier()   (nieuw)
          ▼
       Formulier (hulplaag, je vult hem niet zelf)
          ▼  antwoorden.naar_antwoorden()            bestaat al
       __webform_data__  ──►  upload op wijzerbelonen.nl
```

Het formuliermodel wordt een interne hulplaag van de wijzerbelonen-adapter. We zetten SETU om naar het `Formulier` en
niet rechtstreeks naar de antwoorden. Het model controleert dan zelf welke antwoorden mogen: zichtbaarheid, opties en
combinaties. Het omzetten naar de antwoorden van de tool bestaat al en is getest.

## Wat de analyse laat zien

SETU en het formulier passen niet één-op-één op elkaar. Per onderdeel geldt een van vier gevallen:

| Soort | Betekenis | Voorbeelden |
|---|---|---|
| **1-op-1** | direct terug te zetten | data, namen, bedragen, salarisschalen en -stappen, contactpersonen, grondslagen per `baseType` |
| **afleidbaar** | met een vaste regel | "cao van toepassing?" uit `customLabourAgreement` plus de aanwezigheid van een cao; het soort bedrag (vast/percentage/tijd) uit `amount.unitCode`; een ja/nee-vraag uit de aanwezigheid van een regeling |
| **standaardwaarde** | SETU kent het niet, het formulier wel | naam van de salaristabel, "waarom is de cao van toepassing", het akkoordvinkje (blijft uit, zodat je in de tool zelf tekent) |
| **niet terug** | SETU kan meer dan het formulier | geneste of niet-tekstuele condities, meerdere regels (lines), `interval.value ≠ 1`, typeCodes die het formulier niet kent, werknemerspremie pensioen, meerdere IKB's |

"Niet terug" betekent niet dat het stil verdwijnt. Het komt in een **meldingenlijst**: wat niet in de tool terechtkomt,
per SETU-pad.

### Herkennen welk SETU-onderdeel bij welke vraag hoort

Dit is de grootste uitdaging. In SETU zijn vooral de `allowance`-regels één grote lijst: toeslagen (04),
vergoedingen (06), uitkeringen (07), pauzes (02), wachtdagcompensatie (08) en tijd-voor-tijd (09) staan er allemaal
in. Herkennen gaat in drie stappen:

1. **Op typeCode**, als die uniek is voor één vraag.
   - HT400: betaalde pauzes.
   - HT320, HT300, HT101, EA301, HT200: toeslagsoorten.
   - HT600: reisuren.
   - EA604: zorgverzekering.
   - EA605/EA607/EA608: thuiswerk en internet.
   - EA600: wachtdagcompensatie.
   - HT500: tijd voor tijd.
   - De typeCodes van `supplementaryArrangement` en `sustainableEmployability` zijn grotendeels uniek.
2. **Op typeCode en naam**, als een typeCode meerdere vragen dekt.
   - HT602: stand-by (04 en 06).
   - EA103: vijf soorten reiskosten.
   - EA100: zes kostenvergoedingen en vijf mobiliteitsregelingen.
   - EA300: waarneming, performance of anders.
   - EA801/EA903: soort bijzondere uitkering.
   - `Other`: verplichte scholing en de twee "anders"-varianten in 12.
   - `leave[]`: dit onderdeel heeft geen typeCode; herkennen gaat op sublijst (`paidLeave`, `specialLeave`, …) en naam.
3. **Terugvallen op een "anders"-vraag**, met een melding, als niets past. Een onbekende toeslag wordt dan
   "Toeslagen anders", een onbekende vergoeding "Kostenvergoeding anders".

Stap 2 werkt betrouwbaar voor SETU die de webform zelf heeft gemaakt, want de namen zijn vast. Bij SETU die je zelf
invult, kies je zelf de namen. Daarom stel ik hulpfuncties voor (beslispunt 2).

### Valkuilen

- **"null"-teksten.** De webform plakt lege antwoorden als `"null"` in teksten. Op de terugweg wordt dat weer leeg.
- **Tekstsjablonen.** Sommige informatie zit alleen in vaste zinnen en moet uit de tekst worden gehaald.
  - IKB: `"Eindejaarsuitkering voor 3% van maandloon"`.
  - Duurzaam werken: `"… namelijk: X"`.
  - Verplicht verlof, feestdagen, voorwaarden bij uitkeringen.
- **Verloren structuur.** Afwijkende roosters (02) zijn in SETU kopieën van een salaristabel. Voor SETU die je zelf
  invult wordt elke `remuneration` gewoon een salaristabel. Terugvouwen tot een rooster is een optionele heuristiek.
- **Dezelfde naam op twee plaatsen.** In sectie 12 heten twee regelingen allebei `"Anders, namelijk: X"` (typeCode
  `Other`); alleen de volgorde onderscheidt ze. EA300 in de grondslagen (15) kan naar drie toeslagsoorten wijzen.
- **Voorkomen dat de tool vastloopt.** De tool loopt vast bij sommige combinaties, bijvoorbeeld min/max zonder bedrag,
  of "naar rato" zonder budget. Zulke antwoorden maakt de terugweg nooit aan.
- **Grondslagen (15).** Deze verschijnen in de tool alleen als elders een grondslag gekozen is. Een `baseDefinition`
  waar niets naar verwijst, zou onzichtbaar worden; dat geeft een melding.

## Ontwerp

### Waar het komt

`src/cao_setu_v2/koppeling/wijzerbelonen/van_setu/`:

| Module | Inhoud |
|---|---|
| `naar_formulier.py` | `naar_formulier(bericht) -> (Formulier, meldingen)`: roept de secties in volgorde aan (15 als laatste) |
| `gedeeld.py` | de omgekeerde Bedragregel (`line` → vast/percentage/tijd/n.v.t.), `"null"` → leeg, datums, ISO-duur (`P25Y6M`), tekstsjablonen, meldingen |
| `herkenning.py` | de tabellen typeCode/naam → formuliervraag. Die worden afgeleid uit de bestaande `setu_sNN`-modules (dezelfde constanten en labels), zodat heen en terug niet uit elkaar kunnen lopen |
| `s01_algemeen.py` … `s16_ondertekenen.py` | per sectie de terugweg |

### Uploadbestand

`schrijf_upload(bericht, pad)` schrijft:

- **Het SETU-deel**: jouw eigen `InquiryPayEquity`, ongewijzigd en gevalideerd (beslispunt 1).
- **`__webform_data__`**: de antwoorden die uit de terugweg komen.

Daarnaast geeft de functie de meldingen terug: wat niet in de tool terechtkomt en welke standaardwaarden zijn
ingevuld.

### Controle

De controle gaat, net als bij de heenweg, tegen de echte webformcode.

1. **Rondgang vanuit het formulier.** `Formulier` → SETU (via de tool) → `naar_formulier` → antwoorden. Die moeten
   gelijk zijn aan de oorspronkelijke antwoorden, op de bekende verliezen na. Alle scenario's van de bestaande tests
   (rijk, half, leeg per sectie) worden zo hergebruikt.
2. **Rondgang vanuit SETU.** Een zelf ingevuld SETU-bericht → antwoorden → SETU (via de tool). Het verschil met het
   origineel moet precies overeenkomen met de meldingen. Geen stil verlies dus.
3. **Import in de tool.** De bestaande import-simulatie leest het uploadbestand zonder waarschuwing in.

## Stappen

Na elke stap is er een review door jou.

| Stap | Inhoud | Moeilijkheid |
|---|---|---|
| **0** | `gedeeld.py`, `herkenning.py`, het meldingensysteem en de twee rondgang-tests als raamwerk | middel |
| **A** | 01 Algemeen, 05 Vakantiebijslag, 10 IKB, 11 Pensioen, 14 Overig, 16 Ondertekenen, plus een eerste versie van het nieuwe `maak_upload.py` met het SETU-model als invoer | laag |
| **B** | 02 Beloning en 03 Functiegroepen (schalen, periodieken, roosters, koppeling functie ↔ schaal) | hoog |
| **C** | 04 Toeslagen, 06 Vergoedingen, 07 Bijzondere uitkeringen (de hele `allowance`-herkenning) | hoog |
| **D** | 08 Ziekte, 09 Verlof, 12 Duurzaam werken, 13 Aanvullende regelingen, 15 Grondslagen (als laatste; hangt af van de rest) | middel-hoog |

Na stap A kun je het al gebruiken voor een eenvoudig bericht. De secties die dan nog ontbreken, komen in de meldingen
als "nog niet ondersteund".

## Beslispunten voor Justin

1. **Welk SETU-deel komt in het uploadbestand?**
   - *Voorstel:* jouw eigen SETU, precies zoals je hem invulde. Dat is het standaardbericht, bijvoorbeeld voor het
     uitzendbureau.
   - Let op: exporteer je na het uploaden opnieuw vanuit de tool, dan maakt de tool zijn eigen SETU. Die mist wat in
     de meldingen stond.
2. **Hulpfuncties voor het invullen van SETU.**
   - *Voorstel:* een paar functies die SETU-objecten maken met de vaste typeCodes en namen, bijvoorbeeld
     `toeslag(ToeslagSoort.OVERWERK, percentage=125, ...)` of `kostenvergoeding("koffiegeld", ...)`. Het blijft gewoon
     SETU, maar de herkenning wordt 100% betrouwbaar.
   - Zonder hulpfuncties werkt het ook. Herkenning gaat dan op typeCode, met terugval op "anders".
3. **Wat SETU kan en het formulier niet.**
   - *Voorstel:* een melding geven en doorgaan, want de upload werkt dan nog.
   - *Alternatief:* een fout geven, zodat je het eerst aanpast.
4. **Standaardwaarden voor vragen die SETU niet kent.**
   - *Voorstel:*
     - salaristabel `"Salaristabel 1"`, `"Salaristabel 2"`, …;
     - het akkoordvinkje uit;
     - "waarom cao van toepassing" leeg (je vult het in de tool in);
     - bij ja/nee zonder SETU-gegevens `nee`.
   - Alles wat zo is ingevuld, staat in de meldingen.
5. **Het formulier als invoer houden.**
   - *Voorstel:* ja, als interne laag en voor de tests. Je hoeft het niet meer te gebruiken. `maak_upload.py` gaat
     over op het SETU-model.

## Niet in dit plan

- Een export van wijzerbelonen (`__webform_data__`) terug inlezen in het SETU-model. Dat gaat via de bestaande
  heenweg: antwoorden → SETU → `InquiryPayEquity.lees_tolerant()`.
- Inlenersbeloning.
