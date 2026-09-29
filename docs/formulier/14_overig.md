# 14 · Overig

Bron: `src/definition/14_overig.tsx` (webformulier v2.1.0).

**Structuur:** één subsectie zonder menu-label, met de header *Overig*. Eerst een ja/nee-vraag. Bij *ja* volgt een
herhaalbare lijst `overige-regelingen[]` met vrije regelingen: naam, voorwaarden en een Bedragregel. Elke rij
wordt een eigen `otherArrangement` op positie `OTHER_OVERIG_START + i`.

## Overig

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Zijn er overige regelingen of arbeidsvoorwaarden van toepassing? | `overige-regelingen-ja-nee` | radio | Ja → `ja` · Nee → `nee` | — | | | — |

### Overige regelingen

Het hele blok is zichtbaar als `overige-regelingen-ja-nee` = `ja`.

**Herhaalbare rijen `overige-regelingen[i]`:** één set vragen per element van `answers["overige-regelingen"]`.
Elke rij heeft een verwijderknop (`remove-child`, zonder label, `splice(i, 1)`) en wordt afgesloten met een
scheidingslijn. Onder de lijst staat een toevoegknop (`add-child`, zonder label, `push({})`).

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam | `overige-regelingen[i]/naam` | tekst | — | (blok) | | ja | `otherArrangement[OTHER_OVERIG_START + i]`: bouwt OtherArrangement {name, origin, line[0]: Bedragregel} ¹ |
| Voorwaarden | `overige-regelingen[i]/voorwaarden` | tekst | — | (blok) | ja | ja | `line[0].conditions[0]` {conditionType: Text, description} |
| *Bedragregel* — Hoe wordt de waarde uitgekeerd? | `overige-regelingen[i]/…` (bijv. `overige-regelingen[i]/amount-type`) | [B1](00_bouwstenen.md#b1--bedragregel-makelineamountquestions) | standaard (met vast bedrag, percentage, tijd en "per") | (blok) | | ja | `line[0]` |

¹ `name` = Naam, `origin.type = Unknown` ([B10](00_bouwstenen.md#b10--vaste-setu-standaardwaarden-van-het-formulier)),
`line[0]` = `getLineAmountAnswer` met de rij-prefix. Als Voorwaarden is ingevuld, wordt `line[0].conditions`
vervangen door één tekstconditie.

**Let op:**
- De Bedragregel heeft als prefix de rij zelf (`["overige-regelingen", i]`). De vragen `amount-type`,
  `vast-bedrag/…`, `percentage/…` en `tijd/…` staan dus direct naast `naam` en `voorwaarden` in hetzelfde
  rij-object.
- Er is **geen typeCode**. Een regeling is alleen te herkennen aan haar vrije `name`.
- In `otherArrangement` beginnen deze rijen op index `OTHER_OVERIG_START` (6). De vaste indexen 0–5 worden niet
  gevuld door sectie 13 (die schrijft naar `supplementaryArrangement`). `clean()` verwijdert lege elementen, dus
  in de export staan deze rijen vooraan. Daarna komen de vrije regelingen uit
  [13 Aanvullende regelingen](13_aanvullende-regelingen.md#anders) (`other_EXTRA_OTHERS`).
- Bij `overige-regelingen-ja-nee` = `nee` is het blok verborgen. De `convertSetuValue` van bestaande rijen
  controleert de ja/nee-vraag niet. Of verborgen rijen toch meegaan in de export, hangt af van hoe de
  export-engine met verborgen vragen omgaat.
- `convertSetuValue` roept `value.toString()` aan op Naam. Een rij zonder naam levert daarom waarschijnlijk geen
  regeling op.

## Uitgeschakeld in de code

Niets.

---

**Telling:** 2 tekst/getal · 0 datum · 0 tijd · 1 radio/keuzelijst · 0 checkbox (3 vragen + 1 Bedragregel; de
rijvragen zijn één keer geteld), 0 alerts.
