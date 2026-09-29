# Plan: van formuliermodel naar SETU-JSON

*Status: uitgevoerd op 24–25 september 2026. Zie `docs/koppeling_wijzerbelonen.md`. Afwijkend van dit plan:*
- *de fouten van de tool zijn exact nagedaan;*
- *de omzetting werkt via de antwoorden van de tool;*
- *de controle gebeurt tegen de echte webformcode.*

## Doel

```python
f = Formulier()
...                                   # vullen vanuit je applicatie
bericht = naar_setu(f)                # → InquiryPayEquity (SETU-kernmodel)
bericht.valideer()                    # [] = geldig volgens het officiële schema
bericht.schrijf("uitvraag.json")
```

Eén richting: **formulier → SETU**. De andere kant op (SETU → formulier) en de export van `__webform_data__`
zijn niet in dit plan opgenomen.

## Hoe de webform het zelf doet

Bron: `Store.toSetuStandard()` in de webform-bundle (v2.1.0).

1. De webform begint met een leeg bericht en zet `documentId` (`schemeAgencyId: Customer`) en `issued` (nu).
2. Hij loopt **alle zichtbare vragen** af in formuliervolgorde (sectie 01 → 16). Een vraag met een `setuPath` zet
   zijn waarde op dat pad, eventueel eerst omgezet door `convertSetuValue`. Er zijn ongeveer 45 van zulke
   omzetfuncties, van één regel tot ruim 100 regels.
3. **Vaste posities.** Vaste onderdelen gaan naar een vaste index, bijvoorbeeld `allowance[ALLOWANCE_STANDBY]` of
   `leave[LEAVE_VAKANTIE]` (zie B11 in `00_bouwstenen.md`).
4. **Extra rijen.** Herhaalbare onderdelen komen in een aparte lijst:
   - toeslagvariaties en bijzondere uitkeringen in `allowance_EXTRA_…`;
   - afwijkende roosters in `remuneration_EXTRA_…`;
   - bijzonder verlof in `leave_EXTRA_…`;
   - andere sociale regelingen in `other_EXTRA_…`.

   Die extra lijsten worden achter de vaste posities geplakt.
5. `clean()` verwijdert alle lege onderdelen. Van de vaste indexen blijft dus alleen de **volgorde** over.
6. Daarna worden de vaste standaardwaarden ingevuld: `origin: Unknown` en `currency: EUR`.

Dit gedrag bouw ik na, maar dan met getypte objecten uit het SETU-kernmodel in plaats van losse JSON-paden.

## Ontwerp

### Waar het komt

`src/cao_setu_v2/koppeling/wijzerbelonen/` is de wijzerbelonen-adapter uit de architectuur. Later komt
inlenersbeloning ernaast.

| Module | Inhoud |
|---|---|
| `naar_setu.py` | `naar_setu(formulier) -> InquiryPayEquity`: roept de secties in volgorde aan en voegt alles samen |
| `opbouw.py` | Het tussenresultaat: vaste posities per SETU-lijst, de extra rijen, meldingen, en de volgorde als bij `clean()` |
| `gedeeld.py` | Omzetters die overal terugkomen: Bedragregel → `ArrangementLine`, werkduur → `Interval` (B8), loonbasis → interval (B9), de vaste waarden uit B10 |
| `s01_algemeen.py` … `s16_ondertekenen.py` | Per sectie de omzetting, 1-op-1 met de `convertSetuValue`-functies van die sectie |

Elke sectiefunctie heeft dezelfde vorm: `def omzetten(sectie, opbouw, formulier) -> None`. Het `formulier` is
nodig voor verwijzingen tussen secties:
- functiegroepen verwijzen naar salarisschalen;
- grondslagen (15) hangen af van keuzes in andere secties.

### Wat per sectie naar SETU gaat

| Sectie | SETU | Moeilijkheid |
|---|---|---|
| 01 Algemeen | `documentId`, `effectivePeriod`, `customer` (naam, legalId), `labourAgreements` | laag |
| 02 Beloning | `remuneration[]` met schalen en stappen, werkduur, verhogingen en afwijkende roosters (kopie per rooster); plus `allowance[PAID_BREAKS]` | **hoog** |
| 03 Functiegroepen | `positionProfile[]` + verwijzing vanuit de salarisschaal | middel |
| 04 Toeslagen | `allowance[]` per variatie, met periodes en cumulatie | **hoog** |
| 05 Vakantiebijslag | `holidayAllowance[0]` | laag |
| 06 Vergoedingen | `allowance[…]`: reiskosten, stand-by, zorgverzekering, thuiswerk, mobiliteit, kosten | **hoog** (veel) |
| 07 Bijzondere uitkeringen | `allowance` extra rijen (4 soorten) | middel |
| 08 Ziekte | `sickPay[0]`, `allowance[WACHTDAGCOMPENSATIE]` | middel |
| 09 Verlof | `leave[…]` (ADV, vakantie, Wazo, feestdagen, …), bijzonder verlof als extra rijen, `allowance[TIJD_VOOR_TIJD]` | **hoog** |
| 10 IKB | `individualChoiceBudget[0]` | laag |
| 11 Pensioen | `pension[0]` | laag |
| 12 Duurzaam werken | `sustainableEmployability[…]` (12× dezelfde vragenset + 2) | middel |
| 13 Aanvullende regelingen | `supplementaryArrangement[…]` + extra rijen | middel |
| 14 Overig | `otherArrangement[…]` | laag |
| 15 Grondslagen | `baseDefinition[]` | middel |
| 16 Ondertekenen | `customer.personContacts[]` | laag |

### Controle

Ik vertaal de webform-code, maar ik kan hem niet naast de echte webform draaien. De controle bestaat daarom uit drie
lagen:

1. **Per sectie een test:** een ingevuld voorbeeld → de verwachte SETU-uitvoer, met de hand afgeleid uit de
   webform-code.
2. **Elk resultaat valideert** tegen het officiële schema (`bericht.valideer() == []`).
3. **Vergelijking met de echte tool (sterk aanbevolen):** jij vult in wijzerbelonen 2 of 3 formulieren in en
   exporteert ze. Ik vul hetzelfde in Python in en vergelijk de SETU-uitvoer veld voor veld. `documentId` en
   `issued` tellen daarbij niet mee.

## Beslispunten voor Justin

1. **Bugs in de webform: nadoen of verbeteren?** Het gaat om ongeveer 7 bugs, bijvoorbeeld:
   - loondoorbetaling bij ziekte neemt voor elke rij het percentage van rij 0;
   - de jaren bij vakantiedagen per dienstverband gaan verloren;
   - ADV "anders, namelijk" wordt niet gelezen.

   **Voorstel:** verbeteren waar de webform informatie weggooit, en elke afwijking vastleggen in de docs. Het nadeel
   is dat onze uitvoer op die punten niet gelijk is aan een export van de tool.
2. **Onvolledige invoer.** De webform schrijft gewoon door, ook als het resultaat niet aan het schema voldoet.
   Voorbeelden: een bedrag zonder "per", of een regeling zonder verplicht veld.

   **Voorstel:** `naar_setu()` geeft standaard één fout met álle problemen, met per probleem het formulierveld
   (bijv. `vergoedingen.stand_by.bedrag.per ontbreekt`). Met `naar_setu(f, onvolledig="weglaten")` laat hij die
   onderdelen weg en krijg je een lijst meldingen.
3. **Vaste waarden** (`origin: Unknown`, `currency: EUR`, typeCode `EA100` waar het formulier niets specifieks
   weet). **Voorstel:** hetzelfde als de webform, zodat de uitvoer overeenkomt. Je kunt ze later per regeling
   overschrijven.
4. **Volgorde van bouwen**, met na elke stap een review door jou:
   - **A** (eerst, als proef): 01, 05, 10, 11, 14, 15, 16 plus `gedeeld.py` en `opbouw.py`. Na A is er al een
     klein, geldig SETU-bericht, en zie je hoe het werkt.
   - **B:** 02 Beloning en 03 Functiegroepen.
   - **C:** 04 Toeslagen, 06 Vergoedingen en 07 Bijzondere uitkeringen.
   - **D:** 08 Ziekte, 09 Verlof, 12 Duurzaam werken en 13 Aanvullende regelingen.

   `remuneration` is verplicht in SETU. Na stap A valideert een bericht dus pas als je in de test een minimale
   salaristabel meegeeft.

## Vooraf, klein

- Een fout in het kernmodel rechtzetten: tolerant inlezen zet nu een gewone datum in `recurringInterval`. Het moet
  een ISO-reeks worden, bijv. `R/2026-06-02/P1Y`.
- `tests/test_setu.py` voor het kernmodel: de conformiteit met het schema, het officiële voorbeeld en inlezen →
  wegschrijven → inlezen. De mapping bouwt hierop, dus het kernmodel moet eerst vastliggen.

## Niet in dit plan

- SETU → formulier (terug).
- Formulier ↔ `__webform_data__`, voor importeren en exporteren in de wijzerbelonen-tool.
- Inlenersbeloning.
