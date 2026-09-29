# 04 · Toeslagen

Bron: `src/definition/04_toeslagen.tsx` (webformulier v2.1.0).

**Structuur:** de sectie begint met één vaste subsectie *Toeslagen* met een checkbox per toeslagsoort (9 soorten,
gedefinieerd in `makeToeslagRows`) plus *Geen toeslagen*. Voor elke aangevinkte toeslagsoort verschijnt daarna een
**dynamische subsectie** (menu-label = label van de toeslag). Daarin staan één of meer **variaties** (herhaalbare
rijen onder slug `<toeslag>[i]`), elk met een Bedragregel, voorwaarden, cumulatie en — afhankelijk van de
toeslagsoort — een titel, toepassingsperiodes (zelf weer herhaalbaar, `<toeslag>[i]/toepassingsperiodes[j]`) en
een afbouwregeling. `makeToeslagRows` wordt ook gebruikt door [15 Grondslagen](15_grondslagen.md).

## Toeslagsoorten (`makeToeslagRows`)

| # | Slug (`<toeslag>`) | Label | typeCode | SETU-index (constants.ts, ongebruikt ¹) | Titel | Toepassingsperiodes | Datumbereik | Afbouwregeling |
|---|---|---|---|---|---|---|---|---|
| 1 | `onregelmatigheids-toeslagen` | Onregelmatigheids- toeslagen (waaronder feestdagen) | `HT320` | `ALLOWANCE_ONREGELMATIGHEIDS_TOESLAGEN` (9) | | ja | | |
| 2 | `ploegentoeslagen` | Ploegentoeslagen | `HT300` | `ALLOWANCE_PLOEGETOESLAGEN` (10) | | | | ja |
| 3 | `toeslagen-verschoven-diensten` | Toeslagen voor verschoven diensten | `HT101` | `ALLOWANCE_TOESLAGEN_VERSCHOVEN_DIENSTEN` (11) | | ja | | |
| 4 | `toeslagen-fysieke-belasting` | Toeslagen voor (fysieke) belasting | `EA301` | `ALLOWANCE_TOESLAGEN_FYSIEKE_BELAS` (12) | | | | |
| 5 | `toeslagen-stand-by-consignatie-bereikbaarheidsdiensten` | Toeslagen voor werken tijdens stand-by-, consignatie- of bereik- baarheidsdiensten | `HT602` | `ALLOWANCE_TOESLAGEN_STANDBY` (13) | | ja | | |
| 6 | `overwerktoeslag` | Overwerk | `HT200` | `ALLOWANCE_OVERWERK_TOESLAG` (14) | | ja | | |
| 7 | `waarnemingstoeslag` | Waarnemingstoeslag | `EA300` | `ALLOWANCE_WAARNEMINGSTOESLAG` (15) | | | | ja |
| 8 | `performancetoeslag` | Performancetoeslag | `EA300` | `ALLOWANCE_PERFORMANCETOESLAG` (16) | | | | ja |
| 9 | `anders` | Anders | `EA300` | `ALLOWANCE_TOESLAGEN_ANDERS` (18) | ja (`showNameInput`) | ja | ja | ja |

De laatste vier kolommen geven aan welke optionele blokken per soort zichtbaar zijn (vlaggen
`showNameInput`, `showToepassingsPeriode`, `showToepassingsPeriodeDatumBereik`, `showAfbouwregeling`).

Beschrijvingen (hulptekst bij de checkbox = `shortDescription` indien aanwezig, anders `description`; `description`
is ook de intro van de subsectie):

| Toeslag | Hulptekst / intro |
|---|---|
| `onregelmatigheids-toeslagen` | Ken je toeslagen voor werken in onregelmatigheid? |
| `ploegentoeslagen` | Zijn er afwijkende toeslagen voor het werken in ploegendiensten? (intro extra: *"Vul bij "hoe wordt de toeslag uitgekeerd?" het bedrag of het percentage van de ploegentoeslag in."*) |
| `toeslagen-verschoven-diensten` | Ken je afwijkende toeslagen voor verschoven diensten? |
| `toeslagen-fysieke-belasting` | Ken je toeslagen voor (fysiek) belastend werk? Denk aan een koude toeslag, een vuilwerk toeslag of een toeslag voor het werken met gevaarlijke stoffen. |
| `toeslagen-stand-by-consignatie-bereikbaarheidsdiensten` | Ken je toeslagen voor het komen werken tijdens stand-by-, consignatie- of bereikbaarheidsdiensten? (intro extra: *"Het gaat hier om toeslagen voor de uren die worden gewerkt nadat de medewerker vanuit de stand-by-, consignatie- of bereikbaarheidsdienst is opgeroepen om te komen werken. Dit is anders dan de vergoeding over de uren die de medewerker stand-by staat of bereikbaar is om te komen werken"*) |
| `overwerktoeslag` | Ken je een overwerktoeslag? (intro extra: vul onder "Hoe wordt de toeslag uitgekeerd?" de hoogte in en onder "onder welke voorwaarden geldt de toeslag" wanneer er sprake is van overwerk) |
| `waarnemingstoeslag` | *(leeg)* |
| `performancetoeslag` | hulptekst leeg; intro: *"Het gaat hier om een periodieke toeslag die wordt gebruikt om individuele prestaties te belonen. Dit is anders dan de performance uitkering die vaak achteraf wordt uitgekeerd en afhankelijk is van het behalen van bepaalde targets of resultaten. De performance uitkering komt terug bij de variabele (voorwaardelijke) uitkeringen."* |
| `anders` | Kent jouw onderneming nog andere toeslagen (bijvoorbeeld BHV of OR)? |

¹ De index-constanten staan wel in de rij-definitie (`index`), maar worden in deze sectie niet gebruikt: alle
toeslagen worden via `allowance_EXTRA_ALLOWANCES` **achteraan** de `allowance`-lijst toegevoegd (zie Let op).

## Toeslagen

### Welke toeslagen kent jouw organisatie?

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Onregelmatigheids- toeslagen (waaronder feestdagen) | `onregelmatigheids-toeslagen/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Ploegentoeslagen | `ploegentoeslagen/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Toeslagen voor verschoven diensten | `toeslagen-verschoven-diensten/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Toeslagen voor (fysieke) belasting | `toeslagen-fysieke-belasting/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Toeslagen voor werken tijdens stand-by-, consignatie- of bereik- baarheidsdiensten | `toeslagen-stand-by-consignatie-bereikbaarheidsdiensten/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Overwerk | `overwerktoeslag/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Waarnemingstoeslag | `waarnemingstoeslag/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Performancetoeslag | `performancetoeslag/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Anders | `anders/enabled` | checkbox | — | — | | | `allowance_EXTRA_ALLOWANCES` ² |
| Geen toeslagen | `geen-toeslagen` | checkbox | — | — | | | — |

² Per variatie `i` van de toeslag bouwt de checkbox een AllowanceArrangement
`{name, description, typeCode, line: [Bedragregel + conditions], reference[], period[], phaseOutScheme?, origin}`
en voegt die toe aan `allowance_EXTRA_ALLOWANCES`:

- `name` = label van de toeslag; bij `anders` = de ingevulde `anders[i]/name`.
- `description` = `<toeslag>[i]/description`; `typeCode` = typeCode uit de tabel hierboven (hardcoded).
- `line[0]` = `getLineAmountAnswer` (Bedragregel), `conditions` = `[{conditionType: Text, description: voorwaarden}]` als `voorwaarden` is ingevuld.
- `reference[]` bij `cumulatief` = `ja-cumulative`: één `{relationType: Cumulative, description: "Deze toeslag wordt opgeteld bij de andere toeslag, zie typeCode." (+ " (Toelichting: …)"), typeCode}` per **andere aangevinkte** toeslag. Bij `ja-compounding`: `{relationType: Compounding, description: "Deze toeslag wordt berekend over het resultaat na andere toeslagen, namelijk:", typeCode}` per aangevinkte compounding-checkbox waarvan de toeslag ook aangevinkt is.
- `period[]` alleen bij `toepassingsperiodes-type` = `bepaald`: per periode `{datePeriod: [{start, end}], timePeriod: {start (standaard 00:00), end (standaard 23:59)}, weekday: [{value: Monday…Sunday}]}`.
- `phaseOutScheme` = tekst van `afbouwregeling/ja-namelijk` als `afbouwregeling` = `ja`.

Bij het aanvinken wordt direct een eerste (lege) variatie `<toeslag>[0]` aangemaakt.

## \<Toeslag\> (dynamische subsectie per aangevinkte toeslag)

Er is een subsectie voor elke toeslag waarvan `<toeslag>/enabled` aangevinkt is. De vragen hieronder staan per
**variatie** `i` (herhaalbare rij `<toeslag>[i]`). Header per variatie: `<label>`, met " (variatie N)" als er meer dan
één variatie is. Knoppen: *Variatie toevoegen* (blok "Variaties", kloont de laatste variatie) en *Variatie
verwijderen* (vanaf de tweede variatie). Hulptekst bij "Variaties": *"Zijn er variaties van deze toeslag,
bijvoorbeeld met andere bedragen voor andere toepassingsperioden? Voeg dan een variatie toe."*

### Variatie

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Titel | `<toeslag>[i]/name` | tekst | — | alleen bij `anders` (`showNameInput`) | | ja | `name` |
| Omschrijving van deze variatie | `<toeslag>[i]/description` | tekst (textarea) | — | meer dan 1 variatie | ja | ja | `description` |
| *Bedragregel* — Hoe wordt de toeslag uitgekeerd? | `<toeslag>[i]/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | standaard (alle opties) | — | | ja | `line[0]` |
| Onder welke voorwaarden geldt de toeslag? Of wanneer is er sprake van deze toeslag? ³ | `<toeslag>[i]/voorwaarden` | tekst (textarea) | — | — | ja | ja | `line[0].conditions[]` (Text) |
| Is deze toeslag cumulatief? | `<toeslag>[i]/cumulatief` | radio | Ja, toeslagen worden opgeteld → `ja-cumulative` · Ja, deze toeslag wordt berekend over het resultaat na andere toeslagen, namelijk: → `ja-compounding` · Nee → `nee` | — | | ja | `reference[]` |
| ↳ Toelichting | `<toeslag>[i]/cumulatief/ja-cumulative/namelijk` | tekst (textarea) | — | `cumulatief` = `ja-cumulative` | ja | ja | in `reference[].description` |
| ↳ *\<label andere toeslag\>* (één checkbox per andere aangevinkte toeslag) | `<toeslag>[i]/compounding/<andere-toeslag>` | checkbox | — | `cumulatief` = `ja-compounding` | | ja | `reference[]` (Compounding, typeCode) |

³ Afwijkende vraagtekst bij `ploegentoeslagen`: *"Geef een omschrijving van de ploegendienst, zoals het rooster"*.
Bij `overwerktoeslag` heeft het veld een placeholder (min. hoogte 200px): *"Wanneer meer wordt gewerkt dan de
overeengekomen arbeidsomvang. / Wanneer meer wordt gewerkt dan de normale fulltime arbeidsduur van uur. / Wanneer
meer wordt gewerkt dan de normale arbeidsduur per dag van uur. / Wanneer meer wordt gewerkt dan het overeengekomen
afwijkende rooster. / Anders, namelijk:"*

Alert (warning) als er geen andere aangevinkte toeslagen zijn: *"Er zijn geen andere toeslagen gespecificeerd"*
(wordt getoond ongeacht de gekozen cumulatie-optie).

### Toepassingsperiodes

Het hele blok is zichtbaar als `showToepassingsPeriode` niet `false` is, d.w.z. alleen bij
`onregelmatigheids-toeslagen`, `toeslagen-verschoven-diensten`, `toeslagen-stand-by-consignatie-bereikbaarheidsdiensten`,
`overwerktoeslag` en `anders`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Wanneer is de toeslag geldig? (Toepassingsperiodes) | `<toeslag>[i]/toepassingsperiodes-type` | radio | Altijd → `altijd` · Bepaalde data/tijden/dagen → `bepaald` | (blok) | | ja | bepaalt `period[]` |

Alert bij `bepaald`: *"Specifieer precieze periodes (data, tijden en dagen) waarop deze toeslag van toepassing is.
U kunt meerdere periodes toevoegen als de toeslag op verschillende momenten geldig is (…)."* Bij kiezen van
`bepaald` wordt automatisch een eerste periode aangemaakt.

### Toepassingsperiode {num}

Herhaalbaar per periode `j` (rij `<toeslag>[i]/toepassingsperiodes[j]`), zichtbaar als
`<toeslag>[i]/toepassingsperiodes-type` = `bepaald`. Knoppen: *Toepassingsperiode toevoegen* /
*Toepassingsperiode verwijderen*. Sub-kopjes: "Datumbereik", "Tijdsbestek: Op welke tijden is de toeslag van
toepassing?", "Weekdagen (optioneel)".

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Startdatum | `<toeslag>[i]/toepassingsperiodes[j]/startdatum` | datum | — | (blok) en alleen bij `anders` (`showToepassingsPeriodeDatumBereik`) | ja | ja | `period[j].datePeriod[0].start` |
| Einddatum | `<toeslag>[i]/toepassingsperiodes[j]/einddatum` | datum | — | (blok) en alleen bij `anders` | ja | ja | `period[j].datePeriod[0].end` |
| Starttijd | `<toeslag>[i]/toepassingsperiodes[j]/starttijd` | tijd | — | (blok) | ja | ja | `period[j].timePeriod.start` (leeg → 00:00) |
| Eindtijd | `<toeslag>[i]/toepassingsperiodes[j]/eindtijd` | tijd | — | (blok) | ja | ja | `period[j].timePeriod.end` (leeg → 23:59) |
| Maandag | `<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Monday` | checkbox | — | (blok) | | ja | `period[j].weekday[] = Monday` |
| Dinsdag | `<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Tuesday` | checkbox | — | (blok) | | ja | `period[j].weekday[] = Tuesday` |
| Woensdag | `<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Wednesday` | checkbox | — | (blok) | | ja | `period[j].weekday[] = Wednesday` |
| Donderdag | `<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Thursday` | checkbox | — | (blok) | | ja | `period[j].weekday[] = Thursday` |
| Vrijdag | `<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Friday` | checkbox | — | (blok) | | ja | `period[j].weekday[] = Friday` |
| Zaterdag | `<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Saturday` | checkbox | — | (blok) | | ja | `period[j].weekday[] = Saturday` |
| Zondag | `<toeslag>[i]/toepassingsperiodes[j]/weekdagen/Sunday` | checkbox | — | (blok) | | ja | `period[j].weekday[] = Sunday` |

### Afbouwregeling

Het hele blok is zichtbaar als `showAfbouwregeling` niet `false` is, d.w.z. alleen bij `ploegentoeslagen`,
`waarnemingstoeslag`, `performancetoeslag` en `anders`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Geldt er een afbouwregeling voor deze toeslag? | `<toeslag>[i]/afbouwregeling` | radio | Ja, namelijk → `ja` · Nee → `nee` | (blok) | | ja | — |
| ↳ *(geen vraagtekst)* | `<toeslag>[i]/afbouwregeling/ja-namelijk` | tekst | — | `afbouwregeling` = `ja` | | ja | `phaseOutScheme` |

**Let op:**
- Alle toeslagen komen via `allowance_EXTRA_ALLOWANCES` achteraan in `allowance[]` (samengevoegd in `toSetuStandard`, na de vaste indexen); de `ALLOWANCE_*`-indexen van de toeslagen blijven dus leeg/ongebruikt. Volgorde = volgorde van de toeslagsoorten × variaties.
- `waarnemingstoeslag`, `performancetoeslag` en `anders` delen typeCode `EA300`; ze zijn in SETU alleen via `name` te onderscheiden. Ook in `reference[]` (cumulatief/compounding) wordt alleen de typeCode opgenomen, dus verwijzingen naar deze drie zijn niet eenduidig.
- Cumulatief (`ja-cumulative`) verwijst automatisch naar **alle** andere aangevinkte toeslagen; de gebruiker kiest hier niet welke.
- Bij toeslagen zonder datumbereik (alle behalve `anders`) wordt `datePeriod[0].start/end` toch gevuld met `toDateString(undefined)`.
- Een gekozen grondslag in de Bedragregel (`<toeslag>[i]/percentage/grondslag`) laat die grondslag verschijnen in [15 Grondslagen](15_grondslagen.md); daar kan per grondslag ook per toeslagsoort (`grondslag/<code>/toeslag-<toeslag>`) worden aangegeven welke toeslagen meetellen (via typeCode).
- `geen-toeslagen` heeft geen SETU-mapping en sluit de andere checkboxes niet uit.

## Uitgeschakeld in de code

Niets uitgecommentarieerd in deze sectie.

---

**Telling:** 32 tekst/getal · 2 datum · 10 tijd · 18 radio/keuzelijst · 54 checkbox (116 vragen) + 9 Bedragregels, 14 alerts.
Geteld per toeslagsoort (1 variatie, 1 toepassingsperiode), met de compounding-checkboxes als 1 per toeslag en de
10 checkboxes van het keuzeblok; alerts = 9 × "geen andere toeslagen" + 5 × toepassingsperiode-uitleg.
