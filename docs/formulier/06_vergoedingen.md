# 06 · Vergoedingen

Bron: `src/definition/06_vergoedingen_00.tsx` + `src/definition/06_vergoedingen_mobiliteit.tsx` (webformulier v2.1.0).

**Structuur:** sectie *Vergoedingen* (`makeVergoedingen`) met zeven subsecties, in deze volgorde: Reiskostenvergoedingen ·
Vergoeding voor reisuren en -tijd · Stand-by-, piket-, consignatie- of bereikbaarheidsdiensten · (aanvullende)
zorgverzekering · Thuiswerkvergoedingen · Mobiliteitsvergoeding (de zesde subsectie wordt gemaakt door
`makeMobiliteitsvergoeding(store)`, aangeroepen binnen `makeVergoedingen` tussen Thuiswerk en Kosten) ·
Kostenvergoedingen. Herhaalbaar zijn alleen de twee "eigen vervoer"-blokken in Reiskostenvergoedingen
(`reiskostenvergoeding-eigen-vervoer[]` en `reiskostenvergoeding-zakelijke-kilometers[]`, "variaties"). De blokken voor
OV, mobiliteitsregelingen en kostenvergoedingen worden uit vaste rijdefinities gegenereerd (hieronder uitgeschreven).
Deze sectie bevat geen Bedragregels (B1): alle bedragvragen zijn per vraag handmatig gebouwd.

Tenzij anders vermeld: *Ja* → `ja` · *Nee* → `nee` ([B6](00_bouwstenen.md#b6--ja--nee)); checkboxwaarde "aangevinkt"
= `CHECKED` (`true`); `anders` = `ANDERS_NAMELIJK` ([B7](00_bouwstenen.md#b7--anders-namelijk)). Alle regelingen
krijgen `origin.type = Unknown` ([B10](00_bouwstenen.md#b10--vaste-setu-standaardwaarden-van-het-formulier)). SETU
wordt alleen gevuld voor vragen die zichtbaar zijn en een waarde hebben.

## Reiskostenvergoedingen

### Welke reiskostenvergoeding(en) kent jouw onderneming?

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Welke reiskostenvergoeding(en) kent jouw onderneming? (meerdere opties mogelijk) — Reiskostenvergoeding woon- werk verkeer eigen auto / fiets etc. | `welke-reiskostenvergoedingen-kent-jouw-onderneming/eigen-vervoer` | checkbox | — | — | | | — |
| Reiskostenvergoeding woon- werk verkeer OV | `welke-reiskostenvergoedingen-kent-jouw-onderneming/ov` | checkbox | — | — | | | — |
| Reiskostenvergoeding zakelijke kilometers (werk – werk) | `welke-reiskostenvergoedingen-kent-jouw-onderneming/zakelijke-kilometers` | checkbox | — | — | | | — |
| Reiskostenvergoeding zakelijke kilometers OV (werk – werk) | `welke-reiskostenvergoedingen-kent-jouw-onderneming/zakelijke-kilometers-ov` | checkbox | — | — | | | — |
| Andere reiskostenvergoeding | `welke-reiskostenvergoedingen-kent-jouw-onderneming/andere-reiskostenvergoeding` | checkbox | — | — | | | — |

### Eigen vervoer (herhaalbare variaties)

Twee blokken, elk gegenereerd uit `eigenVervoerRows`:

| `<p>` (slug-prefix) | Bloktitel (= SETU `name`) | Zichtbaar als (checkbox aangevinkt) |
|---|---|---|
| `reiskostenvergoeding-eigen-vervoer` | Reiskostenvergoeding woon- werk verkeer eigen auto / fiets / bromfiets / anders. | `welke-reiskostenvergoedingen-kent-jouw-onderneming/eigen-vervoer` |
| `reiskostenvergoeding-zakelijke-kilometers` | Reiskostenvergoeding zakelijke kilometers (werk – werk) eigen vervoer | `welke-reiskostenvergoedingen-kent-jouw-onderneming/zakelijke-kilometers` |

Per prefix is `<p>` een lijst van variaties (`<p>[i]`); bij opbouw wordt een lege lijst aangevuld tot één lege rij
(`[{}]`). Elke variatie is een eigen blok met dezelfde titel. Knop: *Variatie toevoegen* (alleen onder de laatste
variatie; kopieert de antwoorden van de laatste variatie) en *Variatie verwijderen* (alleen als er > 1 variatie is).
Hulptekst bij toevoegen: *"Zijn er variaties van deze vergoeding, bijvoorbeeld andere bedragen per vervoersmiddel?
Voeg dan een variatie toe."* Bij > 1 variatie staat bij de voorwaarden: *"Vul hier minimaal het vervoersmiddel in
waarvoor deze variatie geldt."*

Het hele blok is zichtbaar als de bijbehorende checkbox (tabel hierboven) is aangevinkt.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `<p>[i]/type` | radio | € 0,23 per kilometer → `standaard-tarief` · Andere vergoeding per kilometer → `ander-tarief-per-km` · Vergoeding per tijdvak → `per-tijdvak` · Anders, namelijk: → `anders` | (blok) | | ja | `allowance_EXTRA_ALLOWANCES` (push) — bouwt AllowanceArrangement {name, typeCode EA103, line[0]} |
| ↳ namelijk … per kilometer | `<p>[i]/ander-tarief-per-km/bedrag` | getal (€) | — | `<p>[i]/type` = `ander-tarief-per-km` | | ja | `line[0].amount.value` |
| ↳ namelijk | `<p>[i]/per-tijdvak/bedrag` | getal (€) | — | `<p>[i]/type` = `per-tijdvak` | | ja | `line[0].amount.value` |
| ↳ per | `<p>[i]/per-tijdvak/type` | keuzelijst | Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` | `<p>[i]/type` = `per-tijdvak` | | ja | `line[0].interval.unitCode` |
| ↳ *(anders, namelijk)* | `<p>[i]/anders/namelijk` | tekst (textarea) | — | `<p>[i]/type` = `anders` | | ja | achter `name`: "… Anders, namelijk: <tekst>" |
| Voor deze vergoeding gelden de volgende voorwaarden: | `<p>[i]/voorwaarden` | tekst (textarea) | — | (blok) | | ja | `line[0].conditions[0]` (Text) |

SETU per variatie: `name` = bloktitel, `typeCode: EA103`, `line[0].amount` = {value, `unitCode: Euro`,
`baseAmount.unitCode: Fixed`}, `interval` standaard 1 × `Kilometer`:
- `standaard-tarief` → `amount.value = 0.23` (vast in de code);
- `ander-tarief-per-km` → bedrag uit `…/ander-tarief-per-km/bedrag`;
- `per-tijdvak` → bedrag uit `…/per-tijdvak/bedrag`, interval 1 × `…/per-tijdvak/type`;
- `anders` → `name` = titel + " Anders, namelijk: " + tekst, `line: [{conditions}]` (geen bedrag).

**Let op:** deze regelingen hebben géén vaste index; ze worden in `allowance_EXTRA_ALLOWANCES` verzameld en na
afloop achteraan in `allowance[]` geplaatst (na alle vaste indexen). Er is geen onderscheid tussen woon-werk en
werk-werk behalve via `name` (beide EA103). In de broncode staan de sub-slugs als `[<p>, i, "/ander-tarief-per-km/bedrag"]`
(met voorloop-slash); de `allowanceIndex` (`ALLOWANCE_TRAVEL_HOME_WORK_OWN` / `…_WORK_WORK_OWN`) is uitgecommentarieerd.

### OV (woon-werk en werk-werk)

Twee blokken, gegenereerd uit een vaste lijst:

| `<p>` (slug-prefix) | Bloktitel (= SETU `name`) | Zichtbaar als (checkbox aangevinkt) | SETU-index |
|---|---|---|---|
| `reiskostenvergoeding-ov` | Reiskostenvergoeding woon- werk verkeer OV | `welke-reiskostenvergoedingen-kent-jouw-onderneming/ov` | `ALLOWANCE_TRAVEL_HOME_WORK_OV` |
| `reiskostenvergoeding-zakelijke-kilometers-ov` | Reiskostenvergoeding werk-werk verkeer OV | `welke-reiskostenvergoedingen-kent-jouw-onderneming/zakelijke-kilometers-ov` | `ALLOWANCE_TRAVEL_WORK_WORK_OV` |

Het hele blok is zichtbaar als de bijbehorende checkbox is aangevinkt.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `<p>-type` | radio | Volledige vergoeding van de gemaakte kosten → `volledige-vergoeding` · Vergoeding per kilometer, namelijk: → `per-kilometer` · Vergoeding per rit, namelijk: → `per-rit` · Vergoeding per traject, namelijk: → `per-traject` · Anders, namelijk: → `anders` | (blok) | | | `allowance[<index>]` — bouwt AllowanceArrangement {name, typeCode EA103, line[0]} |
| ↳ *(bedrag per kilometer)* | `<p>-type/per-kilometer/bedrag` | getal (€) | — | `<p>-type` = `per-kilometer` | | | `line[0].amount.value` |
| ↳ *(bedrag per rit)* | `<p>-type/per-rit/bedrag` | getal (€) | — | `<p>-type` = `per-rit` | | | `line[0].amount.value` |
| ↳ *(bedrag per traject)* | `<p>-type/per-traject/bedrag` | getal (€) | — | `<p>-type` = `per-traject` | | | `line[0].amount.value` |
| ↳ *(anders, namelijk)* | `<p>-type/anders/namelijk` | tekst (textarea) | — | `<p>-type` = `anders` | | | achter `name` |
| Voor deze vergoeding gelden de volgende voorwaarden: | `<p>-voorwaarden` | tekst (textarea) | — | (blok) | | | `line[0].conditions[0]` (Text) |

SETU: `amount` {unitCode `Euro`, `baseAmount.unitCode: Fixed`}, standaard interval 1 × `Kilometer`:
- `volledige-vergoeding` → `amount.value = 100`, `unitCode: Percentage` (baseAmount blijft `Fixed`);
- `per-kilometer` → interval `Kilometer`; `per-rit` → interval `Item`; `per-traject` → interval `Route`;
- `anders` → `name` = titel + " Anders, namelijk: " + tekst, `line: [{conditions}]`.

**Let op:** "per rit" wordt als interval `Item` (niet `Trip`) geëxporteerd; "volledige vergoeding" als 100 % met
`baseAmount.unitCode: Fixed`.

### Andere reiskostenvergoeding

Het hele blok is zichtbaar als `welke-reiskostenvergoedingen-kent-jouw-onderneming/andere-reiskostenvergoeding` is aangevinkt.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Andere reiskostenvergoedingen, namelijk: | `andere-reiskostenvergoeding-namelijk` | tekst (textarea) | — | (blok) | | | `allowance[ALLOWANCE_TRAVEL_OTHER]` — {name "Andere reiskostenvergoedingen, namelijk: <tekst>", typeCode EA103} (geen `line`) |

## Vergoeding voor reisuren en -tijd

### Vergoeding voor reisuren en -tijd

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ken je een vergoeding voor reisuren of reistijd? | `vergoeding-reistijd` | radio | Ja, namelijk percentage van → `percentage` · Ja, namelijk een vaste vergoeding van → `vaste-vergoeding` · Ja, namelijk: → `anders` · Nee → `nee` | — | | | `allowance[ALLOWANCE_REISKOSTEN]` — bouwt AllowanceArrangement {name, typeCode HT600, line[0]}; `nee` → niets |
| ↳ Percentage | `vergoeding-reistijd/percentage/percentage` | getal (%) | — | `vergoeding-reistijd` = `percentage` | | | `line[0].amount.value` (`unitCode: Percentage`) |
| ↳ van | `vergoeding-reistijd/percentage/van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `vergoeding-reistijd` = `percentage` | | | `line[0].amount.baseAmount.unitCode` |
| ↳ per (tijdvak) | `vergoeding-reistijd/percentage/tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` | `vergoeding-reistijd` = `percentage` | | | `line[0].interval.unitCode` |
| ↳ *(bedrag)* | `vergoeding-reistijd/vaste-vergoeding/value` | getal (€) | — | `vergoeding-reistijd` = `vaste-vergoeding` | | | `line[0].amount.value` (`Euro`, `baseAmount: Fixed`) |
| ↳ per | `vergoeding-reistijd/vaste-vergoeding/per` | keuzelijst | Kilometer → `Kilometer` · Route → `Route` · Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Maand → `Month` · Week → `Week` · Jaar → `Year` | `vergoeding-reistijd` = `vaste-vergoeding` | | | `line[0].interval.unitCode` |
| ↳ *(namelijk)* | `vergoeding-reistijd/anders/namelijk` | tekst (textarea) | — | `vergoeding-reistijd` = `anders` | | | `name` = "Reisuren: <tekst>", `line: [{conditions}]` |

Hulptekst: *"Het gaat hier om een vergoeding van de reisuren of -tijd die niet als normale werktijd wordt beschouwd."*

Namen in SETU: "Reisuren: percentage" / "Reisuren: vaste vergoeding" / "Reisuren: <tekst>".

### Voorwaarden

Het hele blok is zichtbaar als `vergoeding-reistijd` ≠ `nee` (dus ook als er nog niets gekozen is).

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Voor deze vergoeding gelden de volgende voorwaarden: | `vergoeding-reistijd_voorwaarden` | tekst (textarea) | — | (blok) | | | `line[0].conditions[0]` (Text) van `allowance[ALLOWANCE_REISKOSTEN]` |

**Let op:** de SETU-index heet `ALLOWANCE_REISKOSTEN`, maar bevat de reisuren-/reistijdvergoeding (HT600).

## Vergoeding voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent je een vergoeding voor de tijd die de werknemer stand-by of bereikbaar moet zijn? | `vergoeding-stand-by-piket-consignatie-bereikbaarheidsdiensten` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | — | | | — |

Hulptekst: *"Het gaat hier om de vergoeding voor de uren die de medewerker bereikbaar is om te komen werken. Dit is
anders dan de toeslagen voor de uren die worden gewerkt nadat de werknemer vanuit de stand-by- consignatie- of
bereikbaarheidsdienst is opgeroepen om te komen werken."*

### Welke vergoeding kent jouw onderneming voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten?

Het hele blok (en het voorwaardenblok) is zichtbaar als `vergoeding-stand-by-piket-consignatie-bereikbaarheidsdiensten` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `type-vergoeding-stand-by` | radio | Vaste vergoeding per tijdvak, namelijk: → `vergoeding-per-tijdvak` · Percentage per tijdvak, namelijk: → `percentage-per-tijdvak` · Anders, namelijk: → `anders` | (blok) | | | `allowance[ALLOWANCE_STANDBY]` — bouwt AllowanceArrangement {name, typeCode HT602, line[0]} |
| ↳ Bedrag | `type-vergoeding-stand-by/vergoeding-per-tijdvak/bedrag` | getal (€ als postfix) | — | `type-vergoeding-stand-by` = `vergoeding-per-tijdvak` | | | `line[0].amount.value` (`Euro`, `baseAmount: Fixed`) |
| ↳ per (tijdvak) | `type-vergoeding-stand-by/vergoeding-per-tijdvak/tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` · Dienst → `Shift` | `type-vergoeding-stand-by` = `vergoeding-per-tijdvak` | | | `line[0].interval.unitCode` |
| ↳ Percentage | `type-vergoeding-stand-by/percentage-per-tijdvak/percentage` | getal (%) | — | `type-vergoeding-stand-by` = `percentage-per-tijdvak` | | | `line[0].amount.value` (`Percentage`) |
| ↳ van: | `type-vergoeding-stand-by/percentage-per-tijdvak/van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `type-vergoeding-stand-by` = `percentage-per-tijdvak` | | | `line[0].amount.baseAmount.unitCode` |
| ↳ per (tijdvak) | `type-vergoeding-stand-by/percentage-per-tijdvak/tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` · Dienst → `Shift` | `type-vergoeding-stand-by` = `percentage-per-tijdvak` | | | `line[0].interval.unitCode` |
| ↳ *(anders, namelijk)* | `type-vergoeding-stand-by/anders/namelijk` | tekst (textarea) | — | `type-vergoeding-stand-by` = `anders` | | | achter `name` |
| Voor deze vergoeding gelden de volgende voorwaarden: | `voorwaarden-vergoeding-stand-by` | tekst (textarea) | — | `vergoeding-stand-by-piket-consignatie-bereikbaarheidsdiensten` = `ja` (eigen blok) | | | `line[0].conditions[0]` (Text) |

Namen in SETU: "Vergoeding voor stand-by-, piket-, consignatie- of bereikbaarheidsdiensten: vergoeding per tijdvak" /
"…: percentage per tijdvak" / "…: <tekst>".

**Let op:** de ja/nee-vraag zelf heeft geen setuPath. Bij `anders` wordt alleen {name, typeCode, origin} gemaakt,
zonder `line` — de voorwaarden gaan dan verloren in SETU.

## Vergoeding voor de (aanvullende) zorgverzekering

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ken je een vergoeding voor de (aanvullende) zorgverzekering? | `vergoeding-zorgverzekering` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | — | | | `allowance[ALLOWANCE_ZORGVERZEKERING]` — bij `ja`: AllowanceArrangement {name "Vergoeding voor de (aanvullende) zorgverzekering", typeCode EA604, line[]} |

### Hoe ziet deze vergoeding eruit?

Het hele blok is zichtbaar als `vergoeding-zorgverzekering` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Hoe ziet deze vergoeding eruit? | `vergoeding-zorgverzekering-type` | radio | Vergoeding per tijdseenheid, namelijk: → `vergoeding-per-tijdseenheid` · Anders, namelijk: → `anders` | (blok) | | | bepaalt of `line[0]` wordt gemaakt |
| ↳ Bedrag | `vergoeding-zorgverzekering-type/vergoeding-per-tijdseenheid/bedrag` | getal (€) | — | `vergoeding-zorgverzekering-type` = `vergoeding-per-tijdseenheid` | | | `line[0].amount.value` (`Euro`, `baseAmount: Fixed`) |
| ↳ per (tijdvak) | `vergoeding-zorgverzekering-type/vergoeding-per-tijdseenheid/tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` | `vergoeding-zorgverzekering-type` = `vergoeding-per-tijdseenheid` | | | `line[0].interval.unitCode` |
| ↳ *(anders, namelijk)* | `vergoeding-zorgverzekering-type/anders/namelijk` | tekst (textarea) | — | `vergoeding-zorgverzekering-type` = `anders` | | | achter `name`: "… Anders, namelijk: <tekst>" (geen `line`) |

### Minimum/maximum, naar rato en voorwaarden

Drie losse blokken, elk zichtbaar als `vergoeding-zorgverzekering-type` = `vergoeding-per-tijdseenheid`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Geldt er een minimum- of een maximumbedrag voor de vergoeding? | `vergoeding-zorgverzekering-min-max` | radio | Ja, namelijk: → `ja` · Nee → `nee` | (blok) | | | bij `ja`: min/max hieronder |
| ↳ Minimum | `vergoeding-zorgverzekering-min-max/ja/minimum` | getal (€) | — | `vergoeding-zorgverzekering-min-max` = `ja` | ja | | `line[0].amount.minValue` |
| ↳ Maximum | `vergoeding-zorgverzekering-min-max/ja/maximum` | getal (€) | — | `vergoeding-zorgverzekering-min-max` = `ja` | ja | | `line[0].amount.maxValue` |
| Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt? | `vergoeding-zorgverzekering-naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | (blok) | | | bedoeld: `line[0].amount.proportional` ¹ |
| Voor deze vergoeding gelden verder de volgende voorwaarden: | `vergoeding-zorgverzekering-voorwaarden` | tekst (textarea) | — | (blok) | | | `line[0].conditions[]` (Text) |

¹ **Let op (bug):** `convertSetuValue` leest `vergoeding-zorgerzekering-naar-rato` (tikfout, zonder "v"), terwijl de
vraag-slug `vergoeding-zorgverzekering-naar-rato` is. `proportional {partTimePercentage: true, employmentDuration:
false}` wordt daardoor nooit gezet; het antwoord staat alleen in `__webform_data__`.

## Thuiswerkvergoedingen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ken je een thuiswerkvergoeding? | `thuiswerkvergoeding` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | — | | | `allowance[ALLOWANCE_THUISWERKVERGOEDING]` — bij `ja`: AllowanceArrangement {name "Thuiswerkvergoeding", typeCode EA607/EA605, line[0]} |

### Vergoeding per tijdseenheid, namelijk:

Het hele blok is zichtbaar als `thuiswerkvergoeding` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Bedrag | `thuiswerkvergoeding/ja/vergoeding-tijdseenheid` | getal (€) | — | (blok) | | | `line[0].amount.value` (`Euro`, `baseAmount: Fixed`) |
| per (tijdvak) | `thuiswerkvergoeding/ja/tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` | (blok) | | | `line[0].interval.unitCode` |
| Voor deze vergoeding gelden de volgende voorwaarden: | `thuiswerkvergoeding/ja/voorwaarden` | tekst (textarea) | — | (blok) | ja | | `line[0].conditions[]` (Text) |
| Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt? | `thuiswerkvergoeding/ja/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | (blok) | | | `line[0].amount.proportional.partTimePercentage` (= `ja`); `employmentDuration: false` |
| Zit er een internetvergoeding besloten in de thuiswerkvergoeding? | `thuiswerkvergoeding/ja/internetvergoeding-inbegrepen` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | (blok) | | | `typeCode`: `ja` → `EA607`, anders `EA605` |
| ↳ Wordt er naast de thuiswerkvergoeding ook (aanvullend) een internetvergoeding verstrekt? | `thuiswerkvergoeding/ja/extra-internetvergoeding` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `thuiswerkvergoeding/ja/internetvergoeding-inbegrepen` = `nee` | | | `allowance[ALLOWANCE_INTERNETVERGOEDING]` — bij `ja`: AllowanceArrangement {name "Internetvergoeding", typeCode EA608, line[0]} |

### Aanvullende internetvergoeding

Het hele blok is zichtbaar als `thuiswerkvergoeding/ja/extra-internetvergoeding` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Bedrag | `thuiswerkvergoeding/ja/extra-internetvergoeding/ja/vergoeding-tijdseenheid` | getal (€) | — | (blok) | | | `allowance[ALLOWANCE_INTERNETVERGOEDING].line[0].amount.value` (`Euro`, `Fixed`) |
| tijdvak | `thuiswerkvergoeding/ja/extra-internetvergoeding/ja/tijdvak` | keuzelijst | Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` | (blok) | | | `…line[0].interval.unitCode` |
| Voor deze vergoeding gelden verder de volgende voorwaarden: | `thuiswerkvergoeding/ja/extra-internetvergoeding/ja/voorwaarden` | tekst (textarea) | — | (blok) | | | `…line[0].conditions[]` (Text) |
| Wordt de internetvergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt? | `thuiswerkvergoeding/ja/extra-internetvergoeding/ja/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | (blok) | | | `…line[0].amount.proportional.partTimePercentage` |

**Let op:** een internetvergoeding die ín de thuiswerkvergoeding zit, is in SETU alleen zichtbaar via typeCode
`EA607` (i.p.v. `EA605`); een aparte internetvergoeding (EA608) komt op een eigen index.

## Mobiliteitsvergoeding

Bron: `makeMobiliteitsvergoeding(store)` (`06_vergoedingen_mobiliteit.tsx`), zesde subsectie van `makeVergoedingen`.

### Ken je een mobiliteitsregeling, bijvoorbeeld een regeling voor een leaseauto of -fiets of OV, dan wel een mobiliteitsvergoeding?

Eén blok met vragensets per regeling uit `regelingRows`:

| `<r>` (slug) | Label (= SETU `name`) | Alternatief? | SETU-index | typeCode |
|---|---|---|---|---|
| `mobiliteitsvergoeding` | Mobiliteitsvergoeding | nee | `ALLOWANCE_MOBILITEITSVERGOEDING` | `EA100` (`TODO_REPLACE_WITH_REAL_TYPECODE`) |
| `regeling-leaseauto` | Regeling leaseauto | ja | `ALLOWANCE_REGELING_LEASEAUTO` | `EA100` (`TODO_…`) |
| `regeling-leasefiets` | Regeling leasefiets | ja | `ALLOWANCE_REGELING_LEASEFIETS` | `EA100` (`TODO_…`) |
| `regeling-ov-vergoeding` | Regeling OV vergoeding | ja | `ALLOWANCE_REGELING_OV_VERGOEDING` | `EA100` (`TODO_…`) |
| `fietsregeling` | Fietsregeling | nee | `ALLOWANCE_FIETSREGELING` | `EA100` (`TODO_…`) |

Vragenset per `<r>` (de rijen met *alternatief* alleen voor leaseauto, leasefiets en OV-vergoeding):

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *\<label\>* | `mobiliteit/<r>` | checkbox | — | — | | | `allowance[<index>]` — bij aangevinkt: AllowanceArrangement {name = label, typeCode EA100, line[0] (+ line[1])} |
| ↳ Wat is de hoogte van de vergoeding / het leasebedrag? | `mobiliteit/<r>/bedrag` | getal (€) | — | `mobiliteit/<r>` aangevinkt | | | `line[0].amount.value` (`Euro`, `Fixed`) |
| ↳ Per tijdvak | `mobiliteit/<r>/tijdvak` | keuzelijst | [B2 Interval](00_bouwstenen.md#b2--interval-per) | `mobiliteit/<r>` aangevinkt | | | `line[0].interval.unitCode` |
| ↳ Voor deze regeling gelden de volgende voorwaarden: | `mobiliteit/<r>/voorwaarden` | tekst (textarea) | — | `mobiliteit/<r>` aangevinkt | ja | | `line[0].conditions[]` (Text) |
| ↳ Wordt de vergoeding naar rato uitgekeerd wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt? | `mobiliteit/<r>/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `mobiliteit/<r>` aangevinkt | | | `line[0].amount.proportional.partTimePercentage` |
| ↳ Er is een alternatieve vergoeding voor {label in kleine letters} | `mobiliteit/<r>/alternatief` | checkbox | — | `mobiliteit/<r>` aangevinkt | | | voegt `line[1]` toe |
| ↳↳ Bedrag | `mobiliteit/<r>/alternatief/bedrag` | getal (€) | — | `mobiliteit/<r>/alternatief` aangevinkt | | | `line[1].amount.value` |
| ↳↳ per tijdvak van | `mobiliteit/<r>/alternatief/tijdvak` | keuzelijst | [B2 Interval](00_bouwstenen.md#b2--interval-per) | `mobiliteit/<r>/alternatief` aangevinkt | | | `line[1].interval.unitCode` |
| ↳↳ Voor deze vergoeding gelden de volgende voorwaarden: | `mobiliteit/<r>/alternatief/voorwaarden` | tekst (textarea) | — | `mobiliteit/<r>/alternatief` aangevinkt | ja | | `line[1].conditions[1]` (Text) |
| ↳↳ Wordt de vergoeding naar rato uitgekeerd wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt? | `mobiliteit/<r>/alternatief/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `mobiliteit/<r>/alternatief` aangevinkt | | | `line[1].amount.proportional.partTimePercentage` |

**Let op:** alle vijf regelingen krijgen de placeholder-typeCode `EA100`; onderscheid alleen via index en `name`. De
alternatieve regel (`line[1]`) krijgt altijd als eerste conditie de vaste tekst "Alternatieve vergoeding voor
<label>". `proportional.employmentDuration` is altijd `false`. Er is geen "geen"-optie.

## Kostenvergoedingen

### Welke kostenvergoedingen ken je verder? (meerdere opties mogelijk)

Eén blok met vragensets per kostenvergoeding uit `kostenVergoedingenRows`:

| `<k>` (slug) | Label (= SETU `name`) | SETU-index |
|---|---|---|
| `kostenvergoedingen/koffiegeld` | Koffiegeld | `ALLOWANCE_KOFFIEGELD` |
| `kostenvergoedingen/maaltijdvergoeding` | Maaltijdvergoeding | `ALLOWANCE_MAALTIJDVERGOEDING` |
| `kostenvergoedingen/wasvergoeding` | Wasvergoeding | `ALLOWANCE_WASVERGOEDING` |
| `kostenvergoedingen/vergoeding-bedrijfskleding-schoenen` | Vergoeding voor bedrijfskleding of schoenen | `ALLOWANCE_VERGOEDING_BEDRIJFSKLEDING_SCHOENEN` |
| `kostenvergoedingen/arbo-vergoeding` | Arbo-vergoeding | `ALLOWANCE_ARBO_VERGOEDING` |
| `kostenvergoedingen/byod-vergoeding` | BYOD (Bring Your Own Device) vergoeding | `ALLOWANCE_BYOD_VERGOEDING` |

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *\<label\>* | `<k>` | checkbox | — | — | | | `allowance[<index>]` — bij aangevinkt: AllowanceArrangement {name = label, typeCode EA100, line[0]} |
| ↳ Bedrag | `<k>/per-tijdvak/bedrag` | getal (€) | — | `<k>` aangevinkt | | | `line[0].amount.value` (`Euro`, `Fixed`) |
| ↳ per | `<k>/tijdvak` | keuzelijst | Item → `Item` · Uur → `Hour` · Dag → `Day` · Dagdeel → `DayPart` · Week → `Week` · Maand → `Month` · Jaar → `Year` | `<k>` aangevinkt | | | `line[0].interval.unitCode` |
| ↳ Voor deze vergoeding gelden de volgende voorwaarden: | `<k>/voorwaarden` | tekst (textarea) | — | `<k>` aangevinkt | ja | | `line[0].conditions[]` (Text) |
| ↳ Wordt de vergoeding naar rato toegekend wanneer er minder dan de normale fulltime arbeidsduur wordt gewerkt? | `<k>/naar-rato` | radio | [B6 Ja/Nee](00_bouwstenen.md#b6--ja--nee) | `<k>` aangevinkt | | | `line[0].amount.proportional.partTimePercentage` |
| Anders, namelijk: | `kostenvergoedingen/anders` | checkbox | — | — | | | `allowance[ALLOWANCE_VERGOEDING_ANDERS]` — {name "Kostenvergoeding anders: <tekst>", typeCode EA100} (geen `line`) |
| ↳ *(namelijk)* | `kostenvergoedingen/anders/namelijk` | tekst (textarea) | — | `kostenvergoedingen/anders` aangevinkt | | | in `name` |
| Geen | `kostenvergoedingen/geen` | checkbox | — | — | | | — |

**Let op:** *Geen* aanvinken wist de zes checkboxen `<k>` (niet `kostenvergoedingen/anders` en niet de
subvragen). Alle kostenvergoedingen hebben typeCode `EA100` (generiek), onderscheid alleen via index en `name`.

## Uitgeschakeld in de code

- Reisuren: een blok met de vraag *"Beschrijf type vergoeding per tijdseenheid:"*
  (`vergoeding-reistijd_type_vergoeding_per_tijdseenheid`, zichtbaar als `vergoeding-reistijd` ≠ `nee`).
- Eigen vervoer: de `allowanceIndex` `ALLOWANCE_TRAVEL_HOME_WORK_OWN` / `ALLOWANCE_TRAVEL_WORK_WORK_OWN` (daarom via
  `allowance_EXTRA_ALLOWANCES`).

---

**Telling:** 65 tekst/getal · 0 datum · 0 tijd · 55 radio/keuzelijst · 22 checkbox (142 vragen), 0 alerts.
Uitgesplitst: Reiskosten 19/6/5 (bij één variatie per eigen-vervoerblok; elke extra variatie +4 tekst/getal +2
radio) · Reisuren 4/4/0 · Stand-by 4/5/0 · Zorgverzekering 5/5/0 · Thuiswerk 4/7/0 · Mobiliteit 16/16/8 · Kosten
13/12/9. Geen Bedragregels.
