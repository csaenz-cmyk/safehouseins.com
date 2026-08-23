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
 'cheaper': ('car', 'I need cheaper insurance', [
   'The most common reason people call us. We put your details in front of every carrier we '
   'represent at once and show you what each one came back with, rather than defending a single '
   'company&rsquo;s number.',
   'Cheaper usually means a different company rather than less coverage. One form, several '
   'carriers, and the spread between them in front of you &mdash; that spread is the entire reason '
   'an independent agency exists.',
   'Before cutting coverage, it is worth finding out what somebody else would charge for the same '
   'coverage. We shop it across the companies we represent and you see all of the answers, not '
   'one.'], 'Compare my options'),
 'renewal': ('trend', 'My renewal went up', [
   'Renewal increases often have nothing to do with you &mdash; carriers re-rate whole segments at '
   'once. It is worth finding out whether your carrier still wants your business before you simply '
   'pay the new number.',
   'A renewal is a price your current company picked without competition. Re-shopping it is the '
   'only way to know whether the increase reflects the market or just that company&rsquo;s appetite '
   'changing.',
   'Nothing about your record has to change for a renewal to move. If yours jumped, the useful '
   'question is not why &mdash; it is what everyone else would charge you today.'], 'Check what else is out there'),
 'sr22':    ('doc', 'I need an SR-22', [
   'An SR-22 is not insurance. It is a form your insurer files with the state to confirm you carry '
   'the required liability coverage. Not every carrier files them, which is exactly why shopping '
   'matters here.',
   'The SR-22 itself is paperwork &mdash; a filing your insurance company makes on your behalf. The '
   'part that matters is finding a carrier that both writes your policy and files the form, and '
   'they are not all willing.'], 'Talk to an agent'),
 'bought':  ('key', 'I just bought a car', [
   'Need coverage before you leave the dealership? Tell us the vehicle and we will compare '
   'available options from the companies we represent. Have the VIN handy if you can &mdash; it '
   'makes the quote far more accurate.',
   'Buying is the moment worth re-shopping everything, not just adding the new car to the old '
   'policy. The vehicle changed, so the rating changed, and the company that was cheapest for the '
   'last one may not be for this one.'], 'Start my quote'),
 'noprior': ('shield', 'I don&rsquo;t have prior insurance', [
   'A gap in coverage does make a quote harder, and it does not make it impossible. Carriers '
   'differ a lot in how they treat a lapse, so this is a case where seeing several at once is '
   'worth more than usual.',
   'Some companies treat a lapse as disqualifying and some barely blink. Since you cannot tell '
   'which is which from the outside, putting the same details to all of them at once is the only '
   'sensible approach.'], 'See who will write me'),
 'newdriver': ('user', 'I&rsquo;m a new driver', [
   'A first policy, or a young driver being added to a household one. Which carrier is reasonable '
   'about it varies more than people expect, and so does whether a good-student discount applies.',
   'First policies are where the spread between companies is widest, because there is no record to '
   'rate on yet. Ask about the good-student discount &mdash; it is real, and nobody applies it for '
   'you.'], 'Get my first quote'),
 'switch':  ('swap', 'I want to switch companies', [
   'You can change carriers mid-term &mdash; you are usually refunded the unused part of what you '
   'paid. The thing to avoid is a gap between the two policies, and we will make sure there is '
   'not one.',
   'Switching does not have to wait for renewal. The one rule is that the new policy starts before '
   'the old one ends &mdash; a gap of even a few days follows you into future quotes.'], 'Compare before I switch'),
 'mexico':  ('border', 'I drive into Mexico', [
   'A U.S. auto policy generally does not provide the liability coverage Mexico requires. Driving '
   'south of the border usually means a separate Mexican policy for the days you are there. Ask us '
   'before the trip, not after.',
   'Your U.S. policy and driving legally in Mexico are two different things. A separate Mexican '
   'auto policy is the normal answer, bought for the days you will be down there. It takes '
   'minutes to arrange in advance and cannot be fixed afterwards.'], 'Ask about Mexico coverage'),
 'commercial': ('truck', 'I use my vehicle for work', [
   'Carrying tools or materials for pay, towing for money, delivery, or a vehicle titled to a '
   'business &mdash; a personal auto policy can deny a claim that happened while working. Tell us '
   'what it actually does.',
   'The question is not what the vehicle is, it is what it does. Hauling your own things is one '
   'thing; hauling anyone else&rsquo;s for money is another, and so is a truck registered to a '
   'company.'], 'Ask about commercial'),
}

PLACES = {

# ----------------------------------------------------------------- Laredo ---
'texas:laredo': dict(
  scene='valley', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'en ingl&eacute;s o en espa&ntilde;ol, and we can talk about crossing before you cross.',
  chips=['Laredo, TX', 'Multiple carriers', 'English &amp; Spanish', 'Border region'],
  zips=[('78040', 'Downtown and El Centro'), ('78041', 'North Central'),
        ('78043', 'East and Southeast'), ('78045', 'North and Northwest'),
        ('78046', 'South and Southeast')],
  areas=[
    ('Downtown and El Centro', 'Closest to the Gateway and Ju&aacute;rez-Lincoln bridges. Tight '
     'older streets, a lot of stop-start driving, and mostly street or lot parking.'),
    ('North Laredo', 'Newer subdivisions out past Del Mar and toward the Loop. Longer daily trips '
     'and more garage and driveway parking than the center.'),
    ('The Loop 20 corridor', 'The Bob Bullock Loop does most of the crosstown work, which is why so '
     'much local driving here is highway driving rather than surface streets.'),
    ('South Laredo', 'Along US 83 down the river. Longer distances into town, and closer to the '
     'commercial traffic heading for the bridges.'),
    ('East and Santa Maria', 'Out toward US 59, where the city thins out and trips get longer '
     'without feeling like it.'),
  ],
  factors=[
    ('border', 'Crossing to Nuevo Laredo',
     'This is the question we get asked most here. A U.S. auto policy generally does not provide '
     'the liability coverage Mexico requires of a driver, and physical damage cover usually stops '
     'at the border. Crossing normally means a separate Mexican policy for the days you are there '
     '&mdash; arranged before you go, because it cannot be fixed at the bridge.'),
    ('truck', 'A city built around freight',
     'Laredo is one of the busiest commercial land ports in the country, and a lot of households '
     'here have a vehicle that does something for work. If yours carries tools or materials for '
     'pay, tows for money, or is titled to a company, a personal auto policy can deny a claim that '
     'happened on the job.'),
    ('road', 'I-35 starts here, and Loop 20 carries the rest',
     'Between the interstate, the loop and US 83 along the river, a lot of everyday driving in '
     'Laredo happens at highway speed. Annual mileage is something a carrier asks about, and it is '
     'the figure people most often estimate from memory.'),
    ('lang', 'En espa&ntilde;ol, con una persona',
     'Nuestros agentes trabajan en espa&ntilde;ol por tel&eacute;fono o por mensaje. Los t&eacute;rminos '
     'de cobertura son donde est&aacute; la confusi&oacute;n, y vale la pena entenderlos en el idioma en '
     'que uno piensa.'),
  ],
  intents=['cheaper', 'mexico', 'renewal', 'bought', 'commercial', 'sr22', 'noprior', 'switch'],
  faq=[
    ('Does my Texas insurance cover me in Nuevo Laredo?',
     '<p>Generally not in the way you need. A standard U.S. auto policy does not usually satisfy '
     'Mexico&rsquo;s liability requirements, and physical damage coverage commonly stops at the '
     'border. Most people crossing here buy a separate Mexican auto policy covering the days they '
     'will be over.</p>'
     '<p>It takes minutes to arrange in advance and nothing can be done about it afterwards, which '
     'is the whole reason to ask before the trip rather than after.</p>'),
    ('&iquest;Puedo hacer todo esto en espa&ntilde;ol?',
     '<p>S&iacute;. Por tel&eacute;fono, por mensaje de texto, o en persona en nuestra oficina de El '
     'Paso. Hablamos espa&ntilde;ol.</p>'
     '<p>Y no solo el precio &mdash; tambi&eacute;n repasamos la p&oacute;liza l&iacute;nea por '
     'l&iacute;nea, porque ah&iacute; es donde normalmente est&aacute;n las dudas.</p>'),
  ],
  links=[('../../../quote.html', 'Get a car insurance quote'), ('../', 'Car insurance in Texas'),
         ('../mcallen/', 'Car insurance in McAllen'),
         ('../../makes/', 'Car insurance by vehicle make'), ('../../ram/', 'Ram truck insurance')],
),

# ---------------------------------------------------------------- McAllen ---
'texas:mcallen': dict(
  scene='valley', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'en ingl&eacute;s o en espa&ntilde;ol, para toda el &aacute;rea del Valle.',
  chips=['McAllen, TX', 'Multiple carriers', 'English &amp; Spanish', 'Rio Grande Valley'],
  zips=[('78501', 'Central and South'), ('78503', 'South and near the bridge'),
        ('78504', 'North McAllen')],
  areas=[
    ('North McAllen', 'Around Trenton and Nolana. Newer housing, more garages and driveways, and '
     'longer drives to the south side of town.'),
    ('Central McAllen', 'The older grid around Main and Bicentennial. Short trips and a lot of '
     'stop-start driving on the 10th Street corridor.'),
    ('South McAllen', 'Down toward Hidalgo and the international bridge, with the heaviest '
     'cross-border and retail traffic in the city.'),
    ('The expressway corridor', 'US 83 &mdash; now signed I-2 &mdash; runs the length of the Valley '
     'and is how most of McAllen connects to Mission, Pharr and Edinburg.'),
  ],
  factors=[
    ('border', 'The bridges at Hidalgo and Anzalduas',
     'Crossing is routine here, and a U.S. auto policy is generally not what Mexico asks of a '
     'driver. A separate Mexican policy for the days you are there is the normal answer, and it has '
     'to be arranged before you go.'),
    ('road', 'One expressway, four cities',
     'The Valley runs east to west on a single expressway corridor, so a McAllen household often '
     'works in Pharr, shops in Edinburg and has family in Mission. Those are real annual miles, and '
     'mileage is one of the things carriers ask about.'),
    ('lang', 'Le atendemos en espa&ntilde;ol',
     'Por tel&eacute;fono o por mensaje, en el idioma que prefiera. Explicamos la cobertura, no '
     'solamente el precio.'),
    ('home', 'Where the vehicle is kept',
     'Rated on the address the vehicle parks at overnight rather than the one on your license. In '
     'the Valley people move between neighbouring cities more than most places, and the policy has '
     'to follow.'),
  ],
  intents=['cheaper', 'mexico', 'renewal', 'bought', 'noprior', 'newdriver', 'switch', 'sr22'],
  faq=[
    ('Can I use my U.S. insurance when I cross at Hidalgo or Anzalduas?',
     '<p>Generally not for the liability Mexico requires, and physical damage cover commonly stops '
     'at the border. A separate Mexican auto policy for the days of the trip is the usual answer.</p>'
     '<p>Ask before you cross. It is quick to arrange in advance and impossible to sort out '
     'afterwards.</p>'),
    ('&iquest;Atienden a clientes en espa&ntilde;ol en el Valle?',
     '<p>S&iacute;, por tel&eacute;fono y por mensaje de texto. Somos una agencia independiente con '
     'licencia en Texas y Nuevo M&eacute;xico, con oficina en El Paso.</p>'
     '<p>Repasamos la p&oacute;liza completa con usted, no solo la cifra final.</p>'),
  ],
  links=[('../../../quote.html', 'Get a car insurance quote'), ('../', 'Car insurance in Texas'),
         ('../brownsville/', 'Car insurance in Brownsville'), ('../laredo/', 'Car insurance in Laredo'),
         ('../../makes/', 'Car insurance by vehicle make')],
),

# ---------------------------------------------------------------- Lubbock ---
'texas:lubbock': dict(
  scene='plains', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'including the hail and student-driver questions that come up on the South Plains.',
  chips=['Lubbock, TX', 'Multiple carriers', 'Student drivers', 'Fast quotes'],
  zips=[('79401', 'Downtown and Tech'), ('79403', 'Northeast'), ('79407', 'West'),
        ('79410', 'Central'), ('79411', 'Central'), ('79412', 'South Central'),
        ('79413', 'South'), ('79414', 'Southwest'), ('79415', 'North'),
        ('79416', 'Northwest'), ('79423', 'South'), ('79424', 'Southwest')],
  areas=[
    ('Tech and Overton', 'Around the university north-west of downtown. A high share of student '
     'drivers, apartment lots rather than garages, and short trips.'),
    ('Downtown and Central', 'The older grid inside the loop, with a mix of street and driveway '
     'parking.'),
    ('Southwest Lubbock', 'Where most of the newer housing has gone, out past 82nd toward the loop '
     'and beyond. Longer drives into town.'),
    ('North and Northeast', 'Older neighbourhoods and more of the city&rsquo;s industrial and '
     'agricultural traffic.'),
    ('Beyond Loop 289', 'The ring road is the dividing line between crosstown trips and genuine '
     'commutes, and a great deal of Lubbock driving happens on it.'),
  ],
  factors=[
    ('sun', 'Hail is a comprehensive claim',
     'The South Plains gets hail, and hail damage to a vehicle is covered by '
     '<strong>comprehensive</strong> &mdash; not collision, not liability. Comprehensive is '
     'optional, applies subject to your deductible, and is governed by the terms of the policy you '
     'hold. It is also the first coverage people drop on a paid-off vehicle.'),
    ('user', 'A university town',
     'A student away at Texas Tech without the car is often rated differently from one who takes it '
     'with them, and a good-student discount is real at many carriers. Neither is applied for you '
     '&mdash; both have to be asked for.'),
    ('road', 'One interstate and a ring road',
     'I-27 runs north toward Amarillo and Loop 289 wraps the city, so most crosstown driving here '
     'happens at speed rather than on surface streets. Annual mileage is something carriers ask '
     'about.'),
    ('home', 'Where the vehicle sits overnight',
     'Carriers rate on the garaging address, and a student apartment lot near campus and a house '
     'with a garage out past the loop are genuinely different answers.'),
  ],
  intents=['cheaper', 'newdriver', 'renewal', 'bought', 'noprior', 'switch', 'sr22'],
  faq=[
    ('Does my insurance cover hail damage in Lubbock?',
     '<p>Only if you carry <strong>comprehensive</strong> coverage. Hail is not a collision claim '
     'and liability does not touch it. Comprehensive is optional, applies subject to your '
     'deductible, and is subject to the terms and exclusions of your policy.</p>'
     '<p>If the vehicle is financed the lender almost certainly requires it. If it is paid off and '
     'you dropped it to save money, hail damage is your own cost &mdash; worth checking which one '
     'describes you before spring.</p>'),
    ('My student is at Texas Tech. How should the policy be set up?',
     '<p>It depends on whether the vehicle goes with them. A student living away at school without '
     'a car is often rated differently from one who keeps it on campus, and where the vehicle is '
     'garaged has to match reality either way.</p>'
     '<p>Ask about the good-student discount while you are at it. It exists at a lot of carriers, '
     'it is worth real money, and nobody applies it automatically.</p>'),
  ],
  links=[('../../../quote.html', 'Get a car insurance quote'), ('../', 'Car insurance in Texas'),
         ('../amarillo/', 'Car insurance in Amarillo'),
         ('../../makes/', 'Car insurance by vehicle make'), ('../../ford/', 'Ford insurance')],
),

# ------------------------------------------------------------- Rio Rancho ---
'new-mexico:rio-rancho': dict(
  scene='high-desert', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'including what a daily commute across the river does to a quote.',
  chips=['Rio Rancho, NM', 'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],
  zips=[('87124', 'south and City Center'), ('87144', 'north and Enchanted Hills')],
  areas=[
    ('City Center and the 528 corridor', 'Along NM 528, where most of the shopping, the offices and '
     'the everyday traffic are.'),
    ('Southern Rio Rancho', 'The older, denser part of the city and the closest to the river '
     'crossings into Albuquerque.'),
    ('Northern Meadows and Enchanted Hills', 'Newer subdivisions north along US 550. Longer '
     'commutes, and mostly garage and driveway parking.'),
    ('The West Mesa edge', 'Out toward Unser and Paseo del Volcan the grid thins out quickly, and '
     'distances between places get longer than they look on a map.'),
  ],
  factors=[
    ('road', 'A commuter city on the other side of the river',
     'A great many Rio Rancho households work in Albuquerque, and the two cities are joined by a '
     'small number of river crossings. That makes for a genuine daily commute rather than a '
     'crosstown trip &mdash; and annual mileage is one of the things a carrier asks about.'),
    ('home', 'Rio Rancho is not Albuquerque',
     'They sit next to each other and they are different cities in different counties. Your policy '
     'is rated on the address the vehicle parks at overnight, so if you moved across the river and '
     'never updated it, that is worth fixing before a claim rather than during one.'),
    ('sun', 'Hail, sun and a cracked windshield',
     'All three are <strong>comprehensive</strong> claims rather than collision. Comprehensive is '
     'optional, applies subject to your deductible, and is governed by the terms of your policy. '
     'It is usually the cheaper half of physical damage cover.'),
    ('lang', 'English or Spanish',
     'Our agents work in both, by phone or text. We go through the coverage itself, not just the '
     'price.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'noprior', 'switch', 'newdriver', 'sr22'],
  faq=[
    ('I moved from Albuquerque to Rio Rancho. Do I need to tell my insurance company?',
     '<p>Yes, and promptly. An auto policy is rated on the address where the vehicle is kept '
     'overnight, not on your mailing address or your license. Rio Rancho and Albuquerque are '
     'separate cities in separate counties, so the change is a real one.</p>'
     '<p>It is also a natural moment to re-shop rather than just update. The company that was '
     'cheapest at the old address is not automatically cheapest at the new one.</p>'),
  ],
  links=[('../../../quote.html', 'Get a car insurance quote'),
         ('../', 'Car insurance in New Mexico'), ('../albuquerque/', 'Car insurance in Albuquerque'),
         ('../../makes/', 'Car insurance by vehicle make')],
),

# ----------------------------------------------------------------- Dallas ---
'texas:dallas': dict(
  scene='metro-skyline', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'including the hail and comprehensive questions that come up across the Metroplex.',
  chips=['Dallas, TX', 'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],
  zips=[('75201', 'Downtown'), ('75204', 'Uptown'), ('75206', 'Lower Greenville'),
        ('75208', 'Oak Cliff'), ('75214', 'Lakewood'), ('75219', 'Oak Lawn'),
        ('75220', 'Northwest Dallas'), ('75224', 'South Oak Cliff'), ('75228', 'East Dallas'),
        ('75230', 'North Dallas'), ('75231', 'Vickery Meadow'), ('75235', 'Love Field'),
        ('75238', 'Lake Highlands'), ('75243', 'Northeast Dallas'), ('75248', 'Far North'),
        ('75252', 'Far North')],
  areas=[
    ('Downtown and Uptown', 'Dense, walkable by Texas standards, and mostly garage or lot parking '
     'rather than a driveway.'),
    ('Oak Cliff and the south', 'South of the Trinity, older street grids and a different set of '
     'routes into town than the northern suburbs use.'),
    ('East Dallas and Lakewood', 'Between I-30 and White Rock Lake. Shorter trips in, and a lot of '
     'on-street and driveway parking.'),
    ('North Dallas', 'Between LBJ and the Tollway. This is where a great many of the long '
     'north-south commutes start.'),
    ('Lake Highlands and the northeast', 'Inside and just outside I-635, feeding onto US 75 and '
     'the LBJ interchange.'),
    ('Far North and the Tollway corridor', 'Up toward Plano and Frisco. Long daily distances, and '
     'the part of the metro where toll roads do most of the work.'),
  ],
  factors=[
    ('sun', 'Hail is a comprehensive claim, not a collision one',
     'North Texas gets hail, and hail damage to a vehicle falls under <strong>comprehensive</strong> '
     'coverage &mdash; which is optional, applies subject to your deductible, and is governed by the '
     'terms of the policy you hold. Liability alone does not cover it. It is also the coverage '
     'people drop first on a paid-off car.'),
    ('road', 'Metroplex distances and the toll network',
     'I-35E, I-30, the LBJ loop and US 75, plus the Tollway and the Bush Turnpike. Using tolls does '
     'not change a quote; the mileage behind them does, and a Dallas-to-Fort Worth commute is a '
     'serious annual figure.'),
    ('home', 'Garage, driveway, lot or street',
     'Carriers ask where the vehicle sits overnight, and across a metro this size the answer '
     'changes street by street. It is rated on the garaging address, not the one on your license.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver', 'commercial'],
  faq=[('Does my insurance cover hail damage in Dallas?',
     '<p>Only if you carry <strong>comprehensive</strong> coverage. Hail is not collision and it is '
     'not liability. Comprehensive is optional, applies subject to your deductible, and is subject '
     'to the terms and exclusions of your policy.</p>'
     '<p>If your vehicle is financed the lender almost certainly requires it. If it is paid off and '
     'you dropped it, a hail claim is your own cost &mdash; worth checking which describes you '
     'before spring rather than after a storm.</p>')],
  links=[('../../../quote.html', 'Get a car insurance quote'), ('../', 'Car insurance in Texas'),
         ('../fort-worth/', 'Car insurance in Fort Worth'), ('../../makes/', 'Insurance by make')],
),

# ----------------------------------------------------------------- Austin ---
'texas:austin': dict(
  scene='hill-city', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'including what changes when you have just moved to Texas.',
  chips=['Austin, TX', 'Multiple carriers', 'New to Texas?', 'Fast quotes'],
  zips=[('78701', 'Downtown'), ('78702', 'East Austin'), ('78703', 'Tarrytown'),
        ('78704', 'South Austin'), ('78705', 'campus area'), ('78717', 'Northwest'),
        ('78723', 'Northeast'), ('78727', 'North'), ('78731', 'Northwest Hills'),
        ('78741', 'Southeast'), ('78745', 'South'), ('78748', 'Far South'),
        ('78749', 'Southwest'), ('78751', 'Hyde Park'), ('78753', 'North'),
        ('78758', 'North'), ('78759', 'Northwest')],
  areas=[
    ('Downtown and Rainey', 'Dense and mostly structured parking. Short trips, and a lot of '
     'households here own fewer vehicles than the metro average.'),
    ('East Austin', 'Just across I-35 from downtown, on an older street grid with driveway and '
     'street parking.'),
    ('South Austin', 'South of the river along Lamar and Congress. Long north-south runs whenever '
     'I-35 or MoPac is the only way through.'),
    ('Central and Hyde Park', 'Around campus and north of it. Short distances, heavy stop-start '
     'traffic, and a high share of student drivers.'),
    ('Northwest Hills and the 360 corridor', 'Into the hills west of MoPac, where the routes in '
     'and out are fewer than the map suggests.'),
    ('North and the Domain', 'Up past 183 toward the tech corridor, and where a lot of the '
     'metro&rsquo;s newer arrivals have landed.'),
  ],
  factors=[
    ('road', 'I-35 straight through the middle',
     'Austin has one interstate through the center and MoPac beside it, which is why so much of '
     'the metro&rsquo;s driving is north-south on two roads. Annual mileage is something carriers '
     'ask about, and a commute that looks short on a map is not always short in practice.'),
    ('home', 'If you have just moved here',
     'Changing your garaging address is not paperwork you can leave for later &mdash; the policy is '
     'rated on where the vehicle actually parks overnight. Moving from out of state also means your '
     'prior insurance history has to be carried across, and carriers differ in how they treat it.'),
    ('user', 'A lot of first policies',
     'Between the university and the number of people arriving from elsewhere, Austin has more '
     'first-time and newly-transferred policies than most. Both are cases where the spread between '
     'carriers is unusually wide.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'newdriver', 'noprior', 'switch', 'sr22'],
  faq=[('I just moved to Texas. What do I need to do about my car insurance?',
     '<p>Two things. Your policy has to be rated on your new Texas garaging address, and Texas has '
     'its own minimum liability limits &mdash; 30/60/25 &mdash; which may not match what you carried '
     'before. Keeping the out-of-state policy indefinitely is not an option.</p>'
     '<p>The useful part is that moving is a natural moment to re-shop rather than transfer. Your '
     'prior insurance history counts in your favour with most carriers, so bring the details of the '
     'old policy and we will put it to several companies at once.</p>')],
  links=[('../../../quote.html', 'Get a car insurance quote'), ('../', 'Car insurance in Texas'),
         ('../san-antonio/', 'Car insurance in San Antonio'), ('../../makes/', 'Insurance by make')],
),

# ------------------------------------------------------------ San Antonio ---
'texas:san-antonio': dict(
  scene='metro-skyline', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent, in '
        'English or Spanish.',
  chips=['San Antonio, TX', 'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],
  zips=[('78201', 'near West Side'), ('78205', 'Downtown'), ('78209', 'Alamo Heights'),
        ('78210', 'Southeast'), ('78212', 'Monte Vista'), ('78216', 'North Central'),
        ('78228', 'West Side'), ('78229', 'Medical Center'), ('78230', 'Northwest'),
        ('78232', 'North Central'), ('78240', 'Northwest'), ('78245', 'Far West'),
        ('78247', 'Northeast'), ('78249', 'Northwest'), ('78250', 'Northwest'),
        ('78254', 'Far Northwest'), ('78258', 'Far North')],
  areas=[
    ('Downtown and Southtown', 'Tight historic streets, mostly lot and street parking, and short '
     'trips rather than freeway runs.'),
    ('Alamo Heights and Monte Vista', 'Inside Loop 410 north of downtown, older housing with '
     'driveways and garages.'),
    ('The Medical Center and Northwest', 'One of the city&rsquo;s biggest employment clusters, and '
     'the reason a lot of commutes converge on the same stretch of Loop 410.'),
    ('North Central and Stone Oak', 'Up US 281 past 1604. Long daily distances into town.'),
    ('West Side', 'West of downtown, on an older grid with shorter local trips and heavier '
     'stop-start driving.'),
    ('Far West and 1604', 'Newer development out beyond the outer loop, where commutes are long '
     'and the routes in are few.'),
  ],
  factors=[
    ('road', 'Two interstates and two loops',
     'I-35 and I-10 cross here, wrapped by Loop 410 and Loop 1604, and most of the city&rsquo;s '
     'driving happens on one of the four. How far you actually drive in a year is something a '
     'carrier asks about, and the outer-loop suburbs push that figure up quickly.'),
    ('lang', 'English or Spanish',
     'Our agents work in both languages, on the phone or by text. Coverage terms are where the '
     'confusion usually is, and comprehensive versus collision is worth understanding in whichever '
     'language you think in.'),
    ('home', 'Where the vehicle is kept',
     'Rated on the overnight address rather than the one on your license &mdash; and inside Loop '
     '410 versus outside 1604 are genuinely different situations for parking.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver'],
  faq=[],
  links=[('../../../quote.html', 'Get a car insurance quote'), ('../', 'Car insurance in Texas'),
         ('../austin/', 'Car insurance in Austin'), ('../../makes/', 'Insurance by make')],
),

# ------------------------------------------------------------- Fort Worth ---
'texas:fort-worth': dict(
  scene='metro-skyline', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'hail, commuting and work-truck questions included.',
  chips=['Fort Worth, TX', 'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],
  zips=[('76102', 'Downtown'), ('76104', 'Near Southside'), ('76107', 'Cultural District'),
        ('76109', 'TCU area'), ('76110', 'South'), ('76112', 'East'), ('76116', 'West'),
        ('76119', 'Southeast'), ('76123', 'Southwest'), ('76131', 'North'),
        ('76132', 'Southwest'), ('76133', 'South'), ('76137', 'North'), ('76179', 'Far North'),
        ('76244', 'Keller area')],
  areas=[
    ('Downtown and Near Southside', 'Compact, with lot and street parking and short local trips.'),
    ('Cultural District and West 7th', 'West of downtown, denser than most of the city, with a mix '
     'of garage and street parking.'),
    ('TCU and the south', 'Around the university and south along Hulen. A higher share of student '
     'drivers than elsewhere in the city.'),
    ('North Fort Worth and Alliance', 'Up I-35W past the loop. Long commutes, and a lot of '
     'work-related vehicle use around the Alliance corridor.'),
    ('East Fort Worth', 'Toward Arlington along I-30, which is also the road most Dallas commutes '
     'from here run on.'),
    ('Southwest and Chisholm Trail', 'Out along the tollway, newer development and long daily '
     'distances.'),
  ],
  factors=[
    ('sun', 'Hail, and what actually covers it',
     'Hail damage to a vehicle is a <strong>comprehensive</strong> claim &mdash; optional coverage, '
     'subject to your deductible and to the terms of your policy. Neither liability nor collision '
     'answers it. On a paid-off vehicle it is the first coverage people drop and the one they most '
     'often wish they had kept.'),
    ('road', 'I-35W, I-30 and the loop',
     'Fort Worth sits at the west end of the Metroplex, so a good share of commutes run east on '
     'I-30 toward Dallas or north on 35W toward Alliance. Those are real annual miles, and mileage '
     'is one of the things a carrier asks about.'),
    ('truck', 'Work trucks',
     'A pickup that carries tools or materials for pay, tows for money, or is titled to a company '
     'is not doing what a personal auto policy assumes. Saying so up front is the difference '
     'between a paid claim and a denied one.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'commercial', 'sr22', 'noprior', 'switch'],
  faq=[],
  links=[('../../../quote.html', 'Get a car insurance quote'), ('../', 'Car insurance in Texas'),
         ('../dallas/', 'Car insurance in Dallas'), ('../../ram/', 'Ram truck insurance')],
),

# ------------------------------------------------------------ Albuquerque ---
'new-mexico:albuquerque': dict(
  scene='high-desert', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent, '
        'licensed in New Mexico and next door in Texas.',
  chips=['Albuquerque, NM', 'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],
  zips=[('87102', 'Downtown'), ('87104', 'Old Town'), ('87105', 'South Valley'),
        ('87106', 'University'), ('87107', 'North Valley'), ('87108', 'Southeast'),
        ('87109', 'Journal Center'), ('87110', 'Uptown'), ('87111', 'Northeast Heights'),
        ('87112', 'East'), ('87113', 'North'), ('87114', 'West Side'),
        ('87120', 'West Side'), ('87121', 'Southwest'), ('87122', 'Far Northeast'),
        ('87123', 'Southeast Heights')],
  areas=[
    ('Downtown and Old Town', 'Compact and older, with street and lot parking rather than '
     'driveways on many blocks.'),
    ('Northeast Heights', 'Up against the Sandias east of I-25. Most trips into town run west or '
     'south from here.'),
    ('Uptown', 'Around the malls at Louisiana and I-40, one of the busier surface-street areas in '
     'the city.'),
    ('West Side', 'Across the river beyond Coors. Everything eastbound funnels over a handful of '
     'bridges, which is what makes the commute what it is.'),
    ('North Valley', 'Along the river north of I-40, semi-rural in places with longer driveways '
     'and more covered parking.'),
    ('South Valley and southwest', 'South of the interstate along Isleta and Bridge, with shorter '
     'local trips and an older street pattern.'),
  ],
  factors=[
    ('road', 'The Big I, and the river crossings',
     'I-25 and I-40 cross in the middle of the city, and the West Side reaches the rest of '
     'Albuquerque over a small number of bridges. That shapes both how far people drive and when '
     'they are on the road &mdash; and mileage is something carriers ask about.'),
    ('sun', 'Hail and sun are comprehensive questions',
     'Hail damage, a cracked windshield and theft all fall under <strong>comprehensive</strong> '
     'coverage rather than collision. It is optional, applies subject to your deductible, and is '
     'governed by the terms of the policy you hold.'),
    ('home', 'Garaging address, not mailing address',
     'Rated on where the vehicle actually parks overnight. In a city split by a river and an '
     'escarpment that is a real distinction rather than a formality.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver'],
  faq=[('What is the minimum car insurance required in New Mexico?',
     '<p>New Mexico requires liability limits of <strong>25/50/10</strong> &mdash; $25,000 for '
     'injury to one person, $50,000 for everyone injured in one accident, and $10,000 for property '
     'damage.</p>'
     '<p>The property damage figure is the one worth looking at twice. $10,000 is well below what a '
     'good many vehicles on the road are worth, and anything above that limit is yours to cover. A '
     'New Mexico insurer also has to offer you uninsured motorist coverage, which you can decline '
     'only in writing.</p>')],
  links=[('../../../quote.html', 'Get a car insurance quote'),
         ('../', 'Car insurance in New Mexico'), ('../rio-rancho/', 'Car insurance in Rio Rancho'),
         ('../../makes/', 'Insurance by make')],
),

# ------------------------------------------------------------- Las Cruces ---
'new-mexico:las-cruces': dict(
  scene='desert-mountains', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'in English or Spanish, from just down the road in El Paso.',
  chips=['Las Cruces, NM', 'Multiple carriers', 'English &amp; Spanish', 'Border region'],
  zips=[('88001', 'central'), ('88003', 'NMSU campus'), ('88005', 'west and Picacho'),
        ('88007', 'northwest'), ('88011', 'East Mesa'), ('88012', 'north and Sonoma Ranch')],
  areas=[
    ('Downtown and Mesquite', 'The older center of the city, with a compact street grid and '
     'shorter local trips.'),
    ('NMSU and University area', 'Around the campus south of University Avenue. A high share of '
     'student drivers and first policies.'),
    ('East Mesa', 'Up the slope east of I-25, newer subdivisions, and where most of the city&rsquo;s '
     'growth has gone.'),
    ('West side and Picacho', 'Toward the river and the West Mesa, with the highway crossings doing '
     'most of the work.'),
    ('North and Doña Ana', 'Along the valley north of town, semi-rural and further from everything '
     'than the map suggests.'),
  ],
  factors=[
    ('road', 'Where I-10 and I-25 meet',
     'Las Cruces sits on the junction of two interstates, with US 70 running east over the pass '
     'toward Alamogordo. A lot of local driving here is highway driving, and annual mileage is one '
     'of the things a carrier asks about.'),
    ('border', 'El Paso, Santa Teresa and the border',
     'Plenty of Las Cruces households drive into Texas regularly, and some cross into Mexico. A '
     'U.S. policy generally does not satisfy what Mexico requires of a driver &mdash; that normally '
     'means a separate Mexican policy for the days you are there.'),
    ('user', 'A university town',
     'Students away at school without the vehicle are often rated differently from students who '
     'take it with them, and a good-student discount is real at many carriers. Neither happens '
     'automatically.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'newdriver', 'mexico', 'noprior', 'switch', 'sr22'],
  faq=[],
  links=[('../../../quote.html', 'Get a car insurance quote'),
         ('../', 'Car insurance in New Mexico'),
         ('../../texas/el-paso/', 'Car insurance in El Paso'), ('../../makes/', 'Insurance by make')],
),

# --------------------------------------------------------------- Santa Fe ---
'new-mexico:santa-fe': dict(
  scene='high-desert', presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent, '
        'licensed across New Mexico.',
  chips=['Santa Fe, NM', 'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],
  zips=[('87501', 'central and Eastside'), ('87505', 'south and Airport Road'),
        ('87506', 'north and Tesuque'), ('87507', 'southwest'), ('87508', 'Eldorado and south')],
  areas=[
    ('The Plaza and downtown', 'Narrow historic streets, limited and often paid parking, and a '
     'great deal of visitor traffic on top of local trips.'),
    ('Eastside and Canyon Road', 'Older, tighter and steeper than the rest of town, with little '
     'off-street parking on many properties.'),
    ('Southside and Airport Road', 'Where most of the everyday shopping and commuting happens, and '
     'where most of the city&rsquo;s newer housing is.'),
    ('North and Tesuque', 'Up toward the ski basin and the pueblos, with longer distances and '
     'steeper grades between places.'),
    ('Eldorado and the south', 'Out along US 285, a genuine commute into town rather than a '
     'crosstown trip.'),
  ],
  factors=[
    ('road', 'A city that is not built on a grid',
     'Santa Fe&rsquo;s older streets are narrow, steep in places and busy with visitors, while most '
     'of the practical driving happens south of it along Cerrillos and Airport Road. Low-speed '
     'scrapes in tight parking are exactly what collision coverage and a deductible decision are '
     'about.'),
    ('mountain', 'Elevation, winter and distance',
     'At seven thousand feet, winter here means real snow and ice, and the next town is a long way '
     'off in most directions. Roadside assistance and rental reimbursement are worth pricing '
     'when a tow and a repair take longer to arrange.'),
    ('home', 'Where the vehicle sits overnight',
     'Rated on the garaging address. Between an Eastside property with no driveway and a Southside '
     'house with a garage, that is a genuinely different answer.'),
  ],
  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch'],
  faq=[],
  links=[('../../../quote.html', 'Get a car insurance quote'),
         ('../', 'Car insurance in New Mexico'), ('../albuquerque/', 'Car insurance in Albuquerque'),
         ('../../makes/', 'Insurance by make')],
),

# ---------------------------------------------------------------- Houston ---
'texas:houston': dict(
  scene='metro-skyline',
  presence='serving',
  blurb='Compare options from several insurance companies with a licensed Safe House agent &mdash; '
        'including the comprehensive coverage questions that come up on the Gulf Coast.',
  chips=['Houston, TX', 'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],

  zips=[('77002', 'Downtown'), ('77004', 'Third Ward'), ('77005', 'West University'),
        ('77007', 'The Heights'), ('77008', 'The Heights'), ('77019', 'River Oaks'),
        ('77024', 'Memorial'), ('77027', 'Uptown'), ('77030', 'Medical Center'),
        ('77036', 'Sharpstown'), ('77042', 'Westchase'), ('77055', 'Spring Branch'),
        ('77056', 'Galleria'), ('77070', 'Willowbrook'), ('77077', 'Energy Corridor'),
        ('77084', 'West Houston'), ('77095', 'Copperfield'), ('77598', 'Clear Lake')],

  areas=[
    ('Inside the Loop',
     'Downtown, Midtown, Montrose and the Heights. Short trips, dense streets, street parking '
     'rather than a garage on a lot of blocks.'),
    ('The Medical Center and Museum District',
     'One of the largest employment centres in the country, which means a great many Houston '
     'commutes end in the same few square miles.'),
    ('Uptown and the Galleria',
     'Dense office and retail inside the 610 loop&rsquo;s west side, and some of the heaviest '
     'surface-street traffic in the city.'),
    ('Energy Corridor and West Houston',
     'Out along I-10 west toward Katy. Long commutes in, and the part of town where the reservoir '
     'flooding of recent years is best remembered.'),
    ('Spring Branch and Memorial',
     'Between I-10 and 290 inside Beltway 8, older housing stock with a mix of garaged and '
     'driveway parking.'),
    ('North and Northwest',
     'Willowbrook, Copperfield, Cypress and up toward Spring. Beltway 8 and 249 do most of the '
     'work getting people in and out.'),
    ('Southeast and Clear Lake',
     'Down I-45 toward NASA and the bay. Long runs on the Gulf Freeway, and closer to the coast '
     'than most of the metro.'),
    ('East End and Pasadena side',
     'Along the Ship Channel, with a heavier mix of work vehicles and commercial traffic than the '
     'rest of the city.'),
  ],

  factors=[
    ('road', 'Freeway miles add up faster here than people think',
     'I-45, I-10, US 59 and two ring roads &mdash; the 610 loop and Beltway 8 &mdash; carry most of '
     'the metro, and a commute from Katy or Cypress into the Medical Center is a serious daily '
     'distance. Annual mileage is something a carrier asks about, and Houston drivers underestimate '
     'it more than most.'),
    ('sun', 'Flood and water damage is a comprehensive question',
     'This is the one worth being precise about. A standard auto policy does not automatically '
     'cover flood damage to a vehicle &mdash; that generally falls under <strong>comprehensive</strong> '
     'coverage, which is optional, subject to your deductible, and subject to the terms of the '
     'policy you actually hold. Liability alone will not do it, and neither will collision. If your '
     'vehicle is paid off and you dropped comprehensive to save money, that is the coverage you no '
     'longer have.'),
    ('shield', 'Comprehensive covers more than weather',
     'The same coverage answers hail, a tree limb, theft, a break-in and a cracked windshield. It '
     'is usually the cheaper half of physical damage cover and it is the half people drop first, '
     'which tends to be backwards.'),
    ('home', 'Where the vehicle actually sits',
     'A garage, a driveway, a carport, an apartment lot or the street &mdash; carriers ask, and in '
     'a metro this size the answer varies enormously between two households a mile apart. It is '
     'rated on the overnight address, not the one on your license.'),
    ('truck', 'Work vehicles around the Ship Channel',
     'Houston has an unusual amount of vehicles doing something commercial &mdash; contractors, '
     'delivery, anything moving materials for pay. A personal auto policy can deny a claim that '
     'happened while working, so it is worth saying out loud what the vehicle does.'),
    ('lang', 'English or Spanish',
     'Our agents work in both, by phone or text. Coverage terms are where the confusion usually '
     'is, and comprehensive versus collision is exactly the sort of thing worth going through in '
     'whichever language you think in.'),
  ],

  intents=['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch', 'newdriver', 'commercial'],

  faq=[
    ('Does car insurance cover flood damage in Houston?',
     '<p>Not automatically, and not under liability or collision. Flood and water damage to a '
     'vehicle generally falls under <strong>comprehensive</strong> coverage, which is optional on '
     'a policy, applies subject to your deductible, and is governed by the terms and exclusions of '
     'the policy you actually hold.</p>'
     '<p>The practical version: if you carry liability only, a flooded vehicle is your loss. If you '
     'carry comprehensive, it is a claim. It is worth checking which of those describes your policy '
     'before hurricane season rather than during it &mdash; we can look at your current declarations '
     'page with you.</p>'),
    ('Is comprehensive coverage worth it in Houston?',
     '<p>It is the coverage that answers hail, flooding, theft, break-ins and a rock through the '
     'windshield, and it is usually the cheaper half of physical damage cover. Whether it is worth '
     'carrying comes down to what the vehicle is worth and whether you could replace it out of '
     'pocket &mdash; not to any claim we could make about the weather.</p>'
     '<p>If the vehicle is financed or leased, the question is settled for you: the lender will '
     'require it.</p>'),
    ('I commute from Katy into town. Does that change my quote?',
     '<p>Annual mileage is one of the things carriers rate on, so a long daily commute is relevant '
     '&mdash; and so is the address the vehicle is parked at overnight, which for a lot of Houston '
     'households is nowhere near where they work.</p>'
     '<p>Estimate the mileage honestly rather than optimistically. Guessing low is not a saving; it '
     'is a mismatch between the policy and the way the vehicle is actually used.</p>'),
  ],

  links=[('../../../quote.html', 'Get a car insurance quote'),
         ('../', 'Car insurance in Texas'),
         ('../../makes/', 'Car insurance by vehicle make'),
         ('../../ford/', 'Ford insurance'),
         ('../../toyota/', 'Toyota insurance'),
         ('../../ram/', 'Ram truck insurance')],
),

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
     'license. In a city this spread out that is a real distinction &mdash; people move across '
     'town and forget to tell anyone, and a claim is the wrong moment to find out the policy has '
     'the old address.'),
    ('lang', 'English or Spanish, whichever is easier',
     'Insurance is a bad thing to half-understand. Our agents work in both languages, in person on '
     'Montana Ave, on the phone, or by text &mdash; and the policy documents themselves can be '
     'gone through line by line either way.'),
    ('sun', 'Sun, hail and the odd flash flood',
     'Comprehensive is the part of the policy that covers hail, flooding, theft and a cracked '
     'windshield &mdash; not collision, and not liability. It is subject to your deductible and to '
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


# ---------------------------------------------------------------------------
# Cities without a hand-written entry above still get the new page. What they
# do NOT get is invented local color: their content is derived from things
# already established and checkable — the corridor fact in cities.ROADS, the
# city's tags, and its county. Sections with no data (ZIP selector, area
# explorer) are simply not rendered, which is the honest outcome for a town
# where we could not name the neighbourhoods without guessing.

SCENE_BY_TAG = [
  ('coastal', 'coastal'), ('oil', 'oilfield'), ('mountain', 'mountain-town'),
  ('rgv', 'valley'), ('border', 'desert-mountains'), ('plains', 'plains'),
  ('dfw', 'metro-skyline'), ('houston-metro', 'metro-skyline'), ('metro', 'metro-skyline'),
]

# New Mexico reads as high desert rather than Gulf-coast metro, so a few tags
# resolve differently there.
SCENE_NM = {'metro': 'high-desert', 'plains': 'plains', 'border': 'desert-mountains',
            'mountain': 'mountain-town', 'oil': 'oilfield'}

def scene_for(state, tags):
    if state == 'new-mexico':
        for t in ('mountain', 'oil', 'border', 'metro', 'plains'):
            if t in tags:
                return SCENE_NM[t]
        return 'high-desert'
    for tag, sc in SCENE_BY_TAG:
        if tag in tags:
            return sc
    return 'plains'

# Tag-driven factor cards. Each is true of that kind of place and useful on an
# insurance page; none of them is a statistic we cannot source.
TAG_FACTORS = {
 'border': ('border', 'Crossing into Mexico',
   'A U.S. auto policy generally does not satisfy what Mexico requires of a driver, and physical '
   'damage cover usually stops at the border. Crossing normally means a separate Mexican policy '
   'for the days you are there &mdash; worth arranging before the trip rather than at the bridge.'),
 'rgv': ('border', 'Valley driving and the bridges',
   'Short trips, heavy local traffic and international bridges within reach. If your car crosses, '
   'a U.S. policy is generally not what Mexico asks for, and a separate Mexican policy is the '
   'usual answer.'),
 'oil': ('truck', 'Work trucks and field miles',
   'A pickup that carries tools or materials for pay, tows for money, or is titled to a company is '
   'not doing what a personal auto policy assumes. Field mileage is also far higher than an '
   'ordinary commute, and mileage is something carriers ask about.'),
 'coastal': ('sun', 'Wind, hail and water are comprehensive questions',
   'A standard auto policy does not automatically cover flood or storm damage to a vehicle. That '
   'generally falls under <strong>comprehensive</strong> coverage, which is optional, applies '
   'subject to your deductible, and is governed by the terms of the policy you hold.'),
 'plains': ('sun', 'Hail is the claim that catches people out',
   'Hail damage is comprehensive, not collision and not liability &mdash; and comprehensive is the '
   'coverage most often dropped by owners of paid-off vehicles. It is usually the cheaper half of '
   'physical damage cover.'),
 'mountain': ('road', 'Grades, weather and longer distances between towns',
   'Roadside assistance and rental reimbursement are worth pricing where the next town is a long '
   'way off, because a tow and a repair take longer to arrange than they do in a city.'),
 'university': ('user', 'Students on the policy',
   'A student living away at school without the vehicle is often rated differently from one who '
   'takes it with them, and a good-student discount is real at many carriers. Neither is applied '
   'automatically &mdash; both have to be asked for.'),
 'military': ('shield', 'Deployments, moves and storage',
   'Frequent moves change the garaging address, and a vehicle in storage is a different '
   'conversation from one in daily use. Some carriers handle both far better than others.'),
 'spanish': ('lang', 'English or Spanish, whichever is easier',
   'Our agents work in both, on the phone or by text. Coverage terms are where the confusion '
   'usually sits, and they are worth going through in whichever language you think in.'),
 'metro': ('road', 'City miles and where the car sits at night',
   'Stop-start traffic, more vehicles per mile, and an overnight parking situation that varies '
   'street by street. Carriers rate on the garaging address rather than the one on your license.'),
 'dfw': ('road', 'Metroplex distances and toll roads',
   'Commutes across the Metroplex are long, and mileage is one of the things a carrier asks about. '
   'Toll usage does not affect a quote, but the distance behind it does.'),
 'houston-metro': ('road', 'Freeway commuting and comprehensive cover',
   'Long freeway runs, and a Gulf Coast weather picture where flood and hail damage to a vehicle '
   'fall under comprehensive coverage &mdash; optional, subject to your deductible, and to the '
   'terms of the policy you hold.'),
}

# Intent cards by tag, on top of the ones every city gets.
TAG_INTENTS = {'border': 'mexico', 'rgv': 'mexico', 'oil': 'commercial',
               'university': 'newdriver', 'military': 'switch'}
BASE_INTENTS = ['cheaper', 'renewal', 'bought', 'sr22', 'noprior', 'switch']

def derive(state, slug, name, county, tags, road):
    """A place entry for a city with no hand-written one."""
    factors = []
    if road:
        # The one genuinely per-city fact we already hold and have checked.
        factors.append(('road', 'Getting around ' + name,
          'Local traffic here runs on ' + road + '. Where and how far you drive is one of the '
          'things an insurance company asks about, and it is the part people most often estimate '
          'from memory rather than from the odometer.'))
    for t in tags:
        if t in TAG_FACTORS and TAG_FACTORS[t] not in factors:
            factors.append(TAG_FACTORS[t])
    factors.append(('home', 'Where the vehicle is kept',
      'Carriers rate on the address the vehicle parks at overnight, not the one printed on your '
      'license. If you have moved within ' + county + ' County and not told anyone, that is worth '
      'sorting out before a claim rather than during one.'))

    intents = list(BASE_INTENTS)
    for t in tags:
        extra = TAG_INTENTS.get(t)
        if extra and extra not in intents:
            intents.append(extra)

    return dict(scene=scene_for(state, tags), presence='serving',
                blurb='Compare options from several insurance companies with help from a licensed '
                      'Safe House agent &mdash; in English or Spanish.',
                chips=[name + ', ' + ('TX' if state == 'texas' else 'NM'),
                       'Multiple carriers', 'English &amp; Spanish', 'Fast quotes'],
                factors=factors[:5], intents=intents[:8],
                links=[('../../../quote.html', 'Get a car insurance quote'),
                       ('../', 'Car insurance in ' + ('Texas' if state == 'texas' else 'New Mexico')),
                       ('../../makes/', 'Car insurance by vehicle make')])
