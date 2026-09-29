# 03 · Functiegroepen

Bron: `src/definition/03_functiegroepen.tsx` (webformulier v2.1.0).

**Structuur:** één subsectie (*Functiegroepen*) met één herhaalbaar blok. Elke rij `functie-groepen[i]` is een
functie of functiegroep en wordt `positionProfile[i]` in SETU. Per rij kies je ook een salarisschaal uit
[02 Beloning](02_beloning.md). Die keuze komt terecht als verwijzing op de gekozen `salaryScale`. De startwaarde in
de Store is `"functie-groepen": []`, dus er staan nog geen rijen.

## Functiegroepen

### Voor welke functie(s) of functiegroep(en) wordt het formulier ingevuld?

Herhaalbaar blok: één rij per `functie-groepen[i]`. Knop: *Functiegroep toevoegen* (voegt `{}` toe). Knop:
*verwijderen* per rij, zonder bevestiging en zonder minimum.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Titel | `functie-groepen[i]/titel` | tekst | — | — | | ja | `positionProfile[i].positionTitle` |
| Code | `functie-groepen[i]/id` | tekst | — | — | ja | ja | `positionProfile[i].positionId.value`; als leeg dan de titel (`shouldConvertNullSetuValue`) |
| Salarisschaal {num} | `functie-groepen[i]/salarisschalen` | keuzelijst | dynamisch: één optie per salarisschaal van elke salaristabel, `"<beloningen[b].naam> - <salarisschalen[s].naam>"` → `"b,s"` | — | | ja | `DONT_AUTO_SET_SETU_VALUE`; de conversie voegt toe aan `remuneration[b].salaryScale[s].positionProfileReference[]` |

Hulptekst bij `id`: *"De identificatiecode van de functiegroep, doorgaans afkomstig uit het registratiesysteem."*

Wat de conversie van `salarisschalen` doet: de waarde `"b,s"` wordt gesplitst in de index van de salaristabel en
de index van de schaal. Aan `remuneration[b].salaryScale[s].positionProfileReference` wordt
`{positionId: {value: <id> ?? <titel>}}` toegevoegd. Er wordt niets onder `positionProfile[i]` zelf geschreven.
Bij export krijgt elke `positionProfile` `origin.type: Unknown` (zie
[B10](00_bouwstenen.md#b10--vaste-setu-standaardwaarden-van-het-formulier)).

**Let op:**
- De vraagtekst is `Salarisschaal {num}` met `num: i`, dus **0-gebaseerd**. De eerste rij heet "Salarisschaal 0".
- Per functiegroep kun je maar **één** salarisschaal kiezen. Meerdere functiegroepen kunnen wel naar dezelfde
  schaal verwijzen; die krijgt dan meerdere `positionProfileReference`s.
- De koppeling loopt via `positionId.value`. Is de code leeg, dan is dat de titel. Bij een lege string (`""`)
  valt `??` niet terug op de titel, maar `clean()` haalt de lege waarde daarna weg.
- De verwijzing komt alleen op de basis-`remuneration[b]`. De extra remunerations van afwijkende roosters
  ([02 Beloning › Afwijkende roosters](02_beloning.md#afwijkende-roosters)) zijn dan al gekopieerd en krijgen
  geen verwijzing.
- Het label van een optie gebruikt `beloning.naam`. Een salaristabel die met *Salaristabel toevoegen* is gemaakt
  en nog geen naam heeft, geeft het label "undefined - …". Een schaal zonder naam geeft "… - undefined".
- De waarde `"b,s"` is gekoppeld aan array-indexen. Verwijder of verschuif je een salaristabel of schaal, dan kan
  een eerder gekozen waarde naar een andere schaal wijzen of niets meer vinden (dan geeft de conversie `null`).
- Fouten in de conversie worden stil genegeerd (`try … finally { return null }`).

## Uitgeschakeld in de code

Geen.

---

**Telling:** 2 tekst/getal · 0 datum · 0 tijd · 1 radio/keuzelijst · 0 checkbox (3 vragen), 0 alerts.
Geteld per functiegroep-rij.
