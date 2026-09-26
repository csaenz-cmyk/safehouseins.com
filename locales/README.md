# Locales — every word a customer reads, in English and Spanish

Each language has one folder, and the two folders hold the same files with the
same keys:

```
locales/en/common.json    locales/es/common.json    menu, header, footer, shared CTAs
locales/en/home.json      locales/es/home.json      index.html
locales/en/quote.json     locales/es/quote.json     the quote form, including its scripts
...
```

A key is the file name plus the path inside it: `common.menu.car` is
`"menu": {"car": ...}` in `common.json`. Generators ask for text by key with
`i18n.t('common.menu.car')`; hand-kept pages carry the key in the markup (see
`tools/genlocale.py`). The layout of a page exists once — the words are the
only thing that changes between languages.

## Rules that the build enforces

`python3 tools/i18ncheck.py` fails when any of these is broken:

- Both languages have exactly the same keys, and the same shape for structured
  content (a guide body with five sections has five in Spanish too).
- The same `{placeholders}` on both sides. `{city}` in English and `{ciudad}`
  in Spanish would render a literal `{ciudad}`.
- The same inline markup on both sides — a `<b>` or a link in English has one
  in Spanish.
- No Spanish value is left identical to the English one unless it is on the
  short list of things that are the same in both languages (brand names,
  phone numbers, "SR-22").
- No Castilian forms: *vosotros*, *coche*, *conducir*, *ordenador*, *móvil*…
  (the full list is in `tools/i18ncheck.py`).
- **Stale translations.** `locales/es.lock.json` records the English each
  Spanish string was written against. Change the English and the check names
  every Spanish string that now needs a second look; update the Spanish, then
  run `python3 tools/i18ncheck.py --accept` to record that it was reviewed.

## Writing the Spanish

**Mexican Spanish, as a bilingual agency on the border speaks it to a
customer.** Not Castilian, and not a word-for-word copy of the English.
Rewrite a sentence when the literal version would be awkward; keep the
meaning, the facts and every caveat.

**Tú, not usted**, across the site and the quote form — the English is direct
and warm, and *tú* is how that sounds in Spanish ("Obtén tu cotización
gratis", "Llámanos"). The two legal documents (privacy, SMS terms) keep
*usted*: they are legal text, they were written that way and they are what the
10DLC reviewers read.

**Never translate:** Safe House Insurance; carrier and product names
(Progressive, GEICO, Chubb, TurboRater…); Uber, Lyft, DoorDash; phone numbers,
email addresses and the street address; policy numbers and prefixes; people's
names; customer reviews (they are the customer's words — show them as
written); SR-22, DWI, PIP, VIN, ITIN. Keep SR-22 intact and translate around
it: "conductores que necesitan SR-22", "seguro con SR-22".

**Form values stay English.** A `<select>` shows Spanish but submits the value
the AMS expects ("Married", "$500", "100/300/100"). Translate the label, never
the `value`.

**Style.** Sentence case in headings ("Cómo comparar cotizaciones", not
"Cómo Comparar Cotizaciones"). Opening ¿ and ¡. Days and months lowercase.
Dates as "6 de agosto de 2026". Money as in the English — `$1,000`, which is
also how it is written in Mexico. Curly quotes “ ” as in the English copy.

### Glossary

Use these consistently. Where a customer's own policy documents will be in
English, name the English term once in parentheses in explanatory copy —
"cobertura integral (comprehensive)" — so they can find it on their dec page.

| English | Español |
| --- | --- |
| car insurance | seguro de auto |
| car / vehicle | carro, auto, vehículo — never *coche* |
| drive, driving | manejar — never *conducir* |
| driver | conductor |
| driver's license | licencia de manejo |
| foreign license | licencia extranjera |
| quote (n.) / to quote | cotización / cotizar |
| Get my free quote | Obtén tu cotización gratis |
| policy | póliza |
| premium | prima (in plain copy: "lo que pagas", "el precio") |
| deductible | deducible |
| coverage | cobertura |
| full coverage | cobertura completa |
| liability | responsabilidad civil; plain: daños a terceros |
| liability insurance | seguro de responsabilidad civil |
| bodily injury / property damage liability | lesiones corporales / daños a la propiedad |
| comprehensive | cobertura integral (comprehensive) |
| collision | cobertura de colisión (collision) |
| uninsured / underinsured motorist | conductor sin seguro / con seguro insuficiente |
| medical payments (MedPay) | gastos médicos (MedPay) |
| PIP | protección contra lesiones personales (PIP) |
| roadside assistance | asistencia vial |
| towing | grúa |
| rental reimbursement | auto de renta |
| claim / file a claim | reclamo / reportar un reclamo |
| adjuster | ajustador |
| at fault | tener la culpa; accidente con culpa |
| ticket | multa |
| lapse in coverage | un periodo sin seguro; se venció el seguro |
| carrier, insurance company | aseguradora, compañía de seguros |
| independent agency | agencia independiente |
| licensed agent | agente con licencia |
| declarations page | hoja de declaraciones (dec page) |
| ID card | tarjeta de seguro |
| proof of insurance | comprobante de seguro |
| lienholder | la financiera o el banco (acreedor prendario) |
| endorsement | endoso |
| down payment | enganche |
| monthly payment | pago mensual, mensualidad |
| pay in full | pagar de contado |
| renewal | renovación |
| homeowners insurance | seguro de casa |
| renters insurance | seguro para inquilinos |
| mobile home | casa móvil |
| rent (v.) | rentar — never *alquilar* |
| commercial auto | seguro de auto comercial |
| general liability | responsabilidad civil general |
| work truck / fleet | camioneta de trabajo / flotilla |
| rideshare & delivery | viajes con apps y entregas (Uber, Lyft, DoorDash) |
| motorcycle | motocicleta, moto |
| cell phone | celular — never *móvil* |
| text us | mándanos un mensaje |
| call us | llámanos |
| ZIP code | código postal |
| make / model / year | marca / modelo / año |
| Mountain Time | hora de la montaña |
| New Mexico | Nuevo México |
| Mon–Fri, 11am–5pm | lun. a vie., 11 a. m. a 5 p. m. |
