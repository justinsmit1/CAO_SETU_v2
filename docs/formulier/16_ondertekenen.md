# 16 · Ondertekenen

Bron: `src/definition/16_ondertekenen.tsx` (webformulier v2.1.0).

**Structuur:** één subsectie zonder menu-label. Een herhaalbare lijst contactpersonen (minstens één), gevolgd
door een verplichte akkoordverklaring.

## Contactpersonen (herhaalbaar)

Herhaalbaar: `contactpersonen[i]`. De eerste rij heeft de titel *"Contactgegevens persoon die dit
uitvraagformulier invult"*, de volgende rijen *"Extra contactpersoon {i}"*. Knoppen: *Extra contactpersoon
toevoegen*, en *Contactpersoon verwijderen* (alleen zichtbaar als er meer dan één rij is). De Store zorgt dat
er altijd minstens één rij is.

| Vraag | Slug | Type | Opties | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Naam: | `contactpersonen[i]/naam` | tekst | — | — | | ja | `customer.personContacts[i].name.formattedName` |
| E-mailadres: | `contactpersonen[i]/email` | tekst | — | — | | ja | `customer.personContacts[i].communication.email[0].address` |
| Telefoonnummer: | `contactpersonen[i]/telefoon` | tekst | — | — | | ja | `customer.personContacts[i].communication.phone[0].formattedNumber` |
| Functie: | `contactpersonen[i]/functie` | tekst | — | — | | ja | `customer.personContacts[i].positionTitle` |

## Verklaring

| Vraag | Slug | Type | Opties | Toon als | Opt. | Herh. | SETU |
|---|---|---|---|---|---|---|---|
| Ik verklaar bevoegd te zijn tot het het verstrekken van de gevraagde informatie aan de uitzendonderneming. Ik verklaar tevens alle arbeidsvoorwaarden die van belang zijn voor het vaststellen van de gelijkwaardige beloning van de uitzendkracht, volledig en correct door te geven. Wanneer er op onderdelen niets wordt ingevuld wordt ervan uitgegaan dat de desbetreffende arbeidsvoorwaarde niet van toepassing is. Ik verklaar bovendien wijzigingen in de arbeidsvoorwaarden direct door te geven zodra deze bekend zijn. | `ondertekening-akkoord` | checkbox | — | — | nee (verplicht) | | — |

**Let op:**
- Het formulier vult `personContacts[i].roleCode` niet in. Het SETU-voorbeeld gebruikt daar "Authorized by".
- De akkoordverklaring gaat niet naar SETU, alleen naar `__webform_data__`.
- De verklaring bevat een typfout uit de bron ("tot het het"). Die is hier letterlijk overgenomen.

---

**Telling:** 4 tekst (per contactpersoon) · 0 datum · 0 tijd · 0 radio · 1 checkbox (5 vragen), 0 alerts.
