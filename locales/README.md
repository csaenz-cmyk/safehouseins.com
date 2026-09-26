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
gratis", "Llámanos"). Three exceptions keep *usted*: the legal documents
(privacy, SMS terms), which are legal text and what the 10DLC reviewers read;
the text messages in `sms/*.es.txt`, which match the SMS terms they send
people to (and stay unsent until the 10DLC approval in `docs/a2p-10dlc.md`);
and the lienholder page (`lienholder.json`), whose readers are bank and
finance-company staff writing to us on a customer's behalf. The shared menu and
footer on that page stay in *tú* like everywhere else.

**Write so the reader's gender does not matter** where it is easy: "¿Tienes
dudas?" rather than "¿No estás seguro?", "Quien solicita el seguro", options
such as "Casado(a)". Avoid *seguro* meaning "sure" — on an insurance site it
reads as the product.

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

Also correct, though the checker's word list would otherwise flag them:
*casa móvil* (a mobile home — *móvil* alone, a phone, is still out).
The SMS keywords stay in English everywhere, **STOP** and **HELP**: they are
the keywords the messaging platform answers to.

## How the words reach a page

**Generated pages** (everything under `tools/gen*.py`) ask for text with
`i18n.t('about.hero.h1')` or put `[[about.hero.h1]]` in a template, and write
each page once per language with `i18n.write()`. The Spanish copy lands at the
same path under `es/`. `t()` is strict: a key missing from a catalog stops the
build, so a page can never ship with a hole in it.

**Hand-kept pages** — `index.html`, `quote.html`, `contact.html`, `404.html`,
`pay/`, `claims/` (and their guides), `id-card/`, `lienholder/` — keep their
layout, styles and scripts in the English file as before. Their words are
marked where they sit (`<!--t:key-->…<!--/t-->`, `data-t="key"`,
`data-t-placeholder="key"` and friends), and `python3 tools/genlocale.py`
rewrites the English file from `locales/en` and writes the Spanish twin from
`locales/es`. **Edit the words in the catalog, not between the markers** — the
next run puts the catalog's text back, and prints a note naming every marker it
had to correct. The shared pieces (menu, footer, language switch, hreflang
head) are blocks the tool writes whole; see the docstring in `genlocale.py`.

**Words a page script puts on screen** are in the catalog too, under
`<namespace>.js.*`, and reach the page as a JSON block that `T('key')` reads
(`T('vehicleN', {n: 2})` fills placeholders). In the browser a missing key
shows nothing and logs an error — never the key itself — and
`tools/i18ncheck.py` makes sure it never gets that far.

### Option labels and the values behind them

A form option submits the English value the AMS expects whatever language it
is shown in. In markup the value is written out (`<option value="Rent"
data-t="…">`). In `quote.html`'s script, lists of values are kept in English and
their labels are looked up by a slug of the value:
`quote.js.opt.<group>.<slug>` — `opt.country.mexico`, `opt.occ.carpenter`,
`opt.mtype.dual-sport`. To add an option, add the value to the script's list
and the label to **both** catalogs under that key.

### Words that are recorded, not just shown

`quote.js.smsConsentText` and `quote.js.disclosureText` are what the quote form
sends the AMS as the record of what a person agreed to, in the language they
saw it in. Change either — in either language — only on purpose, and when the
disclosure changes, date its language's `quote.js.disclosureVersion`.

### Pictures with words in them

A picture whose text needs translating gets a twin beside it:
`assets/step-1.webp` → `assets/step-1.es.webp`. Every Spanish page uses the twin
wherever the English page uses the original, automatically. Pictures without a
twin are shown as they are, so check new artwork for English text.

The five homepage phone screens are rebuilt rather than retouched:
`tools/mockups/step-N.html` holds each screen as HTML, its words come from
`art.json`, and `python3 tools/genmockups.py` renders `step-N.es.webp` at the
original's exact size. It needs a browser and the network (for the typeface),
so it is not part of the page rebuild — run it when `art.json` or a template
changes, and look at every picture before committing it. It never writes the
English originals.

Known and accepted: the product-page illustrations in `assets/who/` carry a
few English prop labels ("NO DRIVER LICENSE", "PASSPORT") that are about three
pixels tall at the size they are shown, and are marked decorative (`alt=""`).

## Adding a page

1. English and Spanish copy in a namespace file in both `locales/en` and
   `locales/es` (a new file is a new namespace).
2. A generated page: write it with `i18n.write(rel, doc)` inside
   `for code in i18n.targets(): with i18n.language(code):`, and give
   `shell.head()` its `path`, `up` and `link` so the canonical, hreflang and the
   switch point at the right twins. A hand-kept page: add it to `PAGES` in
   `tools/genlocale.py` and put the blocks and markers in.
3. `python3 tools/i18ncheck.py` — every English page must have its Spanish twin.

## Checking

```
python3 tools/i18ncheck.py            # catalogs and built pages, both languages
python3 tools/i18ncheck.py --accept   # after reviewing changed Spanish
NODE_PATH=/opt/node22/lib/node_modules node tools/i18nbrowser.js   # in a browser
```
