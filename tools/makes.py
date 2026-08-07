"""Vehicle makes sold in the United States, for the /car-insurance/<make>/ pages.

Each row is (slug, name, parent, origin, tags, note).

`parent` and `origin` are corporate facts and checkable. `tags` decide which of
the written sections a page gets — a luxury page argues about specialist repair
networks, an EV page about battery replacement and mandatory dealer repair, a
truck page about business use. `note` is one true sentence that nothing else on
the site says.

What is NOT here, on purpose: average premiums by make, MPG figures, repair
cost dollars, theft counts. Those change by model, year, trim and state, we do
not have a source for them, and a fabricated number on a page whose whole job
is to be trusted is worse than no page.

tags: luxury, ev, truck, performance, economy, offroad, discontinued,
      mainstream, big-repair (aluminium bodies, sensor-dense bumpers),
      exotic (rarely written on a standard personal auto policy at all)
"""

MAKES = [
 # ---------------- American ----------------
 ('ford','Ford','Ford Motor Company','American',['mainstream','truck','ev','performance'],
  'The F-Series pickup has been the best-selling vehicle line in the country for decades, which is why an F-150 quote is one of the most competitive things we shop.'),
 ('chevrolet','Chevrolet','General Motors','American',['mainstream','truck','ev','performance'],
  'Chevrolet spans a $20,000 Trax and a $100,000 Corvette under one badge, and the two are not remotely the same insurance conversation.'),
 ('gmc','GMC','General Motors','American',['truck','luxury'],
  'GMC is General Motors’ truck-and-SUV division, sharing platforms with Chevrolet but trimmed upmarket — which shows up in parts prices more than people expect.'),
 ('ram','Ram','Stellantis','American',['truck'],
  'Ram was split out of Dodge as its own truck brand in 2009, so an older pickup may still be titled as a Dodge.'),
 ('jeep','Jeep','Stellantis','American',['offroad','truck'],
  'Jeep is the brand most often modified by its owners, and a lift kit or aftermarket bumper is exactly the kind of thing a policy needs to know about.'),
 ('dodge','Dodge','Stellantis','American',['performance','mainstream'],
  'Dodge kept building large-displacement muscle cars long after the rest of the industry moved on, and Hellcat trims are rated very differently from a base Charger.'),
 ('chrysler','Chrysler','Stellantis','American',['mainstream'],
  'Chrysler’s current US lineup is essentially one minivan, which makes it one of the simplest brands to quote.'),
 ('cadillac','Cadillac','General Motors','American',['luxury','ev','performance','big-repair'],
  'Cadillac now sells both a V-Series with more than 600 horsepower and the electric LYRIQ, and those two sit at opposite ends of the rating table.'),
 ('buick','Buick','General Motors','American',['mainstream','luxury'],
  'Buick has quietly become an all-SUV brand in the US, and its cars are among the least likely on the road to be driven hard — which insurers notice.'),
 ('lincoln','Lincoln','Ford Motor Company','American',['luxury','big-repair'],
  'Lincoln shares its platforms with Ford but not its parts prices, and the difference between repairing a Navigator and an Expedition is real money.'),
 ('tesla','Tesla','Tesla, Inc.','American',['ev','performance','big-repair'],
  'Teslas are repaired through an approved network rather than any body shop, and that constraint — not the battery — is what most often drives the premium.'),
 ('rivian','Rivian','Rivian','American',['ev','truck','offroad','big-repair'],
  'Rivian builds an electric pickup and SUV with an aluminium structure, a combination that puts it firmly in the expensive-to-repair column.'),
 ('lucid','Lucid','Lucid Motors','American',['ev','luxury','performance','big-repair'],
  'Lucid is a low-volume luxury EV maker, and low volume is itself a rating factor — fewer shops, fewer parts, longer repairs.'),

 # ---------------- Japanese ----------------
 ('toyota','Toyota','Toyota Motor Corporation','Japanese',['mainstream','economy','truck'],
  'Toyota’s reputation for holding value cuts both ways on a policy: cheap to repair, but worth enough for longer that dropping collision early is a mistake.'),
 ('honda','Honda','Honda Motor Co.','Japanese',['mainstream','economy'],
  'Civics and Accords are among the most commonly stolen vehicles in the country, largely because their parts fit so many other cars on the road.'),
 ('nissan','Nissan','Nissan Motor Corporation','Japanese',['mainstream','economy','ev'],
  'Nissan sells both the Leaf and the GT-R, and a brand-level statement about what a Nissan costs to insure is meaningless without the model.'),
 ('mazda','Mazda','Mazda Motor Corporation','Japanese',['mainstream','economy','performance'],
  'Mazda has pushed upmarket in interior and materials without a luxury badge, which means repair bills that sit above what the price tag suggests.'),
 ('subaru','Subaru','Subaru Corporation','Japanese',['mainstream','offroad'],
  'Almost every Subaru sold in the US is all-wheel drive, and that drivetrain is more expensive to put right after a collision than a front-wheel-drive equivalent.'),
 ('mitsubishi','Mitsubishi','Mitsubishi Motors','Japanese',['economy','mainstream'],
  'Mitsubishi’s long powertrain warranty is a selling point at the dealer and irrelevant to your policy — warranty and insurance cover different things entirely.'),
 ('lexus','Lexus','Toyota Motor Corporation','Japanese',['luxury','big-repair'],
  'Lexus is Toyota’s luxury division, which means Toyota reliability with luxury parts pricing — a good combination for you and a mixed one for a quote.'),
 ('acura','Acura','Honda Motor Co.','Japanese',['luxury','performance'],
  'Acura sits close enough to Honda mechanically that repairs are reasonable, and far enough upmarket that the sensors in the bumpers are not.'),
 ('infiniti','Infiniti','Nissan Motor Corporation','Japanese',['luxury','performance','big-repair'],
  'Infiniti is Nissan’s luxury brand, and its performance trims carry engines that rating tables treat very differently from the equivalent Nissan.'),

 # ---------------- Korean ----------------
 ('hyundai','Hyundai','Hyundai Motor Group','Korean',['mainstream','economy','ev'],
  'Certain 2011-2021 Hyundais built without an engine immobiliser became widely targeted for theft, and some carriers still price those model years accordingly.'),
 ('kia','Kia','Hyundai Motor Group','Korean',['mainstream','economy','ev'],
  'Kia shares the same immobiliser issue on certain 2011-2021 models, and if yours is one of them, the anti-theft software update is worth asking your carrier about.'),
 ('genesis','Genesis','Hyundai Motor Group','Korean',['luxury','performance','big-repair'],
  'Genesis was split from Hyundai as a standalone luxury brand in 2015, and it is priced like a luxury brand at the body shop.'),

 # ---------------- German ----------------
 ('bmw','BMW','BMW Group','German',['luxury','performance','ev','big-repair'],
  'BMW’s M division and its base models share a badge and almost nothing else on a rate sheet — an M3 and a 330i are different insurance products.'),
 ('mercedes-benz','Mercedes-Benz','Mercedes-Benz Group','German',['luxury','performance','ev','big-repair'],
  'Mercedes sells everything from a compact sedan to the Sprinter van, and the Sprinter is commercial the moment it carries anything for work.'),
 ('audi','Audi','Volkswagen Group','German',['luxury','performance','ev','big-repair'],
  'Audi uses aluminium extensively in its structures, and aluminium repair requires a separately certified shop — fewer options, higher labour.'),
 ('volkswagen','Volkswagen','Volkswagen Group','German',['mainstream','economy','ev'],
  'Volkswagen sits between mainstream and premium in parts pricing, which is why VW quotes often surprise people who expected Toyota numbers.'),
 ('porsche','Porsche','Volkswagen Group','German',['luxury','performance','ev','big-repair'],
  'Porsche holds value unusually well, and a policy written on an outdated agreed value is one of the more expensive mistakes an owner can make.'),

 # ---------------- European ----------------
 ('volvo','Volvo','Geely','Swedish',['luxury','ev','big-repair'],
  'Volvo built its brand on crash safety, and the sensors and structures that deliver it are exactly what makes a modern Volvo expensive to repair.'),
 ('polestar','Polestar','Geely','Swedish',['ev','luxury','performance','big-repair'],
  'Polestar is Volvo’s electric performance brand, sold through a small network — which means fewer shops qualified to touch it after a claim.'),
 ('land-rover','Land Rover','JLR (Tata Motors)','British',['luxury','offroad','big-repair'],
  'Land Rover combines genuine off-road capability with luxury pricing, and owners who actually use it off-road should say so when quoting.'),
 ('jaguar','Jaguar','JLR (Tata Motors)','British',['luxury','performance','big-repair'],
  'Jaguar’s aluminium-intensive construction and low US volume put it among the more expensive brands to repair per panel.'),
 ('mini','MINI','BMW Group','British',['economy','performance'],
  'MINI is a BMW underneath, which is the part that shows up on the repair estimate rather than on the sticker.'),
 ('alfa-romeo','Alfa Romeo','Stellantis','Italian',['luxury','performance','big-repair'],
  'Alfa Romeo returned to the US market in 2014 with a small dealer network, and network size is a rating factor in its own right.'),
 ('maserati','Maserati','Stellantis','Italian',['luxury','performance','big-repair'],
  'Maserati is a low-volume luxury brand where a single body panel can cost more than a whole repair on a mainstream car.'),
 ('fiat','Fiat','Stellantis','Italian',['economy'],
  'Fiat’s US presence has shrunk to almost nothing, and a thin parts and service network makes an older 500 harder to repair than its size suggests.'),
 ('ferrari','Ferrari','Ferrari N.V.','Italian',['exotic','luxury','performance','big-repair'],
  'Ferrari repairs go through factory-authorised workshops only, and the waiting list for one is part of what a claim actually costs you.'),
 ('lamborghini','Lamborghini','Volkswagen Group','Italian',['exotic','luxury','performance','big-repair'],
  'Lamborghini bodies are largely carbon fibre and aluminium, materials that are replaced rather than repaired — there is no straightening a carbon tub.'),

 # ---------------- Ultra-luxury and low volume ----------------
 ('bentley','Bentley','Volkswagen Group','British',['exotic','luxury','big-repair'],
  'Bentley interiors are hand-finished, which means an interior claim on one can run past what a whole mainstream car is worth.'),
 ('rolls-royce','Rolls-Royce','BMW Group','British',['exotic','luxury','big-repair'],
  'Rolls-Royce sells a few thousand cars a year across the entire United States, and that volume is why almost no standard carrier will write one.'),
 ('aston-martin','Aston Martin','Aston Martin Lagonda','British',['exotic','luxury','performance','big-repair'],
  'Aston Martin builds in very small numbers with bonded aluminium structures, a construction that a general body shop is not equipped to touch.'),
 ('mclaren','McLaren','McLaren Automotive','British',['exotic','performance','big-repair'],
  'Every McLaren is built around a carbon fibre tub, and whether that tub survived an impact is the single question that decides a total loss.'),
 ('lotus','Lotus','Geely','British',['exotic','performance'],
  'Lotus built its name on light cars with minimal bodywork, and the newer electric models are the opposite of that in both weight and repair cost.'),
 ('vinfast','VinFast','Vingroup','Vietnamese',['ev','big-repair'],
  'VinFast started US deliveries in 2023, and a service network that new is a fair question to ask a carrier about before you buy the car.'),

 # ---------------- No longer sold new in the US ----------------
 ('pontiac','Pontiac','General Motors','American',['discontinued','performance'],
  'General Motors wound Pontiac down in 2010, so every one on the road is at least that old — which changes the collision-coverage arithmetic completely.'),
 ('saturn','Saturn','General Motors','American',['discontinued','economy'],
  'Saturn ended in 2010. Parts still exist through GM channels, but availability is the thing to ask about before insuring one for more than liability.'),
 ('mercury','Mercury','Ford Motor Company','American',['discontinued'],
  'Ford closed Mercury in 2011. Most models shared a platform with a Ford, which is what keeps parts findable.'),
 ('oldsmobile','Oldsmobile','General Motors','American',['discontinued'],
  'Oldsmobile ended in 2004, making it the oldest brand on this list still turning up on quotes — usually as a liability-only policy.'),
 ('hummer','Hummer','General Motors','American',['discontinued','offroad','truck'],
  'The Hummer brand ended in 2010; the name came back as an electric GMC model, and the two are not the same vehicle on a policy.'),
 ('scion','Scion','Toyota Motor Corporation','Japanese',['discontinued','economy'],
  'Toyota folded Scion back into the main brand in 2016, and some models simply became Toyotas — so check what your title actually says.'),
 ('suzuki','Suzuki','Suzuki Motor Corporation','Japanese',['discontinued','economy'],
  'Suzuki left the US car market in 2013 while continuing to sell motorcycles, which is why a Suzuki quote depends entirely on which kind you have.'),
 ('isuzu','Isuzu','Isuzu Motors','Japanese',['discontinued','truck'],
  'Isuzu stopped selling passenger vehicles in the US in 2009 and now sells commercial trucks — those are a commercial policy, not a personal one.'),
 ('saab','Saab','—','Swedish',['discontinued','performance'],
  'Saab stopped production in 2011, and the parts situation is the single biggest question on any Saab policy above liability.'),
 ('plymouth','Plymouth','Chrysler','American',['discontinued','economy'],
  'Chrysler ended Plymouth in 2001, and most of what it sold was badge-shared with Dodge — which is what still keeps parts on the shelf.'),
 ('geo','Geo','General Motors','American',['discontinued','economy'],
  'Geo was General Motors’ import-badge experiment and ended in 1997; a Geo Metro or Prizm is mechanically a Suzuki or a Toyota underneath.'),
 ('eagle','Eagle','Chrysler','American',['discontinued'],
  'Eagle came out of Chrysler’s purchase of American Motors and ended in 1998, so anything wearing the badge is older than most drivers on the policy.'),
 ('daewoo','Daewoo','General Motors','Korean',['discontinued','economy'],
  'Daewoo left the US in 2002 and its models were later rebadged as Suzukis and Chevrolets, which is the only reason parts are findable at all.'),
 ('smart','smart','Mercedes-Benz Group','German',['discontinued','economy'],
  'smart stopped US sales in 2019. The car is unusually small, and small does not mean cheap to repair when the parts come from Mercedes.'),
]

# Bodies that change the conversation, for the model picker.
BODY_NOTES = {
  'truck':  ('Pickup', 'If it carries anything for work — tools, materials, a trailer for pay — a personal policy may not cover the claim. Say what it does.'),
  'suv':    ('SUV', 'Higher repair costs than a sedan of the same price, and more of them are financed, which means the lender will require collision and comprehensive.'),
  'sedan':  ('Sedan', 'The easiest body style to insure and to repair. Also the most commonly stolen, because the parts fit so many other cars.'),
  'sports': ('Sports car', 'Rated on the engine, not the badge. A performance trim can cost more to insure than an SUV twice its price.'),
  'ev':     ('Electric', 'Battery replacement is the largest single repair bill in the industry, which is why a total-loss threshold is reached sooner than owners expect.'),
  'van':    ('Van or minivan', 'A family minivan is straightforward. A cargo van that carries anything for a business is a commercial policy.'),
}
