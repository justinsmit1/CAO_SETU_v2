# 02 · Beloning

Bron: `src/definition/02_beloning.tsx` (webformulier v2.1.0).

**Structuur:** de sectie begint met twee vaste subsecties (*Salaristabellen*, *Betaalde rusttijden en pauzes*).
Daarna volgen **per salaristabel** vijf subsecties (*Geldende periodeloon in de schalen*, *Inschaling*,
*Periodieken*, *Initiële / eenmalige verhogingen*, *Afwijkende roosters*). In het menu staat de naam van de
salaristabel erboven. Het aantal subsecties is dus 2 + 5 × het aantal salaristabellen. De antwoorden zijn genest
en herhaalbaar: `beloningen[i]` (salaristabel) → `salarisschalen[j]` → `stappen[k]`, en daarnaast
`beloningen[i]/afwijkende-roosters[r]`. In SETU wordt `beloningen[i]` → `remuneration[i]`,
`salarisschalen[j]` → `remuneration[i].salaryScale[j]` en `stappen[k]` → `…salaryScale[j].salaryStep[k]`.
Elk afwijkend rooster wordt een **extra** `remuneration` achteraan de lijst (zie
[Afwijkende roosters](#afwijkende-roosters)).

**Startwaarde in de Store:** `beloningen: [{ naam: "Standaard salaristabel", salarisschalen: [{ stappen: [{}] }] }]`.
Er is dus altijd één salaristabel met één lege schaal en één lege stap.

In de tabellen hieronder staat `i` voor de salaristabel, `j` voor de salarisschaal, `k` voor de stap en `r` voor
het afwijkende rooster.

## Salaristabellen

### Welke salaristabellen kent de onderneming?

Alert: *"Is er een nieuwe salaristabel die in de toekomst ingaat? Of zijn er om andere redenen verschillende
salaristabellen? Voeg deze dan hieronder toe."*

Herhaalbaar blok *Salaristabellen*: één rij per `beloningen[i]`. Knop: *Salaristabel toevoegen* (voegt
`{ salarisschalen: [{ stappen: [{}] }] }` toe, **zonder** naam). Knop *verwijderen* (met bevestiging
"Salaristabel verwijderen?") staat er alleen als er meer dan één salaristabel is.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam | `beloningen[i]/naam` | tekst | — | — | | ja | — |

**Let op:** de naam van de salaristabel gaat niet naar SETU. Hij wordt alleen gebruikt als menulabel en in de
keuzelijst van [03 Functiegroepen](03_functiegroepen.md). Het menulabel is de naam (of "Salaristabel {num}" als
er geen naam is) zodra er meer dan één tabel is. Bij één tabel is het altijd "Salaristabel 1".

## Betaalde rusttijden en pauzes

### Betaalde rusttijden en pauzes?

Blok *Kent jouw onderneming doorbetaalde pauzes of rusttijden?* Hulptekst: *"Met dit antwoord kunnen wij
vaststellen over welke uren recht op loon bestaat."*

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `betaalde-rusttijden-en-pauzes` | radio | Ja, namelijk: → `ja` · Nee → `nee` | — | | | `allowance[ALLOWANCE_PAID_BREAKS]`: bouwt AllowanceArrangement {name, typeCode HT400, line} |
| ↳ *(tekstvak)* | `betaalde-rusttijden-en-pauzes/ja/namelijk` | tekst (textarea) | — | `betaalde-rusttijden-en-pauzes` = `ja` | | | via de radio: `line[0].conditions[0].description` |

Alleen bij `ja` wordt geschreven: `name: "Betaalde rusttijden en pauzes"`, `typeCode: "HT400"`,
`origin.type: Unknown`, `line[0].interval` = 1 × `Hour`, `line[0].conditions[0]` = `{conditionType: "Text",
description: <namelijk-tekst>}`. Er is geen bedrag. Als het tekstvak leeg is, wordt de omschrijving de tekst
`"undefined"` (want de code doet `getAnswer(...) + ""`).

## Geldende periodeloon in de schalen

Herhaald per salaristabel `i` (dynamische subsectie). Alle vragen hebben Herh. = ja.

### Deze salaristabel is geldig

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| van | `beloningen[i]/geldig-vanaf` | datum | — | — | ja | ja | `remuneration[i].effectivePeriod.validFrom` |
| tot | `beloningen[i]/geldig-per` | datum | — | — | ja | ja | `remuneration[i].effectivePeriod.validTo` |
| Deze salaristabel is van toepassing in de volgende situatie: (bijvoorbeeld bij werken in een vijf of drie ploegendienst) | `beloningen[i]/voorwaarden` | tekst (textarea) | — | alleen bij de 2e salaristabel en verder (`i` > 0) | ja | ja | `remuneration[i].conditions[BELONING_VOORWAARDE_ANDERS]` = `{conditionType: "Text", description}` |

**Let op:** de slug voor de einddatum is `geldig-per`, niet `geldig-tot`.

### Geldende periodeloon in de schalen

| Vraag | Slug | Type | Opties (label → waarde → SETU-waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Wat is de normale arbeidsduur per week? Hiermee wordt de arbeidsomvang per week bedoeld gebaseerd op een voltijdsdienstverband. | `beloningen[i]/normale-arbeidsduur` | radio | 40 uur → `40` · 38 uur → `38` · 36 uur → `36` · Anders, namelijk: → `anders` → `DONT_AUTO_SET_SETU_VALUE` | — | | ja | `remuneration[i].workDuration` = `{valuePerWeek: <getal>, amount: 1 × Hour, interval: 1 × Week}` |
| ↳ *(aantal)* | `beloningen[i]/normale-arbeidsduur-anders-namelijk` | getal (uur) | — | `normale-arbeidsduur` = `anders` | | ja | `remuneration[i].workDuration` (zelfde object) |

Hulptekst: *"Als je een arbeidsomvang over een langere duur dan een week hebt, vul dan het gemiddelde per week in."*

### Hoe is de beloning vastgesteld?

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `beloningen[i]/beloning-vastgesteld` | radio | Per maand → `per-maand` · Per vier weken → `per-vier-weken` · Per week → `per-week` · Per uur → `per-uur` | — | | ja | `remuneration[i].interval` via [B8 Werkduur-interval](00_bouwstenen.md#b8--werkduur-interval-workduration2interval) |

### Zijn in jouw arbeidsvoorwaardenregeling of cao uurlonen voor eigen werknemers vastgelegd of kent jouw cao of arbeidsvoorwaardenregeling een eenduidige berekeningsmethodiek om het maand-/periodeloon terug te rekenen naar een uurloon?

Het hele blok is zichtbaar als `beloningen[i]/beloning-vastgesteld` ≠ `per-uur` (dus ook als er nog niets is
gekozen).

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `beloningen[i]/uurlonen-vastgelegd` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) (label "Ja, namelijk:") | (blok) | | ja | — |
| ↳ *(percentage)* | `beloningen[i]/uurlonen-vastgelegd/ja/namelijk` | getal (%) | — | (blok) en `uurlonen-vastgelegd` = `ja` | | ja | `remuneration[i].hourlyWageConversion.hourlyWagePercentage` |

Hulptekst: *"Als er sprake is van een uurloonfactor dan moet deze worden omgerekend naar een percentage. Dat doe
je door de factor met 100% te vermenigvuldigen."* en *"Als jouw arbeidsvoorwaardenregeling of cao geen uurlonen
of een eenduidige berekeningsmethodiek kent, dan wordt het uurloon als volgt berekend: Maandloon / (4,35 x
normale arbeidsduur)"*.

### Welke salarisschalen kent de onderneming?

Herhaalbaar, twee niveaus diep:

- Per salarisschaal `j` een blok *Salarisschaal {num}* (num = j + 1). Knop: *Salarisschaal toevoegen* (voegt
  `{ stappen: [{}] }` toe). Knop: *Salarisschaal verwijderen* (met bevestiging "Salarisschaal verwijderen?").
  Er is geen minimum, dus alle schalen kunnen weg.
- Binnen de schaal een lijst *Stappen*, één rij per stap `k`. Knop: *Stap toevoegen* (voegt `{}` toe).
  Knop: *Stap verwijderen* (zonder bevestiging en zonder minimum).

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Schaal | `beloningen[i]/salarisschalen[j]/naam` | tekst | — | — | | ja | `remuneration[i].salaryScale[j].name` |
| Minimaal bedrag | `beloningen[i]/salarisschalen[j]/minimaal-bedrag` | getal (€, als postfix) | — | — | ja | ja | `remuneration[i].salaryScale[j].minValue` |
| Maximaal bedrag | `beloningen[i]/salarisschalen[j]/maximaal-bedrag` | getal (€, als postfix) | — | — | ja | ja | `remuneration[i].salaryScale[j].maxValue` |
| Stap / Trede | `beloningen[i]/salarisschalen[j]/stappen[k]/naam` | tekst | — | — | | ja | `remuneration[i].salaryScale[j].salaryStep[k].name` |
| Bedrag | `beloningen[i]/salarisschalen[j]/stappen[k]/bedrag` | getal (€, als postfix) | — | — | | ja | `remuneration[i].salaryScale[j].salaryStep[k].value` |

Bij export zet `addMissingDefaults()` op elke `salaryScale` `currency: EUR` en op elke `remuneration`
`origin.type: Unknown` (zie [B10](00_bouwstenen.md#b10--vaste-setu-standaardwaarden-van-het-formulier)).

**Let op:** bedragen hebben geen eigen eenheid of interval. De periode komt uit `remuneration[i].interval`
(*Hoe is de beloning vastgesteld?*). Lege schalen of stappen verdwijnen bij `clean()`. Doordat de indexen van de
array gewoon doorlopen, kan de nummering in SETU verschuiven als er een lege tussenrij is.

## Inschaling

Herhaald per salaristabel `i`.

### Inschaling

Blok *Wordt werkervaring bij de inschaling meegenomen?*

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `beloningen[i]/werkervaring-inschaling` | radio | Ja, relevante werkervaring in de sector wordt als volgt meegenomen → `ja-sector` · Ja, relevante werkervaring bij onze onderneming wordt als volgt meegenomen → `ja-onderneming` · Ja, relevante werkervaring in dezelfde functie (ongeacht de sector) wordt als volgt meegenomen → `ja-functie` · Ja, namelijk als volgt → `ja-als-volgt` · Nee → `nee` | — | | ja | `remuneration[i].salaryScale[*].careerLevel.indicator` (`true`, bij `nee` leeg) |
| ↳ *(tekstvak)* | `beloningen[i]/werkervaring-inschaling/ja-sector/namelijk` | tekst | — | `werkervaring-inschaling` = `ja-sector` | | ja | `remuneration[i].salaryScale[*].careerLevel.description` |
| ↳ *(tekstvak)* | `beloningen[i]/werkervaring-inschaling/ja-onderneming/namelijk` | tekst | — | `werkervaring-inschaling` = `ja-onderneming` | | ja | idem |
| ↳ *(tekstvak)* | `beloningen[i]/werkervaring-inschaling/ja-functie/namelijk` | tekst | — | `werkervaring-inschaling` = `ja-functie` | | ja | idem |
| ↳ *(tekstvak)* | `beloningen[i]/werkervaring-inschaling/ja-als-volgt/namelijk` | tekst | — | `werkervaring-inschaling` = `ja-als-volgt` | | ja | idem |

De omschrijving krijgt een vaste tekst vooraan, gevolgd door het antwoord:

| Keuze | `careerLevel.description` |
|---|---|
| `ja-sector` | "Relevante werkervaring in de sector wordt als volgt meegenomen: <tekst>" |
| `ja-onderneming` | "Relevante werkervaring bij onze onderneming wordt als volgt meegenomen: <tekst>" |
| `ja-functie` | "Relevante werkervaring in dezelfde functie (ongeacht de sector) wordt als volgt meegenomen: <tekst>" |
| `ja-als-volgt` | "Relevante werkervaring wordt als volgt meegenomen: <tekst>" |

**Let op:** de `setuPath` wijst naar `salaryScale[0]`, maar de conversie schrijft indicator en omschrijving naar
**alle** salarisschalen van de tabel. De vier "ja"-keuzes worden allemaal `indicator: true`; welke het was, is
alleen terug te halen uit het voorvoegsel van de omschrijving.

## Periodieken

Herhaald per salaristabel `i`.

### Periodieken

Blok *Zijn er periodieke verhogingen?*

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `beloningen[i]/periodieke-verhogingen` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | — | | ja | — |

Het tweede blok is zichtbaar als `beloningen[i]/periodieke-verhogingen` = `ja`. Het bevat voor elk van de vier
rijen hieronder dezelfde set vragen:

| Rij-slug (`<rij>`) | Label (checkbox) | SETU-index |
|---|---|---|
| `periodieke-verhogingen-minimale-duur-dienstverband` | Ja, deze zijn afhankelijk van een minimale duur dienstverband | `INDIVIDUAL_SALARY_INCREASE_RATE_DUUR_DIENSTVERBAND` (0) |
| `periodieke-verhogingen-beoordeling-werknemer` | Ja, deze zijn afhankelijk van de beoordeling van de werknemer | `INDIVIDUAL_SALARY_INCREASE_RATE_BEOORDELING_WERKNEMER` (1) |
| `periodieke-verhogingen-ja` | Ja | `INDIVIDUAL_SALARY_INCREASE_RATE_ANDERS` (2) |
| `periodieke-verhogingen-andere-verhogingen` | Nee, maar wij geven wel andere verhogingen (niet zijnde initiële / eenmalige verhogingen) aan onze werknemers | `INDIVIDUAL_SALARY_INCREASE_RATE_OVERIG` (3) |

Vragenset per rij:

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(label van de rij)* | `beloningen[i]/<rij>` | checkbox | aangevinkt → `true` | (blok) | | ja | `remuneration[i].individualSalaryIncrease[<index>]`: bouwt `{line, effectiveDate?}` |
| ↳ Wanneer wordt de periodieke of andere verhoging toegekend? | `beloningen[i]/<rij>/wanneer` | radio | Op een vast moment, namelijk: → `vast-moment` · Per gewerkt jaar → `gewerkt-jaar` · Anders, namelijk: → `anders` | `<rij>` aangevinkt | | ja | via de checkbox |
| ↳↳ *(datum)* | `beloningen[i]/<rij>/wanneer/vast-moment/namelijk` | datum | — | `<rij>/wanneer` = `vast-moment` | | ja | via de checkbox: `effectiveDate.date` |
| ↳↳ *(tekstvak)* | `beloningen[i]/<rij>/wanneer/anders/namelijk` | tekst (textarea) | — | `<rij>/wanneer` = `anders` | | ja | via de checkbox: `line.conditions[]` |
| ↳ Hoe wordt de periodieke of andere verhoging berekend? | `beloningen[i]/<rij>/berekening` | radio | Vast percentage van het loon, namelijk: → `vast-percentage` · Vast bedrag, namelijk: → `vast-bedrag` · Overeenkomstig de treden in de salaristabellen, namelijk: → `treden` · Anders, namelijk: → `anders` | `<rij>` aangevinkt | | ja | via de checkbox |
| ↳↳ *(percentage)* | `beloningen[i]/<rij>/berekening/vast-percentage/namelijk` | getal (%) | — | `<rij>/berekening` = `vast-percentage` | | ja | via de checkbox: `line.amount` |
| ↳↳ *(bedrag)* | `beloningen[i]/<rij>/berekening/vast-bedrag/namelijk` | getal (€) | — | `<rij>/berekening` = `vast-bedrag` | | ja | via de checkbox: `line.amount` |
| ↳↳ *(aantal)* | `beloningen[i]/<rij>/berekening/treden/namelijk` | getal (trede(n) per jaar) | — | `<rij>/berekening` = `treden` | | ja | via de checkbox: `line.amount` |
| ↳↳ *(tekstvak)* | `beloningen[i]/<rij>/berekening/anders/namelijk` | tekst | — | `<rij>/berekening` = `anders` | | ja | via de checkbox: `line.conditions[0].description` |

Wat de checkbox-conversie bouwt:

- `line.interval` = 1 × `Year`.
- `line.conditions[0]` = `{conditionType: "Text", description: "<label van de rij>"}`. Bij berekening `anders`
  wordt dat `"<label>: <anders-tekst>"`.
- Berekening → `line.amount`:
  - `vast-percentage`: `{value, unitCode: Percentage, baseAmount.unitCode: YearlyRate}`
  - `vast-bedrag`: `{value, unitCode: Euro, baseAmount.unitCode: Fixed}`
  - `treden`: `{value, unitCode: SalaryStep, baseAmount.unitCode: Fixed}`
  - `anders`: geen bedrag
- Wanneer:
  - `vast-moment`: `effectiveDate = {occurrenceType: Single, date}` (op het object, niet op `line`)
  - `gewerkt-jaar`: extra conditie "Wanneer wordt de verhoging toegekend: per gewerkt jaar"
  - `anders`: extra conditie "Wanneer wordt de verhoging toegekend: <tekst>"

**Let op:** `line` is hier één object en geen lijst. Alleen de checkbox heeft een `setuPath`; de subvragen worden
binnen de conversie uitgelezen, ook als ze niet zichtbaar zijn. De radio `periodieke-verhogingen` zelf gaat niet
naar SETU. Kies je `nee`, dan worden de verborgen checkboxes niet geëxporteerd.

## Initiële / eenmalige verhogingen

Herhaald per salaristabel `i`. Blok *Zijn er initiële / eenmalige verhogingen bekend?* Hulptekst: *"Als deze
later bekend worden, moeten deze alsnog worden doorgegeven en de salaristabellen worden aangepast."*

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `beloningen[i]/initiele-eenmalige-verhogingen` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) (label "Ja, namelijk:") | — | | ja | `remuneration[i].generalSalaryIncrease[0]`: bouwt `{amount, effectiveDate, description}` |
| ↳ *(type)* | `beloningen[i]/initiele-eenmalige-verhogingen/ja/type` | radio | Een vast bedrag → `Euro` · Een percentage → `Percentage` | `initiele-eenmalige-verhogingen` = `ja` | | ja | via de radio: `amount.unitCode` |
| ↳↳ *(bedrag)* | `beloningen[i]/initiele-eenmalige-verhogingen/ja/euro` | getal (€) | — | `…/ja/type` = `Euro` | | ja | via de radio: `amount.value` |
| ↳↳ *(percentage)* | `beloningen[i]/initiele-eenmalige-verhogingen/ja/percentage` | getal (%) | — | `…/ja/type` = `Percentage` | | ja | via de radio: `amount.value` |
| ↳ Ingangsdatum | `beloningen[i]/initiele-eenmalige-verhogingen/ja/geldig-vanaf` | datum | — | `initiele-eenmalige-verhogingen` = `ja` | ja | ja | via de radio: `effectiveDate = {occurrenceType: Single, date}` |
| ↳ Voorwaarden voor toekenning | `beloningen[i]/initiele-eenmalige-verhogingen/ja/beschrijving` | tekst (textarea) | — | `initiele-eenmalige-verhogingen` = `ja` | | ja | via de radio: `description` |

Alert (bij `ja`): *"Voeg de nieuwe salaristabel via "Beloning" > "Salaristabellen" toe."*

**Let op:** per salaristabel is er maar één verhoging (`generalSalaryIncrease[0]`). De waarde wordt opgehaald via
de slug `…/ja/<type in kleine letters>` (`euro` of `percentage`). `amount` heeft geen `baseAmount`.

## Afwijkende roosters

Herhaald per salaristabel `i`.

### Afwijkende roosters

Blok *Zijn er werknemers waarvoor een afwijkende arbeidsduur geldt, bijvoorbeeld omdat zij in een ploegendienst
werken of een wisselend arbeidspatroon kennen?*

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `beloningen[i]/afwijkende-arbeidsduur` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | — | | ja | `DONT_AUTO_SET_SETU_VALUE`; de conversie vult `remuneration_EXTRA_RENUMERATIONS` |

Bij `ja` wordt automatisch de eerste rij `afwijkende-roosters[0]` aangemaakt (`ensureAnswerIsArray`). Daarna
volgt het herhaalbare blok *Namelijk de volgende arbeidsduur:*, één blok per rooster `r`. Knop: *Afwijkend
rooster toevoegen* (`addAnswerRow`). Knop: *Afwijkend rooster verwijderen*, alleen bij meer dan één rooster.

Het hele blok is zichtbaar als `beloningen[i]/afwijkende-arbeidsduur` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(arbeidsduur)* | `beloningen[i]/afwijkende-roosters[r]/arbeidsduur` | getal (uur) | — | (blok) | | ja | extra remuneration: `workDuration.valuePerWeek` én `workDuration.amount.value` |
| Per | `beloningen[i]/afwijkende-roosters[r]/arbeidsduur-per` | keuzelijst | Per maand → `per-maand` · Per vier weken → `per-vier-weken` · Per week → `per-week` · Per uur → `per-uur` | (blok) | | ja | extra remuneration: `workDuration.interval` via [B8](00_bouwstenen.md#b8--werkduur-interval-workduration2interval) |
| in de volgende situatie: (bijvoorbeeld bij werken in een vijf of drie ploegendienst) | `beloningen[i]/afwijkende-roosters[r]/in-situatie` | tekst (textarea) | — | (blok) | | ja | extra remuneration: `conditions[]` += `{conditionType: "Text", description}` |
| Zijn in jouw arbeidsvoorwaardenregeling of cao uurlonen vastgelegd of kent jouw cao of arbeidsvoorwaardenregeling een eenduidige berekeningsmethodiek om het maand-/periodeloon terug te rekenen naar een uurloon voor de werknemer waarvoor een afwijkende arbeidsduur geldt? *(header)* | `beloningen[i]/afwijkende-roosters[r]/uurloon-factor-vastgelegd` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) (label "Ja, namelijk:") | (blok) | | ja | — |
| ↳ *(percentage)* | `beloningen[i]/afwijkende-roosters[r]/uurloon-factor` | getal (%) | — | (blok) en `uurloon-factor-vastgelegd` = `ja` | | ja | extra remuneration: `hourlyWageConversion.hourlyWagePercentage` |

Hulptekst bij de uurloonfactor: gelijk aan die bij *uurlonen-vastgelegd* (factor × 100%). Alert: *"Als jouw
arbeidsvoorwaarden of cao geen uurlonen of een eenduidige berekenings- methodiek kent, dan wordt het uurloon voor
de werknemer waarvoor een afwijkende arbeidsduur geldt als volgt berekend: maandloon / (4,35 x normale
arbeidsduur)"*.

**Werking van `remuneration_EXTRA_RENUMERATIONS`:** alleen `afwijkende-arbeidsduur` heeft een `setuPath`. De
vragen per rooster hebben er geen. De conversie van de radio maakt per rooster `r` een **diepe kopie** van
`remuneration[i]` zoals die op dat moment is opgebouwd. Daarin zitten al effectivePeriod, conditions, workDuration,
interval, hourlyWageConversion, salaryScale (met careerLevel), individualSalaryIncrease en generalSalaryIncrease.
Op die kopie worden de rooster-antwoorden toegepast en de kopie gaat naar `setuData.remuneration_EXTRA_RENUMERATIONS`.
Aan het eind van `toSetuStandard()` worden deze kopieën **achteraan** `remuneration[]` gezet en wordt de hulplijst
verwijderd. Tabel 0 met twee roosters en tabel 1 zonder roosters wordt dus: `remuneration[0]`, `remuneration[1]`,
`remuneration[2]` (= kopie tabel 0, rooster 0), `remuneration[3]` (= kopie tabel 0, rooster 1).

**Let op:**
- `workDuration` wordt alleen aangepast als de basistabel al een `workDuration` heeft. `valuePerWeek` krijgt het
  ingevulde aantal uren, ook als *Per* niet `per-week` is. Dat is inconsistent en geeft verlies bij terugmappen.
- Bij uurloonfactor `nee` of leeg blijft het `hourlyWagePercentage` van de basistabel staan.
- De kopieën worden gemaakt vóórdat [03 Functiegroepen](03_functiegroepen.md) `positionProfileReference` toevoegt.
  Extra remunerations krijgen dus **geen** koppeling met een functiegroep.
- Een extra remuneration heeft geen eigen naam of kenmerk. Je herkent hem alleen aan de extra `conditions`-regel
  (in-situatie).

## Uitgeschakeld in de code

Er zijn geen uitgecommentarieerde vragen. De tak in *Salarisschaal toevoegen* die een nieuwe salaristabel maakt
als er geen enkele is (`beloningen.length === 0`), wordt nooit bereikt: de subsectie bestaat alleen als er minstens
één salaristabel is.

---

**Telling:** 40 tekst/getal · 7 datum · 0 tijd · 19 radio/keuzelijst · 4 checkbox (70 vragen), 3 alerts.
Geteld per salaristabel, met één salarisschaal, één stap en één afwijkend rooster. De vier periodiek-rijen zijn
volledig uitgeschreven meegeteld. `voorwaarden` (alleen vanaf de 2e tabel) telt als 1.
