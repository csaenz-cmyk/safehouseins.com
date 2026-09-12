#!/usr/bin/env python3
"""The content of the Car Insurance 101 guides. Rendering lives in genguides.py.

RULES THIS FILE FOLLOWS, AND WHY

No prices. Not one guide names a dollar figure for a premium, a saving or an
average. We have no source for any of them: rates are set by carrier, by state,
by ZIP and by applicant, and a number written here in 2026 is wrong by 2027 on
a page that is asking to be trusted about money. Where the reference site
writes "drivers typically pay $X", these guides explain what moves the number
instead. That is the more useful answer anyway.

No rankings. There is no "best companies" or "cheapest companies" guide. Both
require data we do not have, and an agency that is appointed with some carriers
and not others cannot write an impartial league table of them. Pretending
otherwise is the kind of thing that reads well and cannot be defended.

Statutory limits ARE named, because they are law rather than opinion — but see
VERIFY below.

VERIFY BEFORE LAUNCH: the Texas and New Mexico minimum limits in the last two
guides. They have been stable for years and they are correct as far as we know,
but they are the one class of fact on these pages a visitor could act on
directly. Confirm against tdi.texas.gov and osi.state.nm.us, then tick the row
in docs/CLAIMS_CONTACTS_VERIFY.md.
"""

# TWO COLLECTIONS
#
#   group '101'         the explainers. Somebody weeks from buying anything,
#                       researching how the product works.
#   group 'situations'  the pages for a specific circumstance — no licence, a
#                       DWI, a lapse, driving into Mexico. Same shape, very
#                       different reader: these people have the problem today.
#
# A body part may also be ('es', 'una linea en espanol'). The site is in
# English until the language toggle is built, and these are the exception: on
# the pages where the reader is most likely to be searching in Spanish, one
# sentence in Spanish, marked lang="es", saying we speak it. One per page, no
# more.
#
# Each guide: slug, nav (short label for the grid), title, desc, h1, lede,
# body (heading, [paragraph or ('ul', [items])]), key (the takeaways box),
# faq [(q, a)]. 'featured' marks the one that gets the big card.
GUIDES = [

{
 'group': '101', 'slug': 'compare-car-insurance-quotes', 'featured': True,
 'nav': 'How to Compare Quotes',
 'card': 'What actually makes two quotes comparable, and the four places a '
         'cheaper one is usually cheaper.',
 'title': 'How to Compare Car Insurance Quotes',
 'desc': 'How to compare car insurance quotes properly: matching coverage line '
         'for line, the four places a cheap quote is usually cheap, and what to '
         'check before you switch.',
 'h1': 'How to compare car insurance quotes',
 'lede': 'Two quotes are only comparable when they are quoting the same policy. '
         'Most of the time they are not, and the gap is where the price '
         'difference actually came from.',
 'body': [
  ('Start with your declarations page, not with a website',
   ['Your declarations page — the dec page — is the one- or two-page summary '
    'the carrier sends when a policy starts or renews. It lists every coverage, '
    'every limit, every deductible and every vehicle. It is the only document '
    'that says what you actually have.',
    'Quote against it. Type the same limits into the new quote that appear on '
    'the old one, line by line. Almost every "we beat your price by a lot" '
    'story turns out, on inspection, to be a comparison between a policy and a '
    'smaller policy.',
    'If you do not have your dec page, the carrier will email it in minutes, '
    'and so will we if the policy is with us.']),
  ('The four places a cheap quote is usually cheap',
   ['When one quote comes in well under another and both are from real '
    'carriers, the difference is nearly always in one of four places.',
    ('ul', ['<b>Liability limits.</b> A quote at the state minimum against a '
            'quote at 100/300 is not the same product. The minimum is a floor '
            'set by a legislature, not a recommendation.',
            '<b>Deductibles.</b> Collision and comprehensive each carry their '
            'own. Moving from $500 to $1,000 lowers the premium and moves that '
            'money to the day you have a claim.',
            '<b>Uninsured motorist.</b> Cheap to add, expensive to be without, '
            'and the first line a bargain quote drops.',
            '<b>What is missing entirely.</b> Rental reimbursement, roadside, '
            'medical payments or PIP, and glass coverage are priced per vehicle '
            'and are easy to leave off a quote without mentioning it.']),
   ]),
  ('Check the term before you compare the number',
   ['Car policies are written for six months or twelve. A six-month premium '
    'sitting next to a twelve-month premium looks like a saving of half. It is '
    'not a saving of anything.',
    'Divide both by the number of months they buy and compare that. If a quote '
    'does not say which term it is, that is the first question.']),
  ('Down payment is not price',
   ['"Nothing down" and "low first payment" are financing terms, not the cost '
    'of the policy. A smaller first payment usually means bigger instalments '
    'afterwards, sometimes with a service fee on each one.',
    'Ask for two numbers every time: what the policy costs in total, and what '
    'is due today. They answer different questions and only the first one '
    'compares.']),
  ('The questions a quote form does not ask',
   ['A rating engine prices what you typed. It does not ask how long you were '
    'really insured before this, whose policy that was, whether there was a gap '
    'and why. It does not ask whether the student on the policy has a B average '
    'or lives away at school. It does not ask what your occupation is, whether '
    'you own the home you live in, or whether you finished a defensive driving '
    'course two years ago.',
    'Every one of those changes the price at some carriers and not at others. '
    'It is the single largest reason two people with the same car and the same '
    'record get different numbers.']),
  ('Before you switch',
   [('ul', ['Never cancel the old policy before the new one is active. A gap of '
            'even one day is a lapse, and a lapse raises what you pay at the '
            'next carrier — sometimes by more than you just saved.',
            'Ask what happens at renewal. A price that exists only for the '
            'first term is a common way to win a quote.',
            'Check the carrier is one you can reach. Look at how a claim is '
            'reported and whether there is a person on the other end.',
            'Ask what the new carrier did with your prior-coverage history. If '
            'nobody asked about it, it was not credited.'])]),
 ],
 'key': ['Quote against the declarations page, line for line.',
         'Match the term — six months against six months.',
         'Separate what the policy costs from what is due today.',
         'Never let the old policy lapse before the new one starts.'],
 'faq': [
  ('How many quotes should I get?',
   'More than one and fewer than ten. What matters is not the count but whether '
   'the carriers quoted are ones that want your particular situation — an agent '
   'shopping five appointed carriers who write your profile beats fifteen '
   'websites that do not.'),
  ('Does getting quotes hurt my credit?',
   'No. Carriers use a soft inquiry for insurance scoring and it does not '
   'affect your credit score. It is not the same as applying for a loan.'),
  ('Can I switch in the middle of a policy term?',
   'Yes, any time. The old carrier refunds the unused portion, usually pro '
   'rata. Make the new policy active first.'),
 ],
},

{
 'group': '101', 'slug': 'how-car-insurance-is-calculated',
 'nav': 'How Your Rate Is Calculated',
 'card': 'What a rating engine is actually weighing, and which of those things '
         'you can still do something about.',
 'title': 'How Car Insurance Rates Are Calculated',
 'desc': 'What actually goes into a car insurance rate: the driver, the '
         'vehicle, the coverage, the location and the history — and which parts '
         'you can change.',
 'h1': 'How your car insurance rate is calculated',
 'lede': 'Nobody prices your policy by hand. A rating engine multiplies a base '
         'rate by a long series of factors, and knowing which factors move the '
         'most is most of what there is to know.',
 'body': [
  ('The four groups of factors',
   ['Every carrier weighs these differently — that is exactly why the same '
    'driver gets different numbers from different companies — but they all '
    'weigh roughly the same things.',
    ('ul', ['<b>The driver.</b> Age, years licensed, marital status, and in '
            'most states an insurance score. Tickets, at-fault accidents and '
            'claims, over a look-back period that is not the same at every '
            'carrier.',
            '<b>The vehicle.</b> Year, make, model and trim. What it costs to '
            'repair, how often that model is stolen, how well it protects the '
            'people inside it, and what its safety equipment is.',
            '<b>The coverage.</b> Your liability limits, your deductibles, and '
            'every optional line you keep or drop.',
            '<b>Where it lives.</b> Garaging ZIP code, not where you work. '
            'Claim frequency, theft, weather and repair costs in that ZIP.'])]),
  ('The one most people underrate: continuous coverage',
   ['How long you have been continuously insured, and at what limits, is one of '
    'the largest single credits on a car policy. A driver coming off a lapse '
    'pays noticeably more than the same driver with three unbroken years — same '
    'car, same record.',
    'It is also the factor most often mishandled, because the online form asks '
    'one blunt question about it and moves on. Whose policy it was, the exact '
    'dates, and the reason for any gap all matter, and at some carriers a gap '
    'under thirty days is treated very differently from a gap over it.']),
  ('What you can change, roughly in order of effect',
   [('ul', ['Your limits and deductibles. The most direct lever, and the one '
            'with a real trade-off attached.',
            'Which carrier you are with. The same profile is priced very '
            'differently across companies, and the spread is usually wider '
            'than anything else on this list.',
            'Discounts you qualify for and have not claimed.',
            'How you pay — paid in full and automatic payments are credits at '
            'most carriers.',
            'Which vehicle you buy next. Two cars in the same price bracket can '
            'be a long way apart on insurance.']),
    'What you cannot change quickly: your record, your address, and how long '
    'you have been insured. Those improve with time, which is why a policy is '
    'worth re-shopping every year rather than once.']),
  ('Why a ticket costs more than the ticket',
   ['A moving violation stays in the rating for years, not months — commonly '
    'three, sometimes five. The surcharge is applied at every renewal in that '
    'window, so the real cost of a ticket is the fine plus several years of a '
    'higher premium.',
    'It is also a place where carriers differ sharply. One company surcharges a '
    'first minor violation heavily; another barely notices it. Which is which '
    'is not published, and it is most of what an agent who places this business '
    'every day actually knows.']),
  ('Insurance scores, briefly',
   ['Most states allow carriers to use a credit-based insurance score as one '
    'rating factor. It is not your credit score and it is not used the same '
    'way, but it is built from the same file, and it does move premiums.',
    'Neither Texas nor New Mexico prohibits it. If your credit has improved '
    'since the policy was written, that is a real reason to re-shop.']),
 ],
 'key': ['Carriers weigh the same factors differently — that is the spread.',
         'Continuous coverage is one of the biggest credits, and the most often missed.',
         'A ticket costs the fine plus several years of surcharge.',
         'Re-shop every year: your record and your history keep improving.'],
 'faq': [
  ('Why did my rate go up when nothing changed?',
   'Usually the carrier took a rate increase across the whole book in your '
   'state, which has nothing to do with you. That is the single best moment to '
   're-shop, because the increase was not applied to every company at once.'),
  ('Does my job really affect my rate?',
   'At some carriers, yes, and at others not at all. Where it does, it is '
   'usually an occupational discount rather than a penalty. It is worth stating '
   'accurately.'),
  ('Is my rate based on where I park or where I work?',
   'Where the car is garaged overnight. Commuting distance is asked separately '
   'and matters much less.'),
 ],
},

{
 'group': '101', 'slug': 'how-much-car-insurance-you-need',
 'nav': 'How Much Coverage You Need',
 'card': 'Why the state minimum is a floor rather than a recommendation, and '
         'how to pick limits you can defend.',
 'title': 'How Much Car Insurance Do You Need?',
 'desc': 'How to choose car insurance limits and deductibles: what the state '
         'minimum actually covers, what happens when it runs out, and how to '
         'size coverage to what you have.',
 'h1': 'How much car insurance do you actually need?',
 'lede': 'The legal minimum is the least you may carry, not the amount that '
         'covers a bad day. The difference between the two is usually small on '
         'the premium and very large on the claim.',
 'body': [
  ('What liability limits mean',
   ['Liability is written as three numbers — 30/60/25, for example. The first '
    'is the most the policy pays for injuries to any one person. The second is '
    'the most for all injuries in one accident. The third is the most for the '
    'other party’s property.',
    'Those are ceilings. When the bill goes past the ceiling, the rest is '
    'yours: your savings, your wages, whatever a court decides you can pay.',
    'One hospital stay and one late-model vehicle will reach a state minimum '
    'without anything unusual happening. That is the scenario to price, not the '
    'fender bender.']),
  ('A workable way to pick a number',
   ['Carry enough liability to cover what you could lose. For most households '
    'the honest answer is somewhere above the minimum and below what a lawyer '
    'would recommend if fear were free.',
    ('ul', ['If you rent and have little saved, the minimum is a real choice, '
            'but understand what it is.',
            'If you own a home, have equity, or have wages worth garnishing, '
            'higher limits are the cheapest protection of those you will buy.',
            'If you are already at 100/300, ask what 250/500 costs. The step is '
            'usually far smaller than the first step off the minimum.'])]),
  ('Uninsured motorist is the one to think hardest about',
   ['Liability protects other people from you. Uninsured and underinsured '
    'motorist coverage protects you from the driver who has nothing — or who '
    'has the minimum and hit you with a bill that is a multiple of it.',
    'Texas and New Mexico both require carriers to offer it, and both require '
    'your rejection of it to be in writing. That requirement exists because the '
    'legislature knows what happens without it.',
    'A sensible default is to carry it at the same limits as your liability.']),
  ('Deductibles: what you are buying is timing',
   ['A deductible is not a fee. It is the amount of each claim you have agreed '
    'to pay, and raising it is a way of buying a lower premium with money you '
    'will owe later if something happens.',
    'The test is simple. Pick the highest deductible you could write a check '
    'for tomorrow without it being a crisis. Below that number you are '
    'over-insuring; above it you are not really covered.']),
  ('When to drop collision and comprehensive',
   ['On an older car there is a point where the premium for physical damage '
    'approaches what the carrier would ever pay out, because it will only ever '
    'pay the car’s actual cash value minus the deductible.',
    'It is not a rule about age or mileage — it is arithmetic about that '
    'specific car. Ask what the two coverages cost on their own and compare it '
    'to what the car is worth. If the car is financed or leased, the lender '
    'decides this, not you.']),
  ('The lines people skip and then miss',
   [('ul', ['<b>Rental reimbursement.</b> Priced per vehicle and usually small. '
            'The question is how you get to work for two weeks.',
            '<b>Roadside assistance.</b> Often cheaper than a standalone '
            'membership, and already attached to the policy.',
            '<b>Medical payments or PIP.</b> Pays for you and your passengers '
            'regardless of fault, with no deductible. In Texas, PIP must be '
            'offered and rejected in writing.',
            '<b>Gap coverage.</b> If the car is financed and worth less than '
            'the loan, this is the difference. New cars, long loans and small '
            'down payments are where it matters.'])]),
 ],
 'key': ['The state minimum is a floor set by a legislature, not advice.',
         'Carry liability against what you could lose, not against the car.',
         'Match uninsured-motorist limits to your liability limits.',
         'Set the deductible at the largest check you could write tomorrow.'],
 'faq': [
  ('Is full coverage a real thing?',
   'Not as a defined product. "Full coverage" is shorthand for liability plus '
   'collision plus comprehensive, which is what a lender requires. It does not '
   'mean everything is covered, and two full-coverage policies can be very '
   'different.'),
  ('Does my policy cover someone else driving my car?',
   'Usually yes — car insurance follows the car first. But a household member '
   'who drives regularly and is not listed is a problem, and an excluded driver '
   'is never covered.'),
  ('Do I need coverage for a car I am not driving?',
   'If it is registered and it exists, yes, and comprehensive-only storage '
   'coverage is often available for a car genuinely off the road. Cancelling '
   'outright creates a lapse, which costs more later than the storage coverage '
   'would have.'),
 ],
},

{
 'group': '101', 'slug': 'car-insurance-discounts',
 'nav': 'Car Insurance Discounts',
 'card': 'The sixteen we ask about on every quote, why an online form only '
         'finds some of them, and when to ask again.',
 'title': 'Car Insurance Discounts: The Full List',
 'desc': 'The car insurance discounts worth asking about, why an online quote '
         'form only finds some of them, and when to ask for them again.',
 'h1': 'Car insurance discounts, and why you have to ask',
 'lede': 'Discounts are not applied because you deserve them. They are applied '
         'because somebody asked the right question, and a quote form only asks '
         'a handful of them.',
 'body': [
  ('Credits tied to your history',
   [('ul', ['<b>Prior insurance.</b> Continuous coverage before this policy, '
            'and at what limits. One of the largest credits there is.',
            '<b>Safe driver.</b> A clean record over the carrier’s '
            'look-back period, which is not the same at every carrier.',
            '<b>Defensive driving.</b> A state-approved course. Worth asking '
            'about at renewal, not only when the policy is written.',
            '<b>Early shopping.</b> Quoting before the current policy expires '
            'rather than on the day it does.'])]),
  ('Credits tied to your household',
   [('ul', ['<b>Multi-policy.</b> A home, renters or mobile-home policy with '
            'the same company as the car.',
            '<b>Multi-car.</b> More than one vehicle on the policy.',
            '<b>Homeowner.</b> Owning the home you live in — and at several '
            'carriers this applies even when the home policy is elsewhere.',
            '<b>Good student.</b> A B average or better for a student on the '
            'policy.',
            '<b>Student away at school.</b> A student living far enough away '
            'that they are not driving the car.'])]),
  ('Credits tied to the car',
   [('ul', ['<b>Anti-theft.</b> Factory or aftermarket alarm, immobilizer or '
            'tracker.',
            '<b>Safety features.</b> Anti-lock brakes, airbags, backup camera, '
            'lane assist and the rest of what the car already has.',
            '<b>Usage-based.</b> Letting the carrier see how the car is '
            'actually driven, by app or plug-in device. Not right for everyone, '
            'and a good agent will say so.'])]),
  ('Credits tied to how you pay and who you are',
   [('ul', ['<b>Paid in full.</b> Paying the term up front rather than in '
            'instalments.',
            '<b>Automatic payments.</b> Letting the carrier draft the premium.',
            '<b>Paperless.</b> Documents and bills by email.',
            '<b>Occupation and affinity.</b> Teachers, nurses, military, first '
            'responders, and a long list of employers, unions and alumni '
            'associations.'])]),
  ('Why the online form only finds some of them',
   ['Every carrier has a different list, a different name for the same credit, '
    'and different rules about who qualifies. A quote form has to be short '
    'enough that people finish it, so it asks about the four or five discounts '
    'that apply to the most people and stops.',
    'Nothing is being hidden. The questions simply are not on the form, and a '
    'discount nobody asked about is not applied.']),
  ('Ask again at renewal',
   ['Discounts are not permanent and your situation changes. A student reached '
    'a B average. You bought a house. You finished a defensive driving course. '
    'You moved and the car is now garaged somewhere cheaper.',
    'None of that reaches the carrier on its own. Renewal is the moment to run '
    'through the list again, and it is the moment most people do not.']),
 ],
 'key': ['A discount nobody asked about is not applied.',
         'Every carrier’s list is different — the spread is real.',
         'Homeowner credits often apply without bundling.',
         'Run the list again at every renewal, not just at the start.'],
 'faq': [
  ('Do discounts stack?',
   'Generally yes, though most carriers cap the total and some credits are '
   'mutually exclusive. The order they are applied in is the carrier’s, '
   'not yours.'),
  ('Is the usage-based app worth it?',
   'For a driver with a short, daytime, gentle commute it can be one of the '
   'largest credits available. For somebody who drives late, brakes hard or '
   'covers long distances it can raise the price at renewal. Ask before you '
   'enrol whether the programme can increase your rate.'),
  ('Can you apply a discount after the policy started?',
   'Usually yes, and often back to the start of the term. It is worth a phone '
   'call the moment anything changes.'),
 ],
},

{
 'group': '101', 'slug': 'how-to-save-on-car-insurance',
 'nav': 'How to Save on Car Insurance',
 'card': 'The levers that actually move the number, in order, and the two that '
         'look like savings and are not.',
 'title': 'How to Save on Car Insurance',
 'desc': 'Practical ways to lower a car insurance premium without quietly '
         'buying less coverage — and the two moves that look like savings and '
         'are not.',
 'h1': 'How to save on car insurance',
 'lede': 'There are real ways to pay less, and there are ways to pay less that '
         'are really just carrying less. Worth knowing which is which before '
         'you do either.',
 'body': [
  ('Re-shop once a year, on purpose',
   ['This is the biggest lever and the one almost nobody pulls. Carriers take '
    'rate increases at different times, tighten and loosen their appetite for '
    'different drivers, and enter and leave states. The company that was best '
    'for you two years ago often is not now.',
    'Your side changes too: a violation aged off, a student reached a B '
    'average, your credit improved, you bought a house. None of that reaches '
    'your carrier by itself.']),
  ('Fix your deductibles deliberately',
   ['Raising collision and comprehensive deductibles lowers the premium '
    'immediately. It is a genuine choice, not a trick — you are agreeing to pay '
    'more of a claim in exchange for paying less every month.',
    'Do it with a number you could actually produce tomorrow, and do it knowing '
    'that the saving is real every month and the cost is real on the day.']),
  ('Pay in a way that costs less',
   ['Paid in full is a credit at most carriers, and it also avoids the '
    'instalment fee that quietly rides on every monthly payment. Automatic '
    'payments and paperless are usually credits on top of that.',
    'If paying in full is not possible, ask what the instalment fee is per '
    'payment and what the total is over the term. It is often the difference '
    'between two quotes.']),
  ('Ask what the car is doing to the price',
   ['Two vehicles that cost the same to buy can be a long way apart to insure. '
    'Repair cost, theft rate, and how the model performs in crash data all feed '
    'the rating.',
    'Worth asking before you sign for the next car, not after. It is a '
    'five-minute question and it can change the answer.']),
  ('The two that look like savings and are not',
   [('ul', ['<b>Dropping uninsured motorist.</b> It is cheap, and it is the '
            'only coverage that pays when the person who hit you has nothing. '
            'Both states require your refusal in writing for a reason.',
            '<b>Dropping to the state minimum without doing the arithmetic.</b> '
            'If your liability limit is smaller than what you own, the saving '
            'is a loan against a bad day.'])]),
  ('And one that is neither',
   ['A lapse in coverage. Cancelling for a few weeks to save a payment raises '
    'what you pay at the next carrier for years, and in both states it can put '
    'your registration at risk. It is the most expensive way to save money on '
    'car insurance that exists.']),
 ],
 'key': ['Re-shopping every year moves the number more than anything else.',
         'Paid in full avoids both a lost credit and the instalment fee.',
         'Ask what a car costs to insure before you buy it.',
         'A lapse is the most expensive saving there is.'],
 'faq': [
  ('Will switching carriers every year hurt me?',
   'No. There is no penalty for changing companies. What hurts is a gap between '
   'them, and there is no reason to have one.'),
  ('Does paying monthly really cost more?',
   'Almost always, in two ways: the paid-in-full credit you did not get, and a '
   'per-instalment fee. Over a year the two together are usually more than '
   'people expect.'),
  ('Is a cheaper carrier worse at claims?',
   'Not necessarily, and the correlation is weaker than people assume. What '
   'matters more is whether the policy was written correctly in the first '
   'place, which is the part a person checks.'),
 ],
},

{
 'group': '101', 'slug': 'types-of-car-insurance',
 'nav': 'The 6 Main Types of Coverage',
 'card': 'The six coverages a car policy is built from, what each one pays for, '
         'and which are required.',
 'title': 'The 6 Main Types of Car Insurance',
 'desc': 'The six coverages a car insurance policy is built from — liability, '
         'collision, comprehensive, uninsured motorist, medical payments and '
         'PIP — and what each one actually pays for.',
 'h1': 'The six coverages a car policy is built from',
 'lede': 'A car insurance policy is not one thing. It is a stack of separate '
         'coverages, each with its own limit, its own deductible and its own '
         'reason to exist.',
 'body': [
  ('1. Liability',
   ['Pays other people when a crash is your fault — their injuries under bodily '
    'injury liability, their property under property damage liability. Required '
    'in both Texas and New Mexico.',
    'It pays nothing towards your own car and nothing towards your own '
    'injuries. That is what the rest of the stack is for.']),
  ('2. Collision',
   ['Pays to repair or replace your car when it hits something, or something '
    'hits it — another vehicle, a pole, a curb, the ground. Fault does not '
    'matter; the deductible applies either way.',
    'Optional by law, required by every lender and lessor.']),
  ('3. Comprehensive',
   ['Pays for damage that is not a collision: hail, theft, fire, flood, '
    'vandalism, a cracked windshield, an animal in the road. Its own deductible, '
    'separate from collision.',
    'In hail country this is the coverage that earns its premium.']),
  ('4. Uninsured and underinsured motorist',
   ['Pays when the at-fault driver has no insurance, or not enough of it. Both '
    'states require carriers to offer it and require your rejection in writing.',
    'It is the coverage that fills the hole the other driver left, which is why '
    'dropping it to save a little is the trade most likely to be regretted.']),
  ('5. Medical payments (MedPay)',
   ['Pays medical bills for you and your passengers after an accident, whoever '
    'caused it, with no deductible. It sits in front of your health insurance '
    'and covers the deductibles and copays that follow a crash.']),
  ('6. Personal injury protection (PIP)',
   ['Broader than MedPay: medical bills plus a share of lost wages and the cost '
    'of services you can no longer perform. In Texas it must be offered and '
    'rejected in writing.',
    'A vehicle carries MedPay or PIP, not both.']),
  ('The add-ons that are not coverages exactly',
   [('ul', ['<b>Rental reimbursement.</b> A car to drive while yours is being '
            'repaired after a covered claim.',
            '<b>Roadside assistance.</b> Tow, jump, lockout, flat, fuel.',
            '<b>Gap.</b> The difference between what the car is worth and what '
            'is still owed on it.',
            '<b>SR-22.</b> Not coverage at all — a form the carrier files with '
            'the state to prove the policy exists.'])]),
 ],
 'key': ['Liability pays other people; collision and comprehensive pay for your car.',
         'Collision and comprehensive carry separate deductibles.',
         'Uninsured motorist is the one that fills the other driver’s hole.',
         'A vehicle carries MedPay or PIP, never both.'],
 'faq': [
  ('Which of these are required?',
   'Liability in both states. Everything else is optional by law, though a '
   'lender will require collision and comprehensive while there is a loan.'),
  ('Do I pay two deductibles if both apply?',
   'Only one per claim — whichever coverage is paying. A hail claim is '
   'comprehensive; hitting a pole is collision.'),
  ('Is glass separate?',
   'Usually it falls under comprehensive, sometimes with its own lower '
   'deductible or none at all. It varies by carrier and it is worth asking.'),
 ],
},

{
 'group': '101', 'slug': 'liability-car-insurance',
 'nav': 'Liability Coverage',
 'card': 'The coverage the law requires, what the three numbers mean, and what '
         'happens when they run out.',
 'title': 'Liability Car Insurance Explained',
 'desc': 'What liability car insurance covers, what the three numbers in '
         '30/60/25 mean, and what happens when a claim is larger than your '
         'limit.',
 'h1': 'Liability car insurance',
 'lede': 'The part of the policy the law actually requires, and the part that '
         'stops a bad afternoon from becoming a lien on everything you own.',
 'body': [
  ('What it pays for',
   ['Liability pays other people when an accident is your fault. It splits into '
    'two coverages that are usually quoted together.',
    ('ul', ['<b>Bodily injury liability.</b> Their medical bills, their lost '
            'wages, and what a court awards for pain and suffering.',
            '<b>Property damage liability.</b> Their vehicle, and anything else '
            'you hit — a fence, a storefront, a light pole.']),
    'It also pays for your legal defence if you are sued over a covered '
    'accident, and that cost does not come out of your limit.']),
  ('What the three numbers mean',
   ['Written as 30/60/25, the numbers are in thousands.',
    ('ul', ['<b>30</b> — the most paid for injuries to any one person.',
            '<b>60</b> — the most paid for all injuries in one accident.',
            '<b>25</b> — the most paid for the other party’s property.']),
    'Some policies are written with a single combined limit instead, which is '
    'one pot for the whole accident rather than three ceilings.']),
  ('What happens past the limit',
   ['The carrier pays up to the number and stops. Everything above it is yours '
    'personally — savings, wages, and in some circumstances a lien against '
    'property.',
    'This is the scenario worth pricing. One serious injury and one late-model '
    'vehicle reaches a state-minimum limit without anything unusual happening '
    'at all.']),
  ('What it does not pay for',
   [('ul', ['Your own car — that is collision.',
            'Your own injuries — that is MedPay, PIP or health insurance.',
            'Damage when the other driver is at fault — that is their liability, '
            'or your uninsured-motorist coverage if they have none.',
            'Anything that happens on purpose.'])]),
  ('Where to set it',
   ['Higher liability limits are among the cheapest coverage you will buy, '
    'because the large claims they protect against are rare. The first step up '
    'from the state minimum usually costs far less than people expect, and the '
    'step after that less again.',
    'A useful test: if a claim were twice your current limit, what would the '
    'rest of it come out of?']),
 ],
 'key': ['Liability pays other people, never you and never your car.',
         'The three numbers are per person, per accident, and for property.',
         'Legal defence is paid on top of the limit, not out of it.',
         'Raising limits is unusually cheap per dollar of protection.'],
 'faq': [
  ('Does liability follow me into a rental car?',
   'Usually yes in the United States, at your own limits. Physical damage to '
   'the rental is a separate question and depends on whether you carry '
   'collision.'),
  ('Am I covered if I lend my car to a friend?',
   'Generally yes — the coverage follows the car first. A household member who '
   'drives regularly should be listed, and an excluded driver is never covered.'),
  ('What is an umbrella policy?',
   'A separate policy that sits above your auto and home liability and pays '
   'after those limits are exhausted. It is usually inexpensive for the amount '
   'of protection, and it requires certain underlying limits.'),
 ],
},

{
 'group': '101', 'slug': 'collision-and-comprehensive',
 'nav': 'Collision & Comprehensive',
 'card': 'The two coverages that pay for your own car, how the deductibles '
         'work, and when they stop being worth it.',
 'title': 'Collision and Comprehensive Coverage Explained',
 'desc': 'The difference between collision and comprehensive car insurance, how '
         'each deductible works, and when it makes sense to drop them on an '
         'older car.',
 'h1': 'Collision and comprehensive',
 'lede': 'Liability pays other people. These two are the ones that pay for your '
         'car — and they are two coverages, not one, with a deductible each.',
 'body': [
  ('Collision',
   ['Pays to repair or replace your car when it collides with something: '
    'another vehicle, a pole, a curb, a wall, or the road itself in a rollover.',
    'It pays whether or not the accident was your fault. If the other driver is '
    'at fault and insured, their liability normally pays instead — but '
    'collision is what gets your car fixed now rather than after the fault '
    'argument is finished. Your deductible is usually refunded if the carrier '
    'recovers from the other side.']),
  ('Comprehensive',
   ['Pays for almost everything that is not a collision — often called '
    '"other than collision" on the policy for exactly that reason.',
    ('ul', ['Hail, wind and flood',
            'Theft of the car, and damage from a break-in',
            'Fire and explosion',
            'Vandalism',
            'A falling tree or falling debris',
            'Hitting an animal — which is comprehensive, not collision',
            'Glass, including a cracked windshield'])]),
  ('How the deductibles work',
   ['Each coverage has its own deductible, and you choose both. One claim, one '
    'deductible — the one belonging to whichever coverage is paying.',
    'Raising a deductible lowers the premium immediately. The right number is '
    'the largest amount you could produce tomorrow without it being a crisis; '
    'below that you are over-insuring, above it you are not really covered.']),
  ('What they actually pay',
   ['Both pay the actual cash value of the car at the moment of loss, minus the '
    'deductible — what it was worth that morning, not what you paid for it and '
    'not what it costs to replace it new.',
    'On a financed car that number can be less than the loan balance, and the '
    'difference is yours unless you carry gap coverage.']),
  ('When to drop them',
   ['There is a point on an older car where the annual premium for both '
    'coverages approaches what the carrier would ever pay out, because the pay '
    'out is capped at the car’s value minus the deductible.',
    'It is arithmetic about that specific car, not a rule about age or mileage. '
    'Ask what the two cost separately and compare. And if the car is financed '
    'or leased, the decision is not yours to make — the lender requires them.']),
 ],
 'key': ['Two separate coverages, two separate deductibles.',
         'Hitting an animal is comprehensive; hitting a pole is collision.',
         'Both pay actual cash value minus the deductible, never replacement cost.',
         'A lender requires both for as long as there is a loan.'],
 'faq': [
  ('Is a cracked windshield collision or comprehensive?',
   'Comprehensive, and many carriers waive or reduce the deductible for glass '
   'repair rather than replacement. Worth asking before you pay out of pocket.'),
  ('If the other driver was at fault, do I still pay my deductible?',
   'Often yes up front, and it is usually refunded once the carrier recovers '
   'from the other side. Going through your own collision coverage is generally '
   'the faster route.'),
  ('What is a total loss?',
   'When the repair cost plus salvage exceeds the car’s value, or crosses '
   'whatever percentage of it the state sets. The carrier then pays the actual '
   'cash value rather than repairing it.'),
 ],
},

{
 'group': '101', 'slug': 'uninsured-motorist-coverage',
 'nav': 'Uninsured Motorist',
 'card': 'The coverage that pays when the driver who hit you cannot — and why '
         'both states make you refuse it in writing.',
 'title': 'Uninsured and Underinsured Motorist Coverage',
 'desc': 'What uninsured and underinsured motorist coverage pays for, why Texas '
         'and New Mexico require it to be offered, and how to set the limits.',
 'h1': 'Uninsured and underinsured motorist',
 'lede': 'Every other coverage assumes somebody has insurance. This is the one '
         'that works when nobody does.',
 'body': [
  ('The two halves',
   [('ul', ['<b>Uninsured motorist (UM).</b> The at-fault driver has no '
            'insurance at all — or cannot be identified, which is what covers a '
            'hit-and-run at most carriers.',
            '<b>Underinsured motorist (UIM).</b> The at-fault driver has '
            'insurance, but their limit does not cover the bill. Yours pays the '
            'gap up to your own limit.']),
    'They are usually quoted together and often written as one line on the '
    'policy.']),
  ('Why both states make you refuse it in writing',
   ['Texas and New Mexico both require carriers to offer uninsured-motorist '
    'coverage, and both require your rejection of it to be documented in '
    'writing. A legislature does not add a paperwork requirement to a coverage '
    'nobody needs.',
    'If you do not remember rejecting it, check your declarations page. It is '
    'one of the most commonly dropped lines on a quote shopped purely on '
    'price.']),
  ('Property damage as well as injury',
   ['UM is usually split the same way liability is — bodily injury and property '
    'damage — and the property side is what repairs your car when an uninsured '
    'driver hits it and disappears.',
    'In some cases UM property damage carries its own small deductible. That is '
    'still better than the alternative, which is your collision deductible or '
    'nothing at all.']),
  ('Where to set the limit',
   ['A sensible default is to match your liability limits. You are insuring '
    'against the same size of accident either way; the only difference is which '
    'side had the insurance.',
    'You cannot normally carry more UM than you carry liability, which is '
    'another reason the liability number matters more than it looks.']),
  ('Why it matters more here than in a lot of places',
   ['Both Texas and New Mexico sit well above the national average for the '
    'share of drivers on the road with no insurance at all. That is the whole '
    'argument for this coverage, and it is the reason an agent here will push '
    'back when somebody wants to drop it.']),
 ],
 'key': ['UM covers a driver with nothing; UIM covers one with not enough.',
         'Both states require the offer and a written rejection.',
         'The property-damage half repairs your car after a hit-and-run.',
         'Match the limits to your liability limits.'],
 'faq': [
  ('Does it cover a hit-and-run?',
   'At most carriers yes, under the uninsured half, though some require a '
   'police report or physical contact between the vehicles. It is worth knowing '
   'your carrier’s rule before you need it.'),
  ('Will using it raise my rate?',
   'A not-at-fault claim is treated very differently from an at-fault one, and '
   'at many carriers it is not surchargeable at all. It is not a reason to skip '
   'a legitimate claim.'),
  ('Is it the same as PIP or MedPay?',
   'No. MedPay and PIP pay regardless of fault and regardless of who was '
   'insured. UM only responds when somebody else was at fault and had no '
   'adequate coverage.'),
 ],
},

{
 'group': '101', 'slug': 'medpay-and-pip',
 'nav': 'MedPay & PIP',
 'card': 'The two coverages that pay your own medical bills regardless of '
         'fault, and how they differ.',
 'title': 'MedPay and PIP Coverage Explained',
 'desc': 'The difference between medical payments coverage and personal injury '
         'protection, what each pays for, and why Texas requires PIP to be '
         'rejected in writing.',
 'h1': 'Medical payments and personal injury protection',
 'lede': 'Both pay for injuries to you and your passengers whoever caused the '
         'accident, with no deductible and no argument about fault first. PIP '
         'goes further.',
 'body': [
  ('Medical payments (MedPay)',
   ['Pays medical and, at most carriers, funeral expenses for you and anyone '
    'riding with you, regardless of who caused the accident. No deductible, no '
    'waiting for a fault determination.',
    'It sits in front of your health insurance and is commonly used for exactly '
    'the costs health insurance leaves behind — the deductible, the copays, the '
    'ambulance bill.']),
  ('Personal injury protection (PIP)',
   ['Everything MedPay does, plus two things it does not.',
    ('ul', ['<b>Lost wages.</b> A share of the income you lose while you are '
            'unable to work.',
            '<b>Essential services.</b> The cost of paying somebody to do what '
            'you can no longer do — childcare, housekeeping and similar.']),
    'In Texas, PIP must be offered on every policy and your rejection of it '
    'must be in writing. The minimum offer is a modest amount and higher limits '
    'are usually available and usually cheap.']),
  ('You carry one or the other',
   ['A vehicle carries MedPay or PIP, not both. Which is available depends on '
    'the state and the carrier.',
    'PIP is broader, and where both are offered it is usually the better buy '
    'for a small difference in premium — the wage replacement alone tends to '
    'justify it.']),
  ('Why it is worth having even with good health insurance',
   ['A health plan has a deductible and copays, and a car accident can hit them '
    'all at once. MedPay and PIP cover exactly that, immediately, without a '
    'liability claim being settled first.',
    'They also cover your passengers, who may not have health coverage at all '
    'and whose bills would otherwise land back on you.']),
  ('They do not reduce anything else',
   ['Using MedPay or PIP does not come out of a liability settlement and does '
    'not reduce what you can recover from the at-fault driver. It is a separate '
    'coverage you paid for.']),
 ],
 'key': ['Both pay regardless of fault, with no deductible.',
         'PIP adds lost wages and essential services; MedPay does not.',
         'A vehicle carries one or the other, never both.',
         'In Texas, rejecting PIP has to be in writing.'],
 'faq': [
  ('Does it cover my passengers?',
   'Yes — anyone in the vehicle, and in many cases you as a pedestrian or in '
   'someone else’s car. The exact reach varies by carrier.'),
  ('How much should I carry?',
   'The step up from the minimum offer is usually small. Given that it pays '
   'first, with no deductible, and covers everyone in the car, it is rarely the '
   'place to economise.'),
  ('Is PIP available in New Mexico?',
   'MedPay is the common form in New Mexico; PIP is the required-offer coverage '
   'in Texas. Your agent will tell you which applies to your policy.'),
 ],
},

{
 'group': '101', 'slug': 'roadside-and-rental',
 'nav': 'Roadside & Rental',
 'card': 'The two small add-ons people skip and then need, and what they '
         'actually include.',
 'title': 'Roadside Assistance and Rental Reimbursement',
 'desc': 'What roadside assistance and rental reimbursement cover on a car '
         'insurance policy, how they are priced, and when they are worth '
         'carrying.',
 'h1': 'Roadside assistance and rental reimbursement',
 'lede': 'Neither one protects you from a catastrophe. Both are the difference '
         'between an inconvenient week and a genuinely bad one.',
 'body': [
  ('Roadside assistance',
   ['Usually covers the short list of things that strand a car.',
    ('ul', ['Towing, up to a set distance or a set amount',
            'Jump start',
            'Flat tire change',
            'Lockout service',
            'Fuel delivery when you run out',
            'Winching, at some carriers']),
    'It is priced per vehicle and it is normally small. It is often cheaper '
    'than a standalone motoring membership and it is already attached to a '
    'policy you have.']),
  ('Rental reimbursement',
   ['Pays for a rental car while yours is being repaired after a covered claim. '
    'It is written as a daily amount with a maximum number of days.',
    'The two numbers matter separately. A generous daily allowance with a short '
    'cap runs out during a long repair; a long cap at a small daily allowance '
    'does not cover the class of car you actually need.']),
  ('The part people get wrong',
   ['Rental reimbursement only applies after a <em>covered claim</em>. It is '
    'not a rental car for a breakdown, for maintenance, or for a holiday.',
    'Roadside assistance is the coverage that responds to a breakdown, and it '
    'tows the car — it does not put you in another one.']),
  ('When they are worth carrying',
   [('ul', ['If you have one car and no way to work without it, rental '
            'reimbursement is the small line that matters most on this page.',
            'If you have a second car or somebody to drive you, it matters '
            'much less.',
            'If the car is older, or the commute is long, roadside earns its '
            'keep on the first tow.',
            'If you already pay for a motoring club, compare the two before '
            'carrying both.'])]),
  ('One thing to know before you claim',
   ['Some carriers treat frequent roadside calls as claims activity even though '
    'no damage was paid. It is unusual, it varies by company, and it is worth '
    'asking your agent how yours handles it before you use it for the fourth '
    'time in a year.']),
 ],
 'key': ['Both are priced per vehicle and both are usually small.',
         'Rental reimbursement only applies after a covered claim.',
         'Roadside responds to a breakdown; rental does not.',
         'Check the daily limit and the day cap separately.'],
 'faq': [
  ('Does rental reimbursement pay for any car?',
   'Up to the daily amount on your policy. Anything above that class of vehicle '
   'is yours to cover.'),
  ('Will using roadside raise my rate?',
   'At most carriers no, because nothing was paid for damage. A few treat '
   'repeated use as claims activity — worth asking about yours.'),
  ('Can I add these mid-term?',
   'Usually yes, and they take effect immediately. They cannot be added after '
   'the accident that made you want them.'),
 ],
},

{
 'group': '101', 'slug': 'sr-22-texas-new-mexico',
 'nav': 'SR-22 Filings',
 'card': 'What an SR-22 actually is, how fast one can be filed, and what it '
         'does to the price.',
 'title': 'SR-22 Insurance in Texas and New Mexico',
 'desc': 'What an SR-22 is, when Texas or New Mexico requires one, how quickly '
         'it can be filed, and what it does to your car insurance rate.',
 'h1': 'SR-22 filings, explained',
 'lede': 'An SR-22 is not insurance and it is not a penalty. It is a form the '
         'carrier files with the state to prove a policy exists — and the '
         'reason it matters is what happens if it lapses.',
 'body': [
  ('What it actually is',
   ['A certificate of financial responsibility. Your insurance company files it '
    'with the state on your behalf, confirming you carry at least the minimum '
    'required liability coverage.',
    'You do not buy an SR-22. You buy a policy, and the carrier attaches the '
    'filing to it — usually for a small one-time fee.']),
  ('When one is required',
   [('ul', ['A DWI or DUI conviction',
            'Driving without insurance, or an accident while uninsured',
            'Too many violations in a short period',
            'A license suspension or reinstatement',
            'A court order following a judgement'])],
   ),
  ('How long it lasts',
   ['Commonly two years in Texas and three in New Mexico, counted from the date '
    'the state sets rather than from when you file. The state tells you the '
    'end date; your carrier does not decide it.',
    'The filing has to stay continuously in force for that whole period. There '
    'is no credit for having carried it most of the time.']),
  ('The part that catches people out',
   ['If the policy lapses — cancelled, non-renewed, or a payment missed — the '
    'carrier is required to notify the state, usually with an SR-26 form. The '
    'state then suspends the license again, and the clock on the filing period '
    'frequently restarts.',
    'This is the single most important thing to understand about an SR-22. '
    'Automatic payments exist for exactly this situation and are worth setting '
    'up on day one.']),
  ('What it does to the price',
   ['The filing fee itself is small. The premium is higher because of the event '
    'that caused the requirement, not because of the form.',
    'Carriers differ enormously here. Some will not write the business at all; '
    'others specialise in it and price it sensibly. Which is which is the whole '
    'value of shopping it properly rather than taking the first company that '
    'says yes.']),
  ('If you do not own a car',
   ['A non-owner policy provides liability coverage when you drive a vehicle '
    'you do not own, and it can carry an SR-22 filing. It is how somebody gets '
    'a license reinstated without buying a car first.']),
 ],
 'key': ['An SR-22 is a filing, not a type of insurance.',
         'A lapse triggers an SR-26 and usually restarts the clock.',
         'Set up automatic payments the day the policy starts.',
         'A non-owner policy can carry the filing if you have no car.'],
 'faq': [
  ('How fast can it be filed?',
   'Often the same day. Tell the agent up front that you need one — it changes '
   'which carriers are worth quoting, and getting that right the first time is '
   'the difference between an afternoon and a week.'),
  ('Will every company write an SR-22?',
   'No. Some decline the business outright. We place these regularly and know '
   'which carriers want them.'),
  ('What happens when the period ends?',
   'The requirement simply expires on the date the state set. Tell your agent '
   'when it does — once the filing is no longer required, it is worth '
   're-shopping the policy immediately.'),
 ],
},

{
 'group': '101', 'slug': 'texas-car-insurance-requirements',
 'nav': 'Texas Requirements',
 'card': 'The minimum limits Texas requires, what else has to be offered, and '
         'what happens if you drive without it.',
 'title': 'Texas Car Insurance Requirements',
 'desc': 'The minimum car insurance Texas requires, the coverages carriers must '
         'offer you, and the penalties for driving uninsured.',
 'h1': 'What Texas requires',
 'lede': 'Texas sets a floor, and it is genuinely a floor. Here is what the law '
         'asks for, what the law makes carriers offer you, and what the minimum '
         'does not cover.',
 'body': [
  ('The minimum liability limits',
   ['Texas requires liability coverage of at least <b>30/60/25</b>:',
    ('ul', ['<b>$30,000</b> for injuries to any one person',
            '<b>$60,000</b> for all injuries in one accident',
            '<b>$25,000</b> for the other party’s property']),
    'That is the least you may legally carry. It is not a recommendation and it '
    'was not set with the cost of a modern hospital stay or a late-model truck '
    'in mind.']),
  ('What carriers must offer you',
   [('ul', ['<b>Personal injury protection (PIP).</b> Must be offered on every '
            'policy. Your rejection must be in writing.',
            '<b>Uninsured and underinsured motorist.</b> Must be offered. Your '
            'rejection must be in writing.']),
    'If you do not remember rejecting either, check your declarations page — '
    'they are two of the most commonly dropped lines on a policy shopped purely '
    'on price.']),
  ('How proof of insurance works',
   ['Texas verifies coverage electronically through TexasSure, which checks '
    'registration records against carrier data. A policy that lapses shows up '
    'without anybody pulling you over.',
    'You still need proof in the car. A printed card or the carrier’s app '
    'both count.']),
  ('Driving without it',
   [('ul', ['A fine for a first offence, larger for a second, plus court costs '
            'and a state surcharge',
            'The vehicle can be impounded',
            'Your license and registration can be suspended',
            'An SR-22 filing is frequently required afterwards']),
    'And the part that is not a penalty: an accident while uninsured is paid '
    'out of your own pocket, without a limit.']),
  ('What the minimum leaves you exposed to',
   ['$25,000 of property damage is one late-model vehicle, and not a large one. '
    '$30,000 per person is a short hospital stay.',
    'Past the limit, the rest is personal — savings, wages, and in some '
    'circumstances property. The step up from the minimum is usually far '
    'smaller on the premium than people expect, and it is the single best '
    'value on a car policy.']),
 ],
 'key': ['Texas minimum liability is 30/60/25.',
         'PIP and uninsured motorist must be offered; refusal must be in writing.',
         'Coverage is verified electronically through TexasSure.',
         '$25,000 of property damage is one modern vehicle.'],
 'faq': [
  ('Do I need insurance for a car I am not driving?',
   'If it is registered, yes. Cancelling creates a lapse, which costs more at '
   'the next renewal than comprehensive-only storage coverage would have.'),
  ('Does a Texas policy cover me in New Mexico?',
   'Yes. Liability coverage follows you across state lines and adjusts to meet '
   'the other state’s minimum if it is higher.'),
  ('Is an out-of-state license a problem?',
   'Not by itself. Where the car is garaged matters more than where the license '
   'was issued. Tell the agent the real situation and it gets rated correctly.'),
 ],
},

{
 'group': '101', 'slug': 'new-mexico-car-insurance-requirements',
 'nav': 'New Mexico Requirements',
 'card': 'The minimum limits New Mexico requires, how the state verifies them, '
         'and why the minimum is thin.',
 'title': 'New Mexico Car Insurance Requirements',
 'desc': 'The minimum car insurance New Mexico requires, how the state verifies '
         'coverage, and the penalties for driving uninsured.',
 'h1': 'What New Mexico requires',
 'lede': 'New Mexico’s floor is lower than Texas’s, which makes the '
         'gap between the legal minimum and a sensible policy wider, not '
         'narrower.',
 'body': [
  ('The minimum liability limits',
   ['New Mexico requires liability coverage of at least <b>25/50/10</b>:',
    ('ul', ['<b>$25,000</b> for injuries to any one person',
            '<b>$50,000</b> for all injuries in one accident',
            '<b>$10,000</b> for the other party’s property']),
    'The property damage figure is the one to look at twice. $10,000 does not '
    'replace a current-model vehicle, and the shortfall is personal.']),
  ('Uninsured motorist must be offered',
   ['New Mexico requires carriers to offer uninsured and underinsured motorist '
    'coverage, and requires your rejection of it to be in writing.',
    'It matters more here than in most places. New Mexico consistently runs '
    'among the higher states for the share of drivers on the road with no '
    'coverage at all — the exact situation this line is for.']),
  ('How the state checks',
   ['New Mexico verifies insurance electronically against registration records. '
    'A lapse can trigger a notice and, if it is not resolved, suspension of the '
    'registration.',
    'Proof still has to be in the vehicle. A card or the carrier’s app '
    'both count.']),
  ('Driving without it',
   [('ul', ['Fines and court costs',
            'Registration suspension, and reinstatement fees to undo it',
            'Possible impoundment',
            'An SR-22 filing is commonly required afterwards, usually for three '
            'years'])]),
  ('Quotes for New Mexico take a person',
   ['A rating engine set up for one state does not produce a New Mexico policy '
    'by changing the ZIP code. Limits, required offers and available carriers '
    'are all different.',
    'We are licensed in both states, and New Mexico quotes here are prepared by '
    'an agent rather than by the online rater — so what comes back is a real '
    'New Mexico policy at real New Mexico limits, not a Texas price with a '
    'different address on it.']),
 ],
 'key': ['New Mexico minimum liability is 25/50/10.',
         'Uninsured motorist must be offered; refusal must be in writing.',
         '$10,000 of property damage does not replace a modern vehicle.',
         'New Mexico quotes here are prepared by an agent, not by the rater.'],
 'faq': [
  ('Can I buy a New Mexico policy online here?',
   'You can start it online, and an agent finishes it. That is deliberate — the '
   'online rater is configured for Texas and a New Mexico quote produced by it '
   'would be wrong in ways that are not visible until a claim.'),
  ('Does a New Mexico policy cover me in Texas?',
   'Yes. Liability follows you across state lines and adjusts up to meet the '
   'other state’s minimum where it is higher.'),
  ('I live in one state and work in the other. Which applies?',
   'Where the car is garaged overnight. Tell the agent both facts and it gets '
   'written correctly.'),
 ],
},

]

# --------------------------------------------------------- the situations ---
# Written second and kept in their own list only for readability; they are
# merged into GUIDES below and every consumer sees one list.
SITUATIONS = [

{
 'group': 'situations',
 'slug': 'car-insurance-without-a-license',
 'nav': 'Insurance Without a License',
 'card': ('Foreign licenses, matrículas, a permit, or no license at all — what is actually '
 'possible and what it takes.'),
 'title': 'Car Insurance Without a License in Texas and New Mexico',
 'desc': ('Can you get car insurance without a US driver license? What works with a foreign '
 'license, a matrícula, a permit or an ITIN, and how to get a policy in Texas or New '
 'Mexico.'),
 'h1': 'Car insurance without a US license',
 'lede': ('It is one of the most common questions we get, and the answer people usually expect '
 'is wrong. In a lot of situations it can be done. What it takes is the right carrier '
 'and an agent who has placed it before.'),
 'body': [('First, the short answer',
  ['Yes, often. Not at every company and not in every situation, but "no US license" '
   'is a reason to be shopped carefully, not a reason to be told no at the door.',
   'Some carriers will not write it at all. Others do it every day. Which is which is '
   'not published anywhere, and it is most of what an agency that places this business '
   'actually knows.',
   ('es', 'Sí se puede. Llámanos y lo revisamos contigo en español.')]),
 ('What usually works as identification',
  [('ul',
    ['<b>A foreign driver license.</b> Mexican, and many others. Several carriers '
     'accept it directly; some want an international permit alongside it.',
     '<b>A matrícula consular.</b> Widely used in this area and accepted by a number '
     'of the companies we represent.',
     '<b>A passport.</b> On its own or with something else.',
     '<b>An ITIN instead of a Social Security number.</b> Normal, and not an obstacle '
     'at the carriers that write this business.',
     '<b>A learner permit.</b> Usually written with a licensed driver on the policy.']),
   'What matters more than any one document is that the whole picture is presented '
   'accurately the first time. A quote that gets corrected later is a quote that gets '
   'repriced later.']),
 ('When the car is yours but the driving is not',
  ['A common situation: you own the vehicle, you are not the one driving it, and '
   'somebody in the household is. That policy is written with you as the named insured '
   'and the licensed driver listed as the operator.',
   'It is a normal structure and it is not a workaround. What causes problems is '
   'leaving the real driver off, because a driver the carrier never knew about is the '
   'argument you do not want to be having at claim time.']),
 ('Registration, inspection and the state',
  ['Texas and New Mexico both require the vehicle to be insured, and both verify it '
   'electronically against the registration. The requirement attaches to the car, not '
   'to whether you personally hold a state license.',
   'That is exactly why this is worth solving rather than avoiding: an uninsured '
   'registered vehicle is a suspension waiting to happen, and a lapse raises the price '
   'for years afterwards.']),
 ('What it costs, honestly',
  ['More than the same driver with a long US record, and less than most people fear. '
   'The premium is driven by the same things it always is — how long you have been '
   'continuously insured, the vehicle, the ZIP code, the limits — and a foreign '
   'license is one factor among them rather than a penalty on its own.',
   'The largest single thing you can do about it is prove prior coverage. If you '
   'carried insurance in Mexico or anywhere else, say so and bring what you have; at '
   'some carriers it counts.']),
 ('What to bring when you call',
  [('ul',
    ['Whatever identification you have — license, matrícula, passport, permit',
     'The vehicle: year, make, model, and the VIN if you have it',
     'The address where the car is parked overnight',
     'Anything showing insurance you have carried before',
     'The names and dates of birth of anyone who will drive it'])])],
 'key': ['"No US license" is a reason to be shopped carefully, not a refusal.',
 'Foreign licenses, matrículas, passports and ITINs are all workable.',
 'List the real driver — an unknown driver is a claim problem.',
 'Prior coverage counts, even from another country, at some carriers.'],
 'faq': [('Can I insure a car I own if I do not drive?',
  'Yes. You are the named insured and whoever actually drives it is listed as the '
  'operator. It is a standard way to write a policy, not a workaround.'),
 ('Do you need a Social Security number?',
  'Not at every carrier. An ITIN works with several of the companies we represent, and '
  'at some neither is required.'),
 ('Will it be much more expensive?',
  'It is usually higher than a long US record and lower than people expect. What moves '
  'it most is prior continuous coverage, which is worth documenting if you have any.')],
},

{
 'group': 'situations',
 'slug': 'new-driver-car-insurance',
 'nav': 'New and Teen Drivers',
 'card': ('Why the first policy costs what it does, when to add a teen to yours, and the '
 'credits nobody mentions.'),
 'title': 'Car Insurance for New and Teen Drivers',
 'desc': ('What a first car insurance policy costs and why, when to add a teen driver to a '
 'family policy instead of writing their own, and the discounts new drivers qualify '
 'for.'),
 'h1': 'New drivers and teen drivers',
 'lede': ('A first policy is the most expensive one anybody buys, for reasons that have nothing '
 'to do with how carefully you drive. Most of what can be done about it happens in how '
 'the policy is set up.'),
 'body': [('Why the first policy costs what it does',
  ['Two things, and neither is personal.',
   ('ul',
    ['<b>No record to look at.</b> Rating is built on history, and a new driver has '
     'none — not a bad one, none. The carrier prices the uncertainty.',
     '<b>The numbers on young drivers as a group.</b> Crash rates for drivers in their '
     'first years are genuinely higher, and that is what the rate reflects.']),
   'Both of these improve on their own. The first is largely gone after three years of '
   'continuous coverage; the second eases with each birthday and drops noticeably '
   'around 25. That is why a first policy should be re-shopped every single year '
   'rather than left alone.']),
 ('On the family policy, or their own?',
  ['Adding a teen to the household policy is almost always cheaper than a separate '
   'one, sometimes dramatically. The family policy already carries multi-car and '
   'multi-policy credits, and the teen inherits the household’s continuous-coverage '
   'history rather than starting from zero.',
   'A separate policy makes sense when the young driver has moved out for good, owns '
   'the car in their own name, or has a record that is raising everybody else’s price. '
   'An agent will tell you which side of that line you are on — it is a five-minute '
   'question.']),
 ('Which car they drive changes the number',
  ['On a young driver the vehicle matters more than it does on anybody else. Carriers '
   'assign the driver to a car, and a fast or expensive one on a seventeen-year-old is '
   'the single most expensive combination on a household policy.',
   'A sensible, well-rated, unexciting car with good safety equipment is worth real '
   'money here. Ask what a specific car does to the premium before you buy it, not '
   'after.']),
 ('The credits new drivers actually qualify for',
  [('ul',
    ['<b>Good student.</b> A B average or better. One of the largest available to a '
     'young driver and it has to be asked for.',
     '<b>Student away at school.</b> Living far enough from home that they are not '
     'regularly driving the car.',
     '<b>Driver training.</b> A completed course, beyond whatever the state required '
     'for the licence.',
     '<b>Usage-based.</b> A short, daytime, gentle commute can be worth a lot here. '
     'Ask first whether the programme can raise the rate as well as lower it.'])]),
 ('Do not let the first policy lapse',
  ['The most expensive mistake a new driver makes is dropping coverage for a few '
   'months — between semesters, between cars, between jobs. Continuous coverage is one '
   'of the biggest credits there is and the clock starts over when it breaks.',
   'If the car genuinely is not being driven, ask about storage or comprehensive-only '
   'coverage instead of cancelling. It keeps the history intact for a fraction of the '
   'premium.'])],
 'key': ['A first policy prices uncertainty, not you. It improves every year.',
 'Adding a teen to the family policy usually beats a separate one.',
 'The car a young driver is assigned to moves the price a lot.',
 'Never lapse — ask about storage coverage instead of cancelling.'],
 'faq': [('When should I add my teen to the policy?',
  'When they get their permit at most carriers, and certainly the day they are '
  'licensed. A teen driving on your policy who was never added is the gap you find out '
  'about after an accident.'),
 ('Does a good student discount really help?',
  'It is one of the biggest credits available to a young driver at most carriers. It '
  'usually needs a report card or transcript, and it has to be asked for — it is not '
  'applied automatically.'),
 ('Will their rate drop at 25?',
  'Generally yes, and noticeably, but it is gradual rather than a switch. The bigger '
  'step for most drivers is three years of clean continuous coverage.')],
},

{
 'group': 'situations',
 'slug': 'mexico-auto-insurance',
 'nav': 'Driving Into Mexico',
 'card': ('Your US policy does not cover you south of the border. What is actually required and '
 'what happens without it.'),
 'title': 'Driving Into Mexico: What Your US Car Insurance Does Not Cover',
 'desc': ('Why a US car insurance policy does not cover you in Mexico, what Mexican liability '
 'insurance is required, and what happens after an accident without it.'),
 'h1': 'Driving into Mexico',
 'lede': ('This is the one people find out about at the worst possible moment. A US car '
 'insurance policy does not cover you in Mexico, and Mexico does not recognise it.'),
 'body': [('What your US policy does and does not do',
  ['Almost every US auto policy stops at the border. Some extend physical damage a '
   'short distance into Mexico — commonly around 25 miles — and even those do not '
   'extend liability, which is the part that matters.',
   'Check your own declarations page before you assume anything. If it says nothing '
   'about Mexico, it covers nothing in Mexico.',
   ('es',
    'Tu póliza de Estados Unidos no te cubre en México. Pregúntanos antes de '
    'cruzar.')]),
 ('What Mexico actually requires',
  ['Mexican law requires liability insurance issued by a company authorised in Mexico. '
   'A US policy, a US insurance card and a US carrier’s name mean nothing to a Mexican '
   'authority at the roadside.',
   'The required coverage is liability — damage and injury you cause to other people. '
   'Coverage for your own vehicle, legal assistance and medical expenses are usually '
   'available as well, and on a trip of any length they are worth having.']),
 ('What happens after an accident without it',
  ['This is why the coverage exists and why people who have needed it never skip it '
   'again.',
   ('ul',
    ['An accident causing injury is treated as a criminal matter in Mexico until fault '
     'is determined.',
     'Without recognised insurance, the vehicle is commonly impounded.',
     'The driver can be held until financial responsibility is established.',
     'A policy from an authorised Mexican insurer, and the legal assistance that '
     'usually comes with it, is what resolves that quickly.'])]),
 ('The trips people forget',
  [('ul',
    ['A day in Ciudad Ju&aacute;rez. The distance is short; the border is still the '
     'border.',
     'A weekend in Chihuahua or on the coast.',
     'Driving a rental or somebody else’s car across.',
     'A work trip in a company vehicle — commercial use has its own requirements.'])]),
 ('Before you go',
  [('ul',
    ['Buy the Mexican coverage before you cross, not at the bridge.',
     'Carry the policy in the vehicle, printed.',
     'Check that the dates cover the whole trip, including the day you come back.',
     'Make sure the vehicle on the policy is the vehicle you are actually taking.',
     'If the car is financed, check whether the lender requires anything in '
     'writing.'])]),
 ('Ask us before you cross',
  ['We are in El Paso, and this comes up constantly. Call and we will tell you exactly '
   'what your current policy does at the border and what you need for the trip you are '
   'making, in English or Spanish.'])],
 'key': ['A US policy does not cover liability in Mexico. Mexico does not recognise it.',
 'Mexican law requires liability from a company authorised in Mexico.',
 'An injury accident is a criminal matter there until fault is settled.',
 'Buy before you cross, carry it printed, check the dates both ways.'],
 'faq': [('Does my policy cover me just across the bridge?',
  'Some policies extend physical damage a short distance — often around 25 miles — but '
  'not liability, which is the coverage Mexico requires. Read your declarations page, '
  'and call us if it is not clear.'),
 ('What about a rental car?',
  'Most US rental agreements prohibit taking the vehicle into Mexico at all. Check the '
  'agreement before you plan the trip.'),
 ('Is it expensive?',
  'For a short trip it is generally a small amount of money against a very large '
  'exposure. The cost depends on the length of the trip, the vehicle and the limits '
  'you choose.')],
},

{
 'group': 'situations',
 'slug': 'non-owner-car-insurance',
 'nav': 'Non-Owner Policies',
 'card': 'Liability coverage when you drive but do not own a car — and how it carries an SR-22.',
 'title': 'Non-Owner Car Insurance Explained',
 'desc': ('What a non-owner car insurance policy covers, who needs one, and how it can carry an '
 'SR-22 filing without owning a vehicle.'),
 'h1': 'Non-owner car insurance',
 'lede': ('A policy for somebody who drives but does not own a car. It is a real product, it is '
 'usually inexpensive, and it solves two problems most people do not know it solves.'),
 'body': [('What it covers',
  ['Liability — injuries and property damage you cause while driving a vehicle you do '
   'not own and that is not regularly available to you.',
   'It sits behind the vehicle owner’s policy, not in front of it. The owner’s '
   'insurance responds first; yours covers what is left over up to your limit.',
   'What it does not cover is the car itself. There is no collision or comprehensive '
   'on a non-owner policy, because there is no vehicle on it.']),
 ('Who it is actually for',
  [('ul',
    ['<b>Somebody who needs an SR-22 and has no car.</b> The most common reason. A '
     'non-owner policy carries the filing, which is what gets the licence reinstated.',
     '<b>A frequent renter or borrower.</b> Cheaper than buying the counter coverage '
     'every time, and it follows you.',
     '<b>Somebody between cars.</b> It keeps continuous coverage intact so the next '
     'real policy is not priced as though you had a lapse.',
     '<b>A city driver who uses car share.</b> Same logic as the renter.'])]),
 ('The continuous-coverage point is the one people miss',
  ['Prior insurance is one of the largest credits on a car policy. Going six months '
   'with nothing, then buying a car, means the new policy is rated as a lapse — and '
   'that follows you for years.',
   'A non-owner policy in the gap costs a fraction of a real policy and keeps the '
   'history unbroken. On the maths alone it often pays for itself the first time you '
   'buy a car again.']),
 ('What it will not do',
  [('ul',
    ['It will not cover a car registered to you.',
     'It will not cover a car in your household that is regularly available to you — '
     'that car needs to be on a policy of its own.',
     'It will not pay to repair the car you were driving.',
     'It will not satisfy a lender, because there is no physical damage coverage on '
     'it.'])]),
 ('Getting one',
  ['Not every carrier writes them, and the ones that do are not always the ones you '
   'would guess. If you need an SR-22 attached, that narrows the list again.',
   'Tell us up front what it is for — reinstating a licence, covering a gap, or '
   'driving other people’s cars — because the answer changes which carriers are worth '
   'quoting.'])],
 'key': ['Liability only, for a driver with no car of their own.',
 'It is the usual way to carry an SR-22 without owning a vehicle.',
 'It keeps continuous coverage alive between cars — that is worth real money.',
 'It never covers the car you are driving.'],
 'faq': [('Can a non-owner policy carry an SR-22?',
  'Yes, and that is the most common reason people buy one. It is how a licence gets '
  'reinstated when there is no car to insure.'),
 ('Does it cover a rental car?',
  'The liability side generally does. Damage to the rental itself does not, so that '
  'part still has to come from the rental company, a credit card benefit or somewhere '
  'else.'),
 ('I live with someone who has a car. Can I get one?',
  'Usually not for that car — a vehicle regularly available to you in your own '
  'household needs to be on a policy that lists you. Tell the agent the real living '
  'situation and it gets written correctly.')],
},

{
 'group': 'situations',
 'slug': 'car-insurance-after-a-dwi',
 'nav': 'After a DWI',
 'card': ('What actually happens to your policy, how long it follows you, and why the first '
 'company to say yes is rarely the right one.'),
 'title': 'Car Insurance After a DWI in Texas or New Mexico',
 'desc': ('What happens to your car insurance after a DWI, how long it affects your rate, what '
 'an SR-22 requires, and how to get covered again.'),
 'h1': 'Car insurance after a DWI',
 'lede': ('It is survivable and it is temporary, though neither of those is obvious while it is '
 'happening. What matters most is the order you do things in and which carrier you '
 'land with.'),
 'body': [('What happens to the policy you have',
  ['Two things can happen, and which one depends entirely on the carrier.',
   ('ul',
    ['<b>Non-renewal.</b> The policy runs to the end of its term and is not offered '
     'again. The common outcome.',
     '<b>Cancellation mid-term.</b> Less common, and usually only where something on '
     'the application turns out to be wrong.']),
   'Either way you get notice in writing, and that notice is the moment to start '
   'shopping — not the week it expires. Letting it run out creates a lapse on top of '
   'the DWI, which makes everything that follows more expensive.']),
 ('The SR-22',
  ['Most DWI convictions come with an SR-22 requirement: a form your carrier files '
   'with the state proving you carry at least the minimum liability.',
   'Commonly two years in Texas and three in New Mexico, from a date the state sets. '
   'The filing has to stay continuously in force for that entire period — if the '
   'policy lapses the carrier notifies the state, the licence is suspended again, and '
   'the clock frequently restarts.',
   'Set up automatic payments on day one. This is the single most common way people '
   'extend a two-year problem into a four-year one.']),
 ('How long it follows you',
  ['Most carriers look back three to five years for rating, and a DWI is at the far '
   'end of that range. It does not disappear the day the SR-22 requirement ends.',
   'But it fades. Each renewal it counts for less, and the day it ages out of the '
   'look-back period is a step change. Put a note in your calendar for the month it '
   'happens and re-shop the policy — most people do not, and they keep paying for '
   'it.']),
 ('Why the first company to say yes is rarely the right one',
  ['After a DWI a lot of doors close, and the relief of finding one that opens is '
   'real. It is also how people end up paying considerably more than they have to for '
   'years.',
   'Carriers differ enormously on this business. Some decline it outright, some take '
   'it and price it punitively, and some specialise in it and price it sensibly. That '
   'spread is wider here than on almost any other kind of policy, which makes shopping '
   'it properly worth more here than anywhere else.']),
 ('What to do, in order',
  [('ul',
    ['Do not let the current policy lapse. Shop before it ends.',
     'Tell the agent about the DWI up front — it changes which carriers are worth '
     'quoting, and it will be found anyway.',
     'Ask whether an SR-22 is required and get it filed with the new policy.',
     'Put the premium on automatic payment.',
     'Note the date the filing requirement ends, and re-shop that month.',
     'Re-shop again when it ages out of the rating look-back.'])])],
 'key': ['Shop the moment the non-renewal notice arrives, not when it expires.',
 'A lapse during an SR-22 period usually restarts the clock.',
 'Automatic payments are not optional here.',
 'Re-shop when the filing ends, and again when it ages out of rating.'],
 'faq': [('Will I be able to get insurance at all?',
  'Yes. It costs more and the list of companies is shorter, but this is business we '
  'place regularly. Nobody is uninsurable because of one conviction.'),
 ('Should I tell the agent?',
  'Always, and up front. It changes which carriers are worth quoting, and a quote '
  'built on an incomplete record gets repriced the moment the report is pulled.'),
 ('How soon can I get an SR-22 filed?',
  'Often the same day. Say you need one at the start of the conversation.')],
},

{
 'group': 'situations',
 'slug': 'car-insurance-after-a-lapse',
 'nav': 'After a Lapse',
 'card': ('What a gap in coverage actually costs, how long it counts against you, and how to '
 'stop it happening again.'),
 'title': 'Car Insurance After a Lapse in Coverage',
 'desc': ('What a lapse in car insurance costs you, how long carriers hold it against you, what '
 'it does to your registration, and how to get covered again.'),
 'h1': 'Getting insured again after a lapse',
 'lede': ('A gap in coverage is one of the most expensive things on a car policy, and almost '
 'nobody knows that until they are living on the other side of one.'),
 'body': [('Why a gap costs so much',
  ['Continuous prior coverage is one of the largest credits a carrier applies. It is '
   'not a reward for good behaviour — it is a genuinely strong predictor, and carriers '
   'price it accordingly.',
   'Losing it does two things at once: you lose the credit, and at some carriers you '
   'drop into a different tier entirely. The same driver, the same car and the same '
   'record can be priced very differently on either side of a thirty-day gap.']),
 ('How long it counts',
  ['Most carriers look back six months to a year for prior coverage, and some go '
   'further. The gap stops being asked about eventually, but the credit for continuous '
   'coverage starts rebuilding from the day you are insured again.',
   'Which is the practical point: the sooner it is fixed, the sooner the clock starts. '
   'A gap that is six months old is worth much less against you than one that is still '
   'open.']),
 ('Not all gaps are the same',
  [('ul',
    ['<b>Under 30 days</b> is treated far more gently at most carriers than a longer '
     'one — sometimes barely at all.',
     '<b>A gap with a reason</b> can be documented. Deployment, a car sold, a period '
     'out of the country, a stay in hospital — say so, because at some carriers it is '
     'handled differently.',
     '<b>An open gap</b> is the expensive one. The price is being quoted against a '
     'risk that is still live.'])]),
 ('The registration problem',
  ['Texas and New Mexico both verify insurance electronically against the vehicle '
   'registration. A lapse on a registered car can trigger a notice and, left alone, a '
   'suspended registration and reinstatement fees.',
   'In some cases it also brings an SR-22 requirement afterwards. A gap that started '
   'as a missed payment turns into a filing obligation for two or three years, which '
   'is a long tail on a single month of saving.']),
 ('The mistake behind most lapses',
  ['Almost none of them are deliberate. They are a card that expired, a payment that '
   'fell on a bad week, a policy cancelled while a car was being sold, a move where '
   'the mail did not follow.',
   ('ul',
    ['Put the premium on automatic payment.',
     'Never cancel the old policy before the new one is active — not even by a day.',
     'If a car is genuinely off the road, ask about storage or comprehensive-only '
     'coverage rather than cancelling.',
     'Update the address the day you move.'])]),
 ('Getting covered again',
  ['Say the gap out loud when you call. It changes which carriers are worth quoting, '
   'and it will be found in the report either way — a quote built around it is a quote '
   'that gets repriced.',
   'And re-shop in six months. The gap will be worth less against you then than it is '
   'today, and most people never go back to check.'])],
 'key': ['A lapse loses the credit and can drop you a tier at the same time.',
 'Under 30 days is treated much more gently than longer.',
 'A lapse on a registered car risks the registration itself.',
 'Re-shop six months after you are covered again — it is worth less by then.'],
 'faq': [('How long is too long?',
  'Thirty days is the line at a lot of carriers, though not all. Past that it is '
  'handled as a genuine gap, and past a year the list of carriers that want the '
  'business gets shorter.'),
 ('Will they know if I do not say?',
  'Yes. Prior coverage is verified from a report, not from what was typed into the '
  'form. The only thing not saying achieves is a price that changes after you have '
  'bought.'),
 ('I sold my car and had nothing for a year. Same thing?',
  'It is still a gap, but it is a documentable one, and a non-owner policy during that '
  'period would have prevented it entirely. Worth knowing for next time.')],
},

{
 'group': 'situations',
 'slug': 'rideshare-and-delivery-insurance',
 'nav': 'Rideshare & Delivery',
 'card': 'The gap between your personal policy and the app — and what actually closes it.',
 'title': 'Rideshare and Delivery Car Insurance',
 'desc': ('Why a personal car insurance policy does not cover Uber, Lyft, DoorDash or Amazon '
 'Flex, what the app actually covers, and how to close the gap.'),
 'h1': 'Driving for Uber, Lyft or a delivery app',
 'lede': ('A personal car insurance policy excludes driving for money. The app covers part of '
 'the time you are working. The part in between is the one that ends badly.'),
 'body': [('The three periods',
  ['Everyone in this business talks about periods, and it is worth knowing them '
   'because it is where the gap lives.',
   ('ul',
    ['<b>Period 0 — app off.</b> Your personal policy, normally.',
     '<b>Period 1 — app on, waiting for a request.</b> This is the gap. The platform '
     'usually provides liability only, at low limits, with no coverage at all for your '
     'own car.',
     '<b>Period 2 — request accepted, on the way.</b> The platform’s coverage steps up '
     'substantially.',
     '<b>Period 3 — passenger or order on board.</b> The platform’s full coverage '
     'applies.'])]),
 ('What a personal policy actually says',
  ['Nearly every personal auto policy contains a livery or public-conveyance '
   'exclusion: coverage does not apply while the vehicle is being used to carry people '
   'or property for a fee.',
   'That exclusion does not care whether you told anybody. A claim during a delivery '
   'on a personal policy is a denied claim, and at that point the carrier also knows '
   'what the car has been doing.']),
 ('What closes the gap',
  [('ul',
    ['<b>A rideshare endorsement.</b> Added to the personal policy, usually '
     'inexpensive, and it extends your own coverage through period 1. The simplest fix '
     'where the carrier offers it.',
     '<b>A commercial auto policy.</b> Necessary once the driving is a real operation '
     'rather than evenings and weekends, and required by some contracts outright.']),
   'Not every carrier offers the endorsement, and the ones that do are not always the '
   'ones you would expect. This is a short conversation with an agent and a long one '
   'without.']),
 ('The deductible nobody mentions',
  ['Even in periods 2 and 3, the platform’s physical damage coverage usually carries a '
   'deductible far higher than the one on your own policy — often well into four '
   'figures.',
   'A rideshare endorsement frequently brings that down to your own deductible. It is '
   'the part of the conversation that pays for itself.']),
 ('Delivery is not always the same as rideshare',
  ['Food delivery, parcel delivery and grocery delivery are rated differently from '
   'passenger rideshare, and not every endorsement covers both. Amazon Flex, DoorDash '
   'and Uber Eats are not automatically included because you told the carrier you '
   'drive for Uber.',
   'Say exactly which apps you use. It is a thirty-second question with a very '
   'expensive wrong answer.'])],
 'key': ['Period 1 — app on, no request — is the gap that ends badly.',
 'Personal policies exclude driving for a fee, told or untold.',
 'A rideshare endorsement is usually cheap and usually the right fix.',
 'Name every app you drive for; they are not rated the same.'],
 'faq': [('Will my insurance company find out?',
  'At a claim, yes. Adjusters ask what the vehicle was doing and the app has records. '
  'It is far cheaper to declare it than to have it discovered.'),
 ('Does the app’s insurance not cover me?',
  'Partly. It is strongest with a passenger or order on board and weakest while you '
  'are waiting for a request, which is where a lot of driving time actually goes.'),
 ('Do I need commercial insurance?',
  'Not for most part-time drivers — an endorsement is usually enough. Once it is a '
  'full-time operation, or a vehicle is dedicated to it, commercial is the right '
  'answer. We write both.')],
},

]

GUIDES = GUIDES + SITUATIONS
