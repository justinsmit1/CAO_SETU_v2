# 09 · Verlof

Bron: `src/definition/09_verlof.tsx` (webformulier v2.1.0).

**Structuur:** acht subsecties: ADV/ATV (met een herbruikbaar toekenningsblok dat vier keer voorkomt), vakantiedagen
(met drie herhaalbare lijsten extra dagen), bijzonder verlof (herhaalbare variaties), tijd voor tijd, aanvulling
Wazo (zeven checkboxregels uit een lijst), verplichte aanwending verlof, feestdagen (incl. persoonlijke
feestdagen) en waarde van een (verlof)dag. Bijna alles komt terecht in de SETU-lijst `leave` op een vaste index
(zie [B11](00_bouwstenen.md#b11--vaste-posities-in-setu-lijsten-constantsts)); bijzonder verlof wordt via
`leave_EXTRA_LEAVES` achteraan toegevoegd en tijd voor tijd gaat naar `allowance`.

**Let op (hele sectie):**
- `toSetuStandard()` begint met `setuData = { leave: [{}] }`. Vragen met setuPath `["leave", LEAVE_X]` schrijven
  direct naar `leave[LEAVE_X]`; ontbrekende tussenliggende indexen worden met lege containers opgevuld.
- Na het doorlopen van alle vragen wordt `setuData.leave_EXTRA_LEAVES` (alleen gevuld door **Bijzonder verlof**)
  achter `leave` geplakt en daarna verwijderd.
- Daarna verwijdert `clean()` alle lege elementen uit arrays (`splice`). De vaste `LEAVE_*`-indexen zijn dus
  **niet** de indexen in de uiteindelijke export: alleen de volgorde blijft behouden. Bij terugmappen moet je op
  `name` (vaste teksten zoals "Vakantiedagen", "Feestdagen", "ADV / ATV regeling: …") herkennen, niet op positie.
- `LEAVE_BIJZONDER_VERLOF` wordt nergens gebruikt.
- `convertSetuValue` wordt alleen aangeroepen als de vraag zichtbaar is en een waarde heeft.

## ADV of ATV in tijd of in geld

### ADV of ATV in tijd of in geld

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Is er een betaalde ADV / ATV regeling van toepassing? | `adv-regeling` | radio | Ja, namelijk: → `ja` · Nee → `nee` | — | | | `leave[LEAVE_ADV]` — bouwt Leave {name "ADV / ATV regeling: <namelijk>", origin, workingHoursReduction: [ADV-toekenning `adv-regeling`]} |
| ↳ *(zonder vraagtekst)* | `adv-regeling_ja_namelijk` | tekst | — | `adv-regeling` = `ja` | | | in `name` van `leave[LEAVE_ADV]` |

### Hoe wordt ADV / ATV toegekend?

Toekenningsblok met prefix `adv-regeling`; zie [ADV-toekenningsblok](#adv-toekenningsblok-makeadvtoegekend).
Het hele blok is zichtbaar als `adv-regeling` = `ja`.

### Geldt er een aanvullende ADV / ATV regeling voor specifieke werknemers?

Het hele blok is zichtbaar als `adv-regeling` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `adv-aanvullende-regeling` | radio | Ja → `ja` · Nee → `nee` | (blok) | | | — |

### Voor welke werknemers geldt een aanvullende ADV / ATV regeling?

Het hele blok is zichtbaar als `adv-aanvullende-regeling` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ouderen, namelijk: | `adv-aanvullende-ouderen` | checkbox | — | (blok) | | | `leave[LEAVE_ADV_AANVULLING_OUDEREN]` — Leave {name "Aanvullende ADV / ATV regeling voor ouderen: <namelijk>", origin, workingHoursReduction: [ADV-toekenning `adv-aanvullende-ouderen`]} |
| ↳ *(zonder vraagtekst)* | `adv-aanvullende-ouderen_namelijk` | tekst | — | `adv-aanvullende-ouderen` aangevinkt | | | in `name` |
| Op basis van duur dienstverband, namelijk: | `adv-aanvullende-duur-dienstverband` | checkbox | — | (blok) | | | `leave[LEAVE_ADV_AANVULLING_DUUR_DIENSTVERBAND]` — Leave {name "Aanvullende ADV / ATV regeling voor duur dienstverband: <namelijk>", origin, workingHoursReduction: [ADV-toekenning `adv-aanvullende-duur-dienstverband`]} |
| ↳ *(zonder vraagtekst)* | `adv-aanvullende-duur-dienstverband_namelijk` | tekst | — | `adv-aanvullende-duur-dienstverband` aangevinkt | | | in `name` |
| Anders, namelijk: | `adv-aanvullende-anders` | checkbox | — | (blok) | | | `leave[LEAVE_ADV_AANVULLING_ANDERS]` — Leave {name "Aanvullende ADV / ATV regeling voor anders: <namelijk>", origin, workingHoursReduction: [ADV-toekenning `adv-aanvullende-anders`]} ¹ |
| ↳ *(zonder vraagtekst)* | `adv-aanvullende-anders-namelijk` | tekst | — | `adv-aanvullende-anders` aangevinkt | | | — ¹ |

¹ **Let op (bug):** het tekstveld heet `adv-aanvullende-anders-namelijk` (met streepje), maar de conversie leest
`adv-aanvullende-anders_namelijk` (met underscore). De "namelijk"-tekst komt dus niet in SETU; de naam wordt
"…voor anders: undefined".

### Aanvullende toekenningsblokken

Drie extra toekenningsblokken (zie [ADV-toekenningsblok](#adv-toekenningsblok-makeadvtoegekend)):

| Prefix `<p>` | Bloktitel | Blok zichtbaar als | SETU-doel |
|---|---|---|---|
| `adv-regeling` | Hoe wordt ADV / ATV toegekend? | `adv-regeling` = `ja` | `leave[LEAVE_ADV].workingHoursReduction[0]` |
| `adv-aanvullende-ouderen` | Hoe wordt de aanvullende ADV / ATV voor ouderen toegekend? | `adv-aanvullende-ouderen` aangevinkt | `leave[LEAVE_ADV_AANVULLING_OUDEREN].workingHoursReduction[0]` |
| `adv-aanvullende-duur-dienstverband` | Hoe wordt de aanvullende ADV / ATV op basis van duur dienstverband toegekend? | `adv-aanvullende-duur-dienstverband` aangevinkt | `leave[LEAVE_ADV_AANVULLING_DUUR_DIENSTVERBAND].workingHoursReduction[0]` |
| `adv-aanvullende-anders` | Hoe wordt de aanvullende ADV / ATV op basis van andere voorwaarden toegekend? | `adv-aanvullende-anders` aangevinkt | `leave[LEAVE_ADV_AANVULLING_ANDERS].workingHoursReduction[0]` |

**Let op:** de blokvoorwaarden van de drie aanvullende blokken kijken alleen naar hun checkbox; die checkboxen
staan zelf in een blok dat alleen zichtbaar is bij `adv-aanvullende-regeling` = `ja`.

### ADV-toekenningsblok (`makeAdvToegekend`)

Wordt vier keer gebruikt, met prefix `<p>` uit de tabel hierboven. De conversie (`setuAdv(<p>)`) levert één
WorkingHoursReduction-object.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `<p>/toekenning` | radio | In tijd (dagen) → `tijd-dagen` · In tijd (uren) → `tijd-uren` · In geld → `geld` | (blok) | | | bepaalt de variant |
| ↳ dagen | `<p>/toekenning/tijd-dagen/aantal` | getal | — | `<p>/toekenning` = `tijd-dagen` | | | `amount.value`, `unitCode: Day`, `baseAmount.unitCode: Fixed` |
| ↳ per | `<p>/toekenning/tijd-dagen/tijdvak` | keuzelijst | Dag → `Day` · Week → `Week` · Maand → `Month` · Jaar → `Year` | `<p>/toekenning` = `tijd-dagen` | | | `interval.unitCode` (`interval.value` = 1) |
| ↳ uren | `<p>/toekenning/tijd-uren/aantal` | getal | — | `<p>/toekenning` = `tijd-uren` | | | `amount.value`, `unitCode: Hour`, `baseAmount.unitCode: Fixed` |
| ↳ per | `<p>/toekenning/tijd-uren/tijdvak` | keuzelijst | Dag → `Day` · Week → `Week` · Maand → `Month` · Jaar → `Year` | `<p>/toekenning` = `tijd-uren` | | | `interval.unitCode` (`interval.value` = 1) |
| ↳ percentage | `<p>/toekenning/geld/percentage` | getal (postfix %) | — | `<p>/toekenning` = `geld` | | | `amount.value`, `unitCode: Percentage` |
| ↳ van | `<p>/toekenning/geld/van` | keuzelijst | [B3 Loonbasis](00_bouwstenen.md#b3--loonbasis-van) | `<p>/toekenning` = `geld` | | | `amount.baseAmount.unitCode`; `interval.unitCode` via [B9](00_bouwstenen.md#b9--loonbasis--interval-baseamountunitcodetointerval) |

**Let op:**
- Bij `geld` wordt het interval afgeleid uit de loonbasis (B9). Voor `FourWeeklyRate` staat er niets in B9, dus
  `interval.unitCode` blijft leeg.
- `setuAdv` bevat een tak voor `geld/van` = `percentageFixedAmount` met slugs `<p>/toekenning/geld/van/percentage/amount`
  en `<p>/toekenning/geld/van/percentage/tijdvak`. Die waarde en die velden bestaan niet in het formulier, dus die
  code wordt nooit uitgevoerd.

## Vakantiedagen

### Hoeveel vakantiedagen worden er toegekend bij een fulltime dienstverband?

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Aantal | `vakantiedagen/aantal` | getal | — | — | | | `leave[LEAVE_VAKANTIE]` — bouwt Leave {name "Vakantiedagen", origin, paidLeave: [basisregel, + extra regels]} |
| *(vraagtekst " ")* | `vakantiedagen/type` | keuzelijst (geen lege optie) | dagen → `Day` · uren → `Hour` | — | | | `paidLeave[0].amount.unitCode` |
| per: | `vakantiedagen/tijdvak` | keuzelijst | Dag → `Day` · Week → `Week` · Maand → `Month` · Jaar → `Year` | — | | | `paidLeave[*].interval.unitCode` (alle regels) |

Basisregel: `paidLeave[0]` = {amount {value: aantal, unitCode: type, baseAmount.unitCode Fixed}, interval {1, tijdvak},
conditions: []}.

### Gelden er extra vakantiedagen voor specifieke werknemers of omstandigheden?

Blok is `optional: true`. Drie checkboxen, elk met een eigen herhaalbare lijst regels. Aanvinken maakt de lijst aan
met één lege regel (`ensureAnswerIsArray`); per regel knop: Regel verwijderen; onder de lijst knop: Regel toevoegen.
Regels en knoppen zijn alleen zichtbaar als de bijbehorende checkbox is aangevinkt.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ja, extra dagen vanaf een bepaalde leeftijd, namelijk: | `extra-vakantiedagen-specifiek/dagen-leeftijd` | checkbox | — | — | ja (blok) | | extra `paidLeave`-regels in `leave[LEAVE_VAKANTIE]` |
| ↳ vanaf … jaar oud | `extra-vakantiedagen/leeftijd[i]/leeftijd` | getal (postfix jaar) | — | `extra-vakantiedagen-specifiek/dagen-leeftijd` aangevinkt | | ja | `paidLeave[n].conditions[0]` {conditionType `Age`, operator `gte`, age} |
| ↳ in totaal … dagen | `extra-vakantiedagen/leeftijd[i]/dagen` | getal (postfix dagen) | — | idem | | ja | `paidLeave[n].amount.value`, `unitCode: Day` |
| Ja, extra dagen per duur dienstverband, namelijk: | `extra-vakantiedagen-specifiek/duur-dienstverband` | checkbox | — | — | ja (blok) | | extra `paidLeave`-regels |
| ↳ vanaf … jaar dienstverband | `extra-vakantiedagen/duur-dienstverband[i]/jaar` | getal (postfix jaar) | — | `extra-vakantiedagen-specifiek/duur-dienstverband` aangevinkt | | ja | `paidLeave[n].conditions[0]` {conditionType `EmploymentDuration`, operator `gte`, age} ² |
| ↳ in totaal … dagen | `extra-vakantiedagen/duur-dienstverband[i]/dagen` | getal (postfix dagen) | — | idem | | ja | `paidLeave[n].amount.value`, `unitCode: Day` |
| Ja, anders, namelijk: | `extra-vakantiedagen-specifiek/anders` | checkbox | — | — | ja (blok) | | extra `paidLeave`-regels |
| ↳ in totaal … dagen | `extra-vakantiedagen/anders[i]/dagen` | getal (postfix dagen) | — | `extra-vakantiedagen-specifiek/anders` aangevinkt | | ja | `paidLeave[n].amount.value`, `unitCode` = `vakantiedagen/type` |
| ↳ voor | `extra-vakantiedagen/anders[i]/namelijk` | tekst (textarea) | — | idem | | ja | `paidLeave[n].conditions[0]` {conditionType `Text`, description "Totaal extra aantal vakantiedagen voor: …"} |

Alle extra regels krijgen `baseAmount.unitCode: Fixed` en `interval` {1, `vakantiedagen/tijdvak`}. Volgorde in
`paidLeave`: basisregel, dan leeftijd-regels, dan duur-dienstverband-regels, dan anders-regels.

² **Let op (bug):** bij duur dienstverband staat `age: …?.valueOf` zonder haakjes. Dan wordt een functie
opgeslagen in plaats van het aantal jaren; bij JSON-serialisatie valt die weg. Het aantal jaren dienstverband
komt dus niet in SETU (en het veld heet `age`, ook bij `EmploymentDuration`).

**Let op:**
- Extra dagen worden alleen geëxporteerd als `vakantiedagen/aantal` is ingevuld, want de conversie hangt aan die vraag.
- Bij leeftijd en duur dienstverband is `unitCode` vast `Day`, ook als `vakantiedagen/type` = `Hour`. Bij "anders"
  volgt het wel `vakantiedagen/type`.
- De leeftijd komt uit `…valueOf()` op het tekstantwoord, dus als tekst en niet als getal.

## Bijzonder verlof

### Bijzonder verlof

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming bijzonder verlofregelingen, zoals bijvoorbeeld verlof voor een huwelijk, bij overlijden familielid, voor mantelzorg etc. | `bijzonder-verlof-aanwezig` | radio | Ja → `ja` · Nee → `nee` | — | | | `[DONT_AUTO_SET_SETU_VALUE]` → per rij een Leave in `leave_EXTRA_LEAVES` ³ |

### Variaties (herhaalbaar)

Herhaalbare lijst `bijzonder-verlof`: elke rij is een eigen blok (zichtbaar als `bijzonder-verlof-aanwezig` = `ja`)
met knop: Variatie verwijderen. Onder de lijst een blok met knop: Variatie toevoegen. Bij `ja` wordt de lijst
aangemaakt met één lege rij.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Hoeveel | `bijzonder-verlof[i]/hoeveel` | getal | — | (blok) | | ja | `specialLeave[0].amount.value` + in `name` |
| wat | `bijzonder-verlof[i]/wat` | keuzelijst (geen lege optie) | Uur → `Hour` · Dagen → `Day` · Weken → `Week` · Maanden → `Month` · Jaren → `Year` | (blok) | | ja | `specialLeave[0].interval.unitCode`; `amount.unitCode` = `Hour` bij Uur, anders `Day` |
| In welk geval | `bijzonder-verlof[i]/voorwaarden` | tekst (textarea) | — | (blok) | | ja | `specialLeave[0].conditions[0]` {conditionType `Text`, description} + in `name` |

³ Per rij: Leave {name "Bijzonder verlof: <hoeveel> <dagen/weken/maanden/jaren/uren> in het geval van:
<voorwaarden>", origin, specialLeave: [{amount {hoeveel, Day/Hour, baseAmount Fixed}, interval {1, wat},
conditions [Text]}]}.

**Let op:**
- Dit is de enige plek in de sectie die `leave_EXTRA_LEAVES` vult. De rijen komen **achter** alle vaste
  `leave`-onderdelen; `LEAVE_BIJZONDER_VERLOF` blijft ongebruikt.
- De eenheid is verwarrend opgeslagen: bij "5 Weken" wordt het amount 5 `Day` met interval 1 `Week`. De bedoelde
  eenheid staat alleen correct in `name`.

## Tijd voor tijd

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ken je een regeling waarin gewerkte uren (bijvoorbeeld meeruren, overuren) niet tot uitkering komen, maar worden omgezet in tijd? | `tijd-voor-tijd` | radio | Ja, namelijk: → `ja` · Nee → `nee` | — | | | `allowance[ALLOWANCE_TIJD_VOOR_TIJD]` — bouwt AllowanceArrangement {name "Tijd voor tijd regeling: <namelijk>", typeCode `HT500`, origin} |
| ↳ *(zonder vraagtekst)* | `tijd-voor-tijd/ja/namelijk` | tekst (textarea) | — | `tijd-voor-tijd` = `ja` | | | in `name` |

**Let op:** deze regeling gaat naar `allowance`, niet naar `leave`. Er is geen `line` (geen bedrag of uren), alleen
een vrije tekst in `name` en de vaste typeCode `HT500`.

## Aanvulling Wazo

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming aanvullende regelingen indien de werknemer een Wazo uitkering geniet, zoals bijvoorbeeld een aanvulling op het betaalde of onbetaalde ouderschapsverlof. | `wazo-aanvulling` | radio | Ja → `ja` · Nee → `nee` | — | | | — |

### Welke aanvullende regelingen gelden er?

Het hele blok is zichtbaar als `wazo-aanvulling` = `ja`. Voor elk item uit `wazoRows` komen er een checkbox en een
tekstveld:

| Checkbox-label | Slug `<r>` | SETU-index |
|---|---|---|
| Een aanvulling op het betaalde ouderschapsverlof van | `wazo/betaald-ouderschapsverlof` | `LEAVE_WAZO_BETAALD_OUDERSCHAPSVERLOF` |
| Een aanvulling op het onbetaalde ouderschapsverlof van | `wazo/onbetaald-ouderschapsverlof` | `LEAVE_WAZO_ONBETAALD_OUDERSCHAPSVERLOF` |
| Een aanvulling op het aanvullend geboorteverlof | `wazo/geboorteverlof` | `LEAVE_WAZO_GEBOORTEVERLOF` |
| Een aanvulling op het kortdurend zorgverlof | `wazo/kortdurend-zorgverlof` | `LEAVE_WAZO_KORTDUREND_ZORGVERLOF` |
| Een tegemoetkoming bij langdurend zorgverlof | `wazo/langdurend-zorgverlof` | `LEAVE_WAZO_LANGDUREND_ZORGVERLOF` |
| Een langere verlofduur: | `wazo/langere-verlofduur` | `LEAVE_WAZO_LANGE_VERLOFDUUR` |
| Anders, namelijk: | `wazo/anders` | `LEAVE_WAZO_ANDERS` |

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(checkbox-label uit de lijst)* | `<r>` | checkbox | — | (blok) | | | `leave[<index>]` — Leave {name "Wazo aanvulling: <label>", origin, additionalParentalLeave: [{amount {0, Day, Fixed}, interval {1, Year}, name "Namelijk: <namelijk>"}]} |
| ↳ *(zonder vraagtekst)* | `<r>/namelijk` | tekst | — | `<r>` aangevinkt | | | `additionalParentalLeave[0].name` |

**Let op:** `amount.value` staat vast op 0 `Day` per 1 `Year` (TODO in de code: "add form fields for proper
amount"). Ook bij zorgverlof en "anders" wordt `additionalParentalLeave` gebruikt. De inhoud staat alleen als vrije
tekst in `name`.

## Verplichte aanwending verlof

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming periodes, dagen of uren waarbij sprake is van een bedrijfssluiting waarvoor de werknemer verplicht verlof moet aanwenden? | `verplichte-aanwending-verlof` | radio | Ja → `ja` · Nee → `nee` | — | | | `leave[LEAVE_VERPLICHT]` — Leave {name "Verplichte aanwending verlof", origin, mandatoryLeaveAllocation.description} |

Hulptekst: *"Denk aan een brugdag tussen Hemelvaartsdag en het weekend, de bouwvak etc."*

### Geef aan voor welke periode/dagen/uren de werknemer verplicht verlof moet aanwenden

Het hele blok is zichtbaar als `verplichte-aanwending-verlof` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `verplichte-aanwending-verlof/ja/periode-dagen-uren` | tekst (textarea) | — | (blok) | | | in `mandatoryLeaveAllocation.description` |

### Welk verlof dient de werknemer te gebruiken voor de hiervoor genoemde verplichte vrije periodes, dagen of uren?

Het hele blok is zichtbaar als `verplichte-aanwending-verlof` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `verplichte-aanwending-verlof_welk-verlof` | tekst (textarea) | — | (blok) | | | in `mandatoryLeaveAllocation.description` |

**Let op:** beide tekstvelden worden samengevoegd tot één string:
`"Periode/dagen/uren:" + <periode> + "\n\nWelk verlof:" + <welk verlof>`.

## Feestdagen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Hoeveel feestdagen kent jouw onderneming? | `aantal-feestdagen` | getal | — | — | | | `leave[LEAVE_FEESTDAGEN]` — Leave {name "Feestdagen", origin, holidays: [{amount {aantal, Day, Fixed}, interval {1, Year}, name, conditions}]} |
| Welke feestdagen kent jouw onderneming? | `welke-feestdagen` | tekst (textarea) | — | — | | | `holidays[0].name` (regels samengevoegd met ", ") |
| Gelden er voorwaarden voor het genieten van een feestdag? | `voorwaarden-feestdagen` | tekst (textarea) | — | — | ja | | `holidays[0].conditions[]` {Text, "Voorwaarden voor het genieten van een feestdag: …"} |
| Ken je feestdagen die niet elk jaar worden toegekend? | `feestdagen-niet-elk-jaar` | radio | Ja → `ja` · Nee → `nee` | — | | | bepaalt extra condition |
| ↳ Om welke feestdagen gaat het en wat zijn de voorwaarden voor toekenning? | `feestdagen-niet-elk-jaar_voorwaarden` | tekst (textarea) | — | `feestdagen-niet-elk-jaar` = `ja` | | | `holidays[0].conditions[]` {Text, "Feestdagen die niet elk jaar worden toegekend, en hun voorwaarden: …"} |
| Ken je persoonlijke feestdagen? | `persoonlijke-feestdagen` | radio | Ja, namelijk: → `ja` · Nee → `nee` | — | | | `leave[LEAVE_PERSOONLIJKE_FEESTDAGEN]` — Leave {name "Persoonlijke feestdagen", origin, holidays: [{amount {aantal, Day, Fixed}, interval {1, Year}, name, conditions}]} |
| ↳ Hoeveel persoonlijke feestdagen kent jouw onderneming? | `persoonlijke-feestdagen/aantal` | getal | — | `persoonlijke-feestdagen` = `ja` | | | `holidays[0].amount.value` |
| ↳ Welke persoonlijke feestdagen kent jouw onderneming? | `persoonlijke-feestdagen/namelijk` | tekst (textarea) | — | `persoonlijke-feestdagen` = `ja` | | | `holidays[0].name` (regels samengevoegd met ", ") |
| ↳ Welke voorwaarden gelden er voor de persoonlijke feestdagen? | `persoonlijke-feestdagen/voorwaarden` | tekst (textarea) | — | `persoonlijke-feestdagen` = `ja` | ja | | `holidays[0].conditions[]` {Text, "Voorwaarden voor het genieten van een persoonlijke feestdag: …"} |

Hulpteksten: bij het aantal *"Exclusief persoonlijke feestdagen, deze kunnen onderaan deze pagina worden
toegevoegd. Inclusief feestdagen die niet jaarlijks worden toegekend, b.v. 5-mei."*; bij welke feestdagen en
welke persoonlijke feestdagen *"Voer de feestdagen 1 per regel in, gebruik de Enter-toets om een nieuwe regel te
maken."*

**Let op:** de feestdagen-Leave wordt alleen gemaakt als `aantal-feestdagen` is ingevuld. De lijst met feestdagen
wordt één komma-gescheiden `name`-string, zonder aparte datums.

## Waarde van een (verlof)dag

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kennen jouw arbeidsvoorwaardenregeling(en) en/of cao een regeling om de waarde van een (verlof)dag te bepalen? | `waarde-verlofdag` | radio | Ja, namelijk → `ja` · Nee. In dat geval wordt de waarde op 0,385% vastgesteld, waarbij dit percentage is gebaseerd op 260 werkbare dagen. → `nee` | — | | | `leave[LEAVE_WAARDE_VERLOFDAG]` — Leave {name "Waarde van een (verlof)dag", origin, paidLeave: [{amount {0, Day, Fixed}, interval {1, Year}, leaveDayValue}]} |
| ↳ *(zonder vraagtekst)* | `waarde-verlofdag_ja_percentage` | getal (postfix %) | — | `waarde-verlofdag` = `ja` | | | `paidLeave[0].leaveDayValue` {value, `unitCode: Percentage`, `baseAmount.unitCode: DailyRate`} |

Hulptekst bij het percentage: *"Als je geen percentage maar een factor hanteert, reken deze dan om naar een
percentage"*.

**Let op:** bij `nee` wordt niets geëxporteerd; de standaardwaarde 0,385% staat alleen in het optielabel en komt
niet in SETU. `paidLeave[0].amount` is een vaste 0-regel.

## Uitgeschakeld in de code

- Vakantiedagen: een uitgecommentarieerd uren-veld `vakantiedagen-uren_aantal` (postfix uren, getoond bij
  `vakantiedagen-toekenning` = `uren`). Dat is vervangen door de keuzelijst `vakantiedagen/type`.
- Aanvulling Wazo: op `wazo-aanvulling` staan een uitgecommentarieerde `setuPath: ['leave', LEAVE_WAZO]` en een
  conversie. Die bouwde één Leave {name "Wazo aanvulling", WAZO.description} op basis van een oude radio
  `wazo-aanvullende-regelingen` (waarden `betaald-ouderschapsverlof`, `onbetaald-ouderschapsverlof`, `geboorteverlof`,
  `kortdurend-zorgverlof`, `langdurend-zorgverlof`, `langere-verlofduur`, `anders`, elk met `…/namelijk`). Dat is
  vervangen door de checkboxlijst hierboven.

---

**Telling:** 43 tekst/getal · 0 datum · 0 tijd · 28 radio/keuzelijst · 13 checkbox (84 vragen), 0 alerts.
(Toekenningsblok 4× uitgeschreven; herhaalbare rijen één keer per rijdefinitie geteld.)
