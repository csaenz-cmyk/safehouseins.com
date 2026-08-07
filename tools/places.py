"""Per-city content for the car-insurance location pages.

This is the file that decides whether these pages are worth existing. Shared
components are fine; shared *content* is a doorway-page pattern and Google
treats a doorway set as a single page. So nothing in here is a template with a
name substituted — every entry is written for that city.

A city only gets a section if there is something true and useful to put in it.
A page with four good sections beats a page with nine padded ones, and short
pages are fine. `citykit` omits any section whose data is missing.

Row shape, all keys optional except `scene`:

  scene     which cityscape illustration (see cityscape.SCENES)
  blurb     the hero sub-line. One sentence, specific to this place.
  chips     up to four short hero chips
  zips      [(zip, area name)] — real ZIPs, for the ZIP selector
  areas     [(area, one useful line)] — for the area explorer
  factors   [(icon, heading, body)] — the local driving considerations
  intents   which "what brings you here" cards to show, in order
  faq       [(question, answer)] — city-specific, appended to the state FAQ
  presence  'office' only where Safe House genuinely has one. Otherwise
            'serving', which renders as "Serving drivers throughout X".
  links     [(href, label)] — genuinely relevant internal links

Rules this file is written under:
  * No average premiums, no "drivers here save", no accident/crime/weather
    statistics. We have no maintainable source for any of it.
  * No claim that one ZIP or area is cheaper or dearer than another.
  * `presence: 'office'` is a factual claim about a physical location. El Paso
    is the only one, because 6065 Montana Ave is the only office there is.
"""

# The intent cards. Text is shared because the situation is the same
# everywhere; which ones appear, and in what order, is per city.
INTENTS = {
 'cheaper': ('car', 'I need cheaper insurance',
   'The most common reason people call us. We put your details in front of every carrier we '
   'represent at once and show you what each one came back with, rather than defending a single '
   'company&rsquo;s number.', 'Compare my options'),
 'renewal': ('trend', 'My renewal went up',
   'Renewal increases often have nothing to do with you &mdash; carriers re-rate whole segments at '
   'once. It is worth finding out whether your carrier still wants your business before you simply '
   'pay the new number.', 'Check what else is out there'),
 'sr22':    ('doc', 'I need an SR-22',
   'An SR-22 is not insurance. It is a form your insurer files with the state to confirm you carry '
   'the required liability coverage. Not every carrier files them, which is exactly why shopping '
   'matters here.', 'Talk to an agent'),
 'bought':  ('key', 'I just bought a car',
   'Need coverage before you leave the dealership? Tell us the vehicle and we will compare '
   'available options from the companies we represent. Have the VIN handy if you can &mdash; it '
   'makes the quote far more accurate.', 'Start my quote'),
 'noprior': ('shield', 'I don&rsquo;t have prior insurance',
   'A gap in coverage does make a quote harder, and it does not make it impossible. Carriers '
   'differ a lot in how they treat a lapse, so this is a case where seeing several at once is '
   'worth more than usual.', 'See who will write me'),
 'newdriver': ('user', 'I&rsquo;m a new driver',
   'A first policy, or a young driver being added to a household one. Which carrier is reasonable '
   'about it varies more than people expect, and so does whether a good-student discount applies.',
   'Get my first quote'),
 'switch':  ('swap', 'I want to switch companies',
   'You can change carriers mid-term &mdash; you are usually refunded the unused part of what you '
   'paid. The thing to avoid is a gap between the two policies, and we will make sure there is '
   'not one.', 'Compare before I switch'),
 'mexico':  ('border', 'I drive into Mexico',
   'A U.S. auto policy generally does not provide the liability coverage Mexico requires. Driving '
   'south of the border usually means a separate Mexican policy for the days you are there. Ask us '
   'before the trip, not after.', 'Ask about Mexico coverage'),
 'commercial': ('truck', 'I use my vehicle for work',
   'Carrying tools or materials for pay, towing for money, delivery, or a vehicle titled to a '
   'business &mdash; a personal auto policy can deny a claim that happened while working. Tell us '
   'what it actually does.', 'Ask about commercial'),
}

PLACES = {

# ---------------------------------------------------------------- El Paso ---
'texas:el-paso': dict(
  scene='desert-mountains',
  presence='office',
  blurb='Compare options from multiple insurance companies with help from a licensed Safe House '
        'agent &mdash; in English or Spanish, from an office on Montana Ave.',
  chips=['El Paso, TX', 'Multiple carriers', 'English &amp; Spanish', 'Local office'],

  zips=[('79901', 'Downtown'), ('79902', 'Central'), ('79903', 'Central'),
        ('79904', 'Northeast'), ('79905', 'Central'), ('79907', 'Lower Valley'),
        ('79912', 'West Side'), ('79915', 'Lower Valley'), ('79922', 'Upper Valley'),
        ('79924', 'Northeast'), ('79925', 'East Central'), ('79928', 'Horizon City'),
        ('79930', 'Central'), ('79932', 'Upper Valley'), ('79934', 'Far Northeast'),
        ('79935', 'East'), ('79936', 'East'), ('79938', 'Far East')],

  areas=[
    ('West Side',
     'Between the Franklins and the river, with most through traffic funnelling onto I-10. '
     'Long commutes east are common from here.'),
    ('Central',
     'The oldest part of the city and the closest to the international bridges. Short trips, '
     'dense streets, and a lot of stop-start driving.'),
    ('Northeast',
     'On the far side of the mountain from the West Side, which is why the drive between them '
     'goes around rather than through.'),
    ('East Side',
     'The bulk of the city&rsquo;s growth, and the reason so many El Paso commutes are long '
     'east-west runs on I-10 or Montana.'),
    ('Far East and Horizon',
     'Newer subdivisions well east of Loop 375. Commutes from out here are among the longest in '
     'the city.'),
    ('Lower Valley',
     'Along the river southeast of downtown, following Alameda and North Loop rather than the '
     'interstate.'),
    ('Upper Valley',
     'North-west along the Rio Grande toward Canutillo, semi-rural in places, with fewer routes '
     'in and out than the map suggests.'),
  ],

  factors=[
    ('road', 'The I-10 run across town',
     'El Paso is long and thin &mdash; roughly forty miles from the Upper Valley to Horizon &mdash; '
     'and almost everything crosses I-10 at some point. Annual mileage is one of the things a '
     'carrier asks about, and people who drive the length of the city every day often estimate it '
     'far too low.'),
    ('border', 'Driving into Ju&aacute;rez',
     'A U.S. auto policy generally does not satisfy what Mexico requires of a driver, and physical '
     'damage cover usually stops at the border too. Crossing normally means a separate Mexican '
     'policy for the days you are there. Worth sorting out before the trip rather than at the '
     'bridge.'),
    ('home', 'Where the vehicle sleeps',
     'Carriers rate on the address the vehicle is garaged at overnight, not the one on your '
     'licence. In a city this spread out that is a real distinction &mdash; people move across '
     'town and forget to tell anyone, and a claim is the wrong moment to find out the policy has '
     'the old address.'),
    ('lang', 'English or Spanish, whichever is easier',
     'Insurance is a bad thing to half-understand. Our agents work in both languages, in person on '
     'Montana Ave, on the phone, or by text &mdash; and the policy documents themselves can be '
     'gone through line by line either way.'),
    ('sun', 'Sun, hail and the odd flash flood',
     'Comprehensive is the part of the policy that covers hail, flooding, theft and a cracked '
     'windscreen &mdash; not collision, and not liability. It is subject to your deductible and to '
     'the terms of the policy, and it is the coverage most often dropped by people who then need '
     'it.'),
  ],

  intents=['cheaper', 'renewal', 'sr22', 'bought', 'noprior', 'newdriver', 'switch', 'mexico'],

  faq=[
    ('Does my Texas auto insurance cover me when I drive into Mexico?',
     '<p>Generally not in the way you need it to. A standard U.S. auto policy does not usually '
     'satisfy Mexico&rsquo;s liability requirements, and physical damage coverage often stops at '
     'the border as well. Most people crossing at the Ju&aacute;rez bridges buy a separate Mexican '
     'auto policy for the days they will be there.</p>'
     '<p>Ask us before you go. It is quick to arrange and it is not something you want to discover '
     'at the border or, worse, after an accident.</p>'),
    ('Can Safe House help me in Spanish?',
     '<p>Yes &mdash; on the phone, by text, and in person at the office on Montana Ave. Se habla '
     'espa&ntilde;ol.</p>'
     '<p>That includes going through the policy itself rather than just the price. Coverage terms '
     'are where the confusion usually is, and they are worth understanding in whichever language '
     'you think in.</p>'),
    ('Do you have an actual office in El Paso?',
     '<p>Yes. Safe House Insurance is at 6065 Montana Ave, Suite C8, El Paso, TX 79925. You can '
     'call ' + '915-503-1207' + ', text 915-594-3777, or come in.</p>'
     '<p>The quote itself can be done entirely online if you prefer &mdash; but a licensed agent '
     'reviews it with you before anything is issued either way.</p>'),
  ],

  links=[('../../../quote.html', 'Get a car insurance quote'),
         ('../', 'Car insurance in Texas'),
         ('../../makes/', 'Car insurance by vehicle make'),
         ('../../ford/', 'Ford insurance'),
         ('../../chevrolet/', 'Chevrolet insurance'),
         ('../../toyota/', 'Toyota insurance')],
),
}

def get(state, slug):
    return PLACES.get(state + ':' + slug)

def has(state, slug):
    return (state + ':' + slug) in PLACES
