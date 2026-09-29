# 01 · Algemeen

Bron: `src/definition/01_algemeen.tsx` (webformulier v2.1.0). Eén subsectie, zonder menu-label.

## Arbeidsvoorwaardenregeling en toepassingsperiode

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Geef je arbeidsvoorwaardenregeling een naam of nummer: | `id` | tekst | — | — | | | `documentId.value` ¹ |
| Geldig van | `toepassingsperiode-van` | datum | — | — | | | `effectivePeriod.validFrom` |
| tot | `toepassingsperiode-tot` | datum | — | — | ja | | `effectivePeriod.validTo` |

Hulptekst bij `id`: *"Zo ziet je contactpersoon van het uitzendbureau snel bij welke opdrachtgever dit
uitvraagformulier hoort."*

¹ Bij export overschrijft `toSetuStandard()` `documentId` met een nieuw uuid, waardoor deze naam in de SETU-inhoud
verloren gaat. Hij blijft wel bewaard in `__webform_data__`.

## Opdrachtgever

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam onderneming(en) / organisatie(s): | `opdrachtgever-naam` | tekst | — | — | | | `customer.name` |
| Bijbehorende KvK of een ander identificatienummer van de onderneming(en) / organisatie(s) waarvoor dit uitvraagformulier geldt: | `opdrachtgever-kvk` | tekst | — | — | | | `customer.legalId[0].value` |
| Type identificatienummer | `opdrachtgever-kvk-type` | keuzelijst | KvK → `KvK` · OIN → `OIN` · RSIN → `RSIN` | — | | | `customer.legalId[0].schemeAgencyId` |
| In welke sector ben je actief? | `sector` | tekst | — | — | | | `labourAgreements.industryIdentifier[0].value` |

Hulptekst bij `opdrachtgever-kvk-type`: *"Is er geen KvK nummer? Kies dan voor een ander identificatienummer
(bijvoorbeeld het OIN)."*

## Hoe zijn de arbeidsvoorwaarden voor jouw eigen werknemers geregeld?

| Vraag | Slug | Type | Opties (label → waarde → SETU-waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| *(bloktitel is de vraag)* | `cao-of-regeling` | radio | Er is een cao van toepassing → `cao-van-toepassing` → `false` · Er is of zijn (een) eigen arbeidsvoorwaardenregeling(en) van toepassing → `eigen-arbeidsvoorwaardenregeling` → `true` · Er is een cao van toepassing en wij hebben (een) eigen arbeidsvoorwaardenregeling(en) → `cao-en-eigen-arbeidsvoorwaardenregeling` → `true` · Er is geen cao of arbeidsvoorwaardenregeling van toepassing → `geen-cao-of-arbeidsvoorwaardenregeling` → `false` | — | | | `labourAgreements.customLabourAgreement` (boolean) |

De keuze bepaalt welke uitleg (alert) getoond wordt:

| Keuze | Alert |
|---|---|
| `cao-van-toepassing` | Vul dit formulier in op basis van deze cao als minimum. |
| `eigen-arbeidsvoorwaardenregeling` | Vul dit formulier in op basis van deze eigen arbeidsvoorwaardenregeling. |
| `cao-en-eigen-arbeidsvoorwaardenregeling` | Vul dit formulier in op basis van de arbeidsvoorwaardenregeling met de cao als minimum. |
| `geen-cao-of-arbeidsvoorwaardenregeling` | Vul dit formulier in op basis van de arbeidsvoorwaarden van de eigen medewerker(s). |

**Let op:** de vier formulieropties worden in SETU teruggebracht tot een boolean, dus deze keuze is vanuit SETU
alleen terug te halen via `__webform_data__`.

## Welke cao is van toepassing?

Het hele blok is zichtbaar als `cao-of-regeling` = `cao-van-toepassing` **of** `cao-en-eigen-arbeidsvoorwaardenregeling`.

| Vraag | Slug | Type | Opties (label → waarde) | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam cao: | `cao-naam` | tekst | — | (blok) | | | `labourAgreements.collectiveLabourAgreement.name` |
| Nummer cao: | `cao-nummer` | tekst | — | (blok) | | | `labourAgreements.collectiveLabourAgreement.id.value` |
| Wat geldt er binnen jouw onderneming? | `cao-van-toepassing-omdat` | radio | Je onderneming is lid van de brancheorganisatie → `lid-brancheorganisatie` · De cao is algemeen verbindend verklaard → `algemeen-verbindend` · De cao wordt van toepassing verklaard in de arbeidsovereenkomst van de werknemers → `in-arbeidsovereenkomst` | (blok) | | | `labourAgreements.collectiveLabourAgreement.basedOn` (formulierwaarde als tekst) |
| ↳ van | `cao-van` | datum | — | `cao-van-toepassing-omdat` = `algemeen-verbindend` | | | `labourAgreements.collectiveLabourAgreement.effectivePeriod.validFrom` |
| ↳ tot | `cao-tot` | datum | — | `cao-van-toepassing-omdat` = `algemeen-verbindend` | | | `labourAgreements.collectiveLabourAgreement.effectivePeriod.validTo` |

Info bij het cao-nummer: *"Het cao-nummer vind je in de CBS-codelijst cao's en overige
arbeidsvoorwaardenregelingen"* (link naar cbs.nl).

Toelichting in het blok: *"Een cao is van toepassing als de werkgever lid is van de brancheorganisatie, doordat
de cao door de minister van SZW algemeen verbindend is verklaard voor de sector waarin de werkgever actief is of
omdat deze in de arbeidsovereenkomst van de medewerker van toepassing wordt verklaard."*

## Uitgeschakeld in de code

Er staat nog een oude, uitgecommentarieerde versie van de KvK-vraag (`opdrachtgever-kvk`). Die is vervangen door
de actieve vraag hierboven.

---

**Telling:** 6 tekst · 4 datum · 3 radio/keuzelijst · 0 checkbox (13 vragen), 4 alerts.
