# 13 · Aanvullende regelingen

Bron: `src/definition/13_aanvullende-regelingen.tsx` (webformulier v2.1.0).

**Structuur:** zes subsecties. Vijf daarvan (PAWW, PAZW, RVU regeling, WGA-Hiaat, Ongevallenverzekering) worden
gegenereerd uit `makeAanvullendeRegelingenRows`. Die functie wordt ook gebruikt door sectie
[15 Grondslagen](15_grondslagen.md). Elke subsectie bevat dezelfde vragen: een ja/nee-vraag, een omschrijving,
twee premie-Bedragregels en (behalve bij RVU) een Bedragregel voor de dekkingswaarde. De zesde subsectie *Anders*
heeft een herhaalbare lijst `andere-sociale-regelingen[]` voor vrije regelingen. De vijf vaste regelingen gaan
naar `supplementaryArrangement[…]` en de vrije regelingen naar `otherArrangement[]`.

## Regelingen uit `makeAanvullendeRegelingenRows`

| Slug `<r>` | Menu-label | Vraag | setuName | typeCode | SETU-index | Dekkingswaarde? |
|---|---|---|---|---|---|---|
| `aanvullende-sociale-zekerheidsregelingen/paww` | PAWW | Kent jouw onderneming een PAWW (private aanvulling WW) regeling? | PAWW regeling | `PAWW` | `OTHER_PAWW` | ja |
| `aanvullende-sociale-zekerheidsregelingen/pazw` | PAZW | Kent jouw onderneming een PAZW (private aanvulling Ziektewet) regeling? | PAZW regeling | `PAZW` | `OTHER_PAZW` | ja |
| `aanvullende-sociale-zekerheidsregelingen/rvu-regeling` | RVU regeling | Kent jouw onderneming een RVU regeling, een generatiepact of regeling om minder te gaan werken richting het pensioen? | RVU regeling, generatiepact of regeling om minder te gaan werken richting het pensioen | `RVU` | `OTHER_RVU_REGELING` | **nee** (`showCoverageQuestions: false`) |
| `aanvullende-sociale-zekerheidsregelingen/wga-hiaat` | WGA-Hiaat | Kent jouw onderneming een WGA-Hiaat regeling? | WGA-Hiaat regeling | `WGA` | `OTHER_WGA_HIAAT` | ja |
| `aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering` | Ongevallenverzekering | Kent jouw onderneming een ongevallenverzekering? | Ongevallenverzekering | `AccidentBenefit` | `OTHER_ACCIDENT_BENEFIT` | ja |

Hulpteksten:
- Bij RVU (boven de vraag): *"RVU: regeling voor vervroegde uittreding. Het gaat hier niet om de toekenning van
  extra ADV / ATV of verlof aan oudere werknemers"*.
- Bij Ongevallenverzekering (bij de omschrijving): *"Geef o.a. aan of er een 24-uursdekking en/of functiedekking
  is, welk bedrag wordt uitgekeerd bij overlijden en bij blijvende invaliditeit"*.

## PAWW

`<r>` = `aanvullende-sociale-zekerheidsregelingen/paww`. De blokken 2 t/m 5 zijn zichtbaar als `<r>` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming een PAWW (private aanvulling WW) regeling? | `aanvullende-sociale-zekerheidsregelingen/paww` | radio | Ja → `ja` · Nee → `nee` | — | | | `supplementaryArrangement[OTHER_PAWW]`: bouwt SupplementaryArrangement {name, typeCode `PAWW`, description, line[2], coverage} ¹ |
| Omschrijf de inhoud van de regeling | `aanvullende-sociale-zekerheidsregelingen/paww/omschrijving` | tekst (textarea) | — | (blok) | | | `description` |
| *Bedragregel* — Wat is de werkgeverspremie? | `aanvullende-sociale-zekerheidsregelingen/paww/werkgeverspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[0]` + `contributionSource: Employer` |
| *Bedragregel* — Wat is de werknemerspremie? | `aanvullende-sociale-zekerheidsregelingen/paww/werknemerspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[1]` + `contributionSource: Employee` |
| *Bedragregel* — Wat is de dekkingswaarde? | `aanvullende-sociale-zekerheidsregelingen/paww/dekkingswaarde/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder "per"-vragen, optioneel | (blok) | ja | | `coverage` (alleen `.amount`) |

## PAZW

`<r>` = `aanvullende-sociale-zekerheidsregelingen/pazw`. De blokken 2 t/m 5 zijn zichtbaar als `<r>` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming een PAZW (private aanvulling Ziektewet) regeling? | `aanvullende-sociale-zekerheidsregelingen/pazw` | radio | Ja → `ja` · Nee → `nee` | — | | | `supplementaryArrangement[OTHER_PAZW]`: bouwt SupplementaryArrangement {typeCode `PAZW`, …} ¹ |
| Omschrijf de inhoud van de regeling | `aanvullende-sociale-zekerheidsregelingen/pazw/omschrijving` | tekst (textarea) | — | (blok) | | | `description` |
| *Bedragregel* — Wat is de werkgeverspremie? | `aanvullende-sociale-zekerheidsregelingen/pazw/werkgeverspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[0]` + `contributionSource: Employer` |
| *Bedragregel* — Wat is de werknemerspremie? | `aanvullende-sociale-zekerheidsregelingen/pazw/werknemerspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[1]` + `contributionSource: Employee` |
| *Bedragregel* — Wat is de dekkingswaarde? | `aanvullende-sociale-zekerheidsregelingen/pazw/dekkingswaarde/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder "per"-vragen, optioneel | (blok) | ja | | `coverage` (alleen `.amount`) |

## RVU regeling

`<r>` = `aanvullende-sociale-zekerheidsregelingen/rvu-regeling`. De blokken 2 t/m 4 zijn zichtbaar als `<r>` = `ja`.
Er is **geen** dekkingswaarde.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming een RVU regeling, een generatiepact of regeling om minder te gaan werken richting het pensioen? | `aanvullende-sociale-zekerheidsregelingen/rvu-regeling` | radio | Ja → `ja` · Nee → `nee` | — | | | `supplementaryArrangement[OTHER_RVU_REGELING]`: bouwt SupplementaryArrangement {typeCode `RVU`, …} ¹ |
| Omschrijf de inhoud van de regeling | `aanvullende-sociale-zekerheidsregelingen/rvu-regeling/omschrijving` | tekst (textarea) | — | (blok) | | | `description` |
| *Bedragregel* — Wat is de werkgeverspremie? | `aanvullende-sociale-zekerheidsregelingen/rvu-regeling/werkgeverspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[0]` + `contributionSource: Employer` |
| *Bedragregel* — Wat is de werknemerspremie? | `aanvullende-sociale-zekerheidsregelingen/rvu-regeling/werknemerspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[1]` + `contributionSource: Employee` |

## WGA-Hiaat

`<r>` = `aanvullende-sociale-zekerheidsregelingen/wga-hiaat`. De blokken 2 t/m 5 zijn zichtbaar als `<r>` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming een WGA-Hiaat regeling? | `aanvullende-sociale-zekerheidsregelingen/wga-hiaat` | radio | Ja → `ja` · Nee → `nee` | — | | | `supplementaryArrangement[OTHER_WGA_HIAAT]`: bouwt SupplementaryArrangement {typeCode `WGA`, …} ¹ |
| Omschrijf de inhoud van de regeling | `aanvullende-sociale-zekerheidsregelingen/wga-hiaat/omschrijving` | tekst (textarea) | — | (blok) | | | `description` |
| *Bedragregel* — Wat is de werkgeverspremie? | `aanvullende-sociale-zekerheidsregelingen/wga-hiaat/werkgeverspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[0]` + `contributionSource: Employer` |
| *Bedragregel* — Wat is de werknemerspremie? | `aanvullende-sociale-zekerheidsregelingen/wga-hiaat/werknemerspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[1]` + `contributionSource: Employee` |
| *Bedragregel* — Wat is de dekkingswaarde? | `aanvullende-sociale-zekerheidsregelingen/wga-hiaat/dekkingswaarde/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder "per"-vragen, optioneel | (blok) | ja | | `coverage` (alleen `.amount`) |

## Ongevallenverzekering

`<r>` = `aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering`. De blokken 2 t/m 5 zijn zichtbaar als
`<r>` = `ja`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming een ongevallenverzekering? | `aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering` | radio | Ja → `ja` · Nee → `nee` | — | | | `supplementaryArrangement[OTHER_ACCIDENT_BENEFIT]`: bouwt SupplementaryArrangement {typeCode `AccidentBenefit`, …} ¹ |
| Omschrijf de inhoud van de regeling | `aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering/omschrijving` | tekst (textarea) | — | (blok) | | | `description` |
| *Bedragregel* — Wat is de werkgeverspremie? | `aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering/werkgeverspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[0]` + `contributionSource: Employer` |
| *Bedragregel* — Wat is de werknemerspremie? | `aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering/werknemerspremie/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder tijd, met N.v.t. | (blok) | | | `line[1]` + `contributionSource: Employee` |
| *Bedragregel* — Wat is de dekkingswaarde? | `aanvullende-sociale-zekerheidsregelingen/ongevallenverzekering/dekkingswaarde/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | zonder "per"-vragen, optioneel | (blok) | ja | | `coverage` (alleen `.amount`) |

¹ Alleen bij `ja` gevuld: `name` = setuName, `origin.type = Unknown`, `description` = omschrijving (of `""`),
`typeCode` uit de tabel hierboven, `line[0]` = werkgeverspremie met `contributionSource: Employer`,
`line[1]` = werknemerspremie met `contributionSource: Employee`, `coverage` = alleen het `amount`-deel van de
dekkingswaarde-regel.

**Let op:**
- De SETU-indexen zijn de `OTHER_*`-constanten (0, 1, 3, 4, 5), maar ze worden gebruikt in de lijst
  `supplementaryArrangement`, niet in `otherArrangement`. Index 2 (`OTHER_ANDERS`) wordt nergens gevuld.
  `clean()` verwijdert lege elementen uit arrays, dus in de export schuiven de posities op. Je kunt een regeling
  daarom niet herkennen aan haar index, alleen aan `typeCode`.
- Kies je bij een premie *N.v.t.*, dan levert de Bedragregel `{}` op. De premie-regel wordt daardoor
  `{contributionSource: …}` zonder bedrag. Die is niet leeg en blijft dus in de export staan.
- De dekkingswaarde-Bedragregel heeft wel de keuze *In tijd* (uren), want `includeTimeQuestions` staat op de
  standaardwaarde. `coverage` kan dus een bedrag in uren zijn.

## Anders

### Andere aanvullende sociale zekerheidsregelingen

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Kent jouw onderneming andere aanvullende sociale zekerheidsregeling? | `andere-sociale-regelingen/ja-nee` | radio | Ja → `ja` · Nee → `nee` | — | | | — |

**Herhaalbare rijen `andere-sociale-regelingen[i]`:** één blok per rij, via `range(countAnswerRows(...))`. Elke rij
heeft een knop *Regeling verwijderen* (`removeAnswerRow`). Onder de lijst staat de knop *Regeling toevoegen*
(`addAnswerRow`), die alleen zichtbaar is als `andere-sociale-regelingen/ja-nee` = `ja`. De rijen zelf hebben
**geen** showIf, dus bestaande rijen blijven ook bij `nee` zichtbaar.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Omschrijf de inhoud van de regeling | `andere-sociale-regelingen[i]/omschrijving` | tekst (textarea) | — | — | | ja | `DONT_AUTO_SET_SETU_VALUE`: voegt toe aan `other_EXTRA_OTHERS` → `otherArrangement[]` (achteraan) ² |
| *Bedragregel* — Wat is de werkgeverspremie? | `andere-sociale-regelingen[i]/werkgeverspremie[0]/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | standaard (met vast bedrag, percentage, tijd en "per") | — | | ja | `line[0]` + `contributionSource: Employer` |
| *Bedragregel* — Wat is de werknemerspremie? | `andere-sociale-regelingen[i]/werknemerspremie[0]/…` | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | standaard | — | | ja | `line[1]` + `contributionSource: Employee` |

Alert (warning), zichtbaar als `andere-sociale-regelingen/ja-nee` = `nee` **en** er minstens 1 rij bestaat:
*"Je hebt aangegeven dat jouw onderneming geen aanvullende sociale zekerheidsregelingen kent. Verwijder daarom
hierboven de regelingen of kies voor optie 'ja'."*

² Bouwt OtherArrangement {name `"Andere aanvullende sociale zekerheidsregeling"` (vast), description =
omschrijving, `origin.type = Unknown`, line[0] werkgever, line[1] werknemer}. Er is **geen typeCode**.

**Let op:**
- Dit is een `*_EXTRA_*`-samenvoeging. `toSetuStandard()` voegt `other_EXTRA_OTHERS` pas na alle vaste indexen
  achteraan toe aan `otherArrangement`, dus ook na de vrije regelingen uit [14 Overig](14_overig.md)
  (`OTHER_OVERIG_START + i`).
- De naam staat voor elke rij vast. Je kunt deze regelingen dus alleen van elkaar onderscheiden via
  `description`.
- De premies staan onder een extra array-niveau `[0]` (`…/werkgeverspremie[0]/amount-type`).
- Bij `ja-nee` = `nee` worden bestaande rijen **toch** geëxporteerd, want er is geen controle op `ja-nee`.

## Uitgeschakeld in de code

Niets.

---

**Telling:** 6 tekst/getal · 0 datum · 0 tijd · 6 radio/keuzelijst · 0 checkbox (12 vragen + 16 Bedragregels:
5 × werkgever, 5 × werknemer, 4 × dekkingswaarde en per rij van `andere-sociale-regelingen` 2; de rijvragen zijn
één keer geteld), 1 alert.
