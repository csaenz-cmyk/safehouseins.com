"""Vehicle makes sold in the United States, for the /car-insurance/<make>/ pages.

Each row is (slug, name, parent, origin, tags).

`parent` and `origin` are corporate facts and checkable. `tags` decide which of
the written sections a page gets — a luxury page argues about specialist repair
networks, an EV page about battery replacement and mandatory dealer repair, a
truck page about business use.

Names and parent companies are proper nouns and stay here. The words are in
locales/<lang>/makes.json, in English and Spanish: `origin` is a key into
makes.origin (the adjective, and the heading the hub groups under), and each
brand's note — one true sentence that nothing else on the site says — is
makes.note.<slug>.

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
 ('ford','Ford','Ford Motor Company','american',['mainstream','truck','ev','performance']),
 ('chevrolet','Chevrolet','General Motors','american',['mainstream','truck','ev','performance']),
 ('gmc','GMC','General Motors','american',['truck','luxury']),
 ('ram','Ram','Stellantis','american',['truck']),
 ('jeep','Jeep','Stellantis','american',['offroad','truck']),
 ('dodge','Dodge','Stellantis','american',['performance','mainstream']),
 ('chrysler','Chrysler','Stellantis','american',['mainstream']),
 ('cadillac','Cadillac','General Motors','american',['luxury','ev','performance','big-repair']),
 ('buick','Buick','General Motors','american',['mainstream','luxury']),
 ('lincoln','Lincoln','Ford Motor Company','american',['luxury','big-repair']),
 ('tesla','Tesla','Tesla, Inc.','american',['ev','performance','big-repair']),
 ('rivian','Rivian','Rivian','american',['ev','truck','offroad','big-repair']),
 ('lucid','Lucid','Lucid Motors','american',['ev','luxury','performance','big-repair']),

 # ---------------- Japanese ----------------
 ('toyota','Toyota','Toyota Motor Corporation','japanese',['mainstream','economy','truck']),
 ('honda','Honda','Honda Motor Co.','japanese',['mainstream','economy']),
 ('nissan','Nissan','Nissan Motor Corporation','japanese',['mainstream','economy','ev']),
 ('mazda','Mazda','Mazda Motor Corporation','japanese',['mainstream','economy','performance']),
 ('subaru','Subaru','Subaru Corporation','japanese',['mainstream','offroad']),
 ('mitsubishi','Mitsubishi','Mitsubishi Motors','japanese',['economy','mainstream']),
 ('lexus','Lexus','Toyota Motor Corporation','japanese',['luxury','big-repair']),
 ('acura','Acura','Honda Motor Co.','japanese',['luxury','performance']),
 ('infiniti','Infiniti','Nissan Motor Corporation','japanese',['luxury','performance','big-repair']),

 # ---------------- Korean ----------------
 ('hyundai','Hyundai','Hyundai Motor Group','korean',['mainstream','economy','ev']),
 ('kia','Kia','Hyundai Motor Group','korean',['mainstream','economy','ev']),
 ('genesis','Genesis','Hyundai Motor Group','korean',['luxury','performance','big-repair']),

 # ---------------- German ----------------
 ('bmw','BMW','BMW Group','german',['luxury','performance','ev','big-repair']),
 ('mercedes-benz','Mercedes-Benz','Mercedes-Benz Group','german',['luxury','performance','ev','big-repair']),
 ('audi','Audi','Volkswagen Group','german',['luxury','performance','ev','big-repair']),
 ('volkswagen','Volkswagen','Volkswagen Group','german',['mainstream','economy','ev']),
 ('porsche','Porsche','Volkswagen Group','german',['luxury','performance','ev','big-repair']),

 # ---------------- European ----------------
 ('volvo','Volvo','Geely','swedish',['luxury','ev','big-repair']),
 ('polestar','Polestar','Geely','swedish',['ev','luxury','performance','big-repair']),
 ('land-rover','Land Rover','JLR (Tata Motors)','british',['luxury','offroad','big-repair']),
 ('jaguar','Jaguar','JLR (Tata Motors)','british',['luxury','performance','big-repair']),
 ('mini','MINI','BMW Group','british',['economy','performance']),
 ('alfa-romeo','Alfa Romeo','Stellantis','italian',['luxury','performance','big-repair']),
 ('maserati','Maserati','Stellantis','italian',['luxury','performance','big-repair']),
 ('fiat','Fiat','Stellantis','italian',['economy']),
 ('ferrari','Ferrari','Ferrari N.V.','italian',['exotic','luxury','performance','big-repair']),
 ('lamborghini','Lamborghini','Volkswagen Group','italian',['exotic','luxury','performance','big-repair']),

 # ---------------- Ultra-luxury and low volume ----------------
 ('bentley','Bentley','Volkswagen Group','british',['exotic','luxury','big-repair']),
 ('rolls-royce','Rolls-Royce','BMW Group','british',['exotic','luxury','big-repair']),
 ('aston-martin','Aston Martin','Aston Martin Lagonda','british',['exotic','luxury','performance','big-repair']),
 ('mclaren','McLaren','McLaren Automotive','british',['exotic','performance','big-repair']),
 ('lotus','Lotus','Geely','british',['exotic','performance']),
 ('vinfast','VinFast','Vingroup','vietnamese',['ev','big-repair']),

 # ---------------- No longer sold new in the US ----------------
 ('pontiac','Pontiac','General Motors','american',['discontinued','performance']),
 ('saturn','Saturn','General Motors','american',['discontinued','economy']),
 ('mercury','Mercury','Ford Motor Company','american',['discontinued']),
 ('oldsmobile','Oldsmobile','General Motors','american',['discontinued']),
 ('hummer','Hummer','General Motors','american',['discontinued','offroad','truck']),
 ('scion','Scion','Toyota Motor Corporation','japanese',['discontinued','economy']),
 ('suzuki','Suzuki','Suzuki Motor Corporation','japanese',['discontinued','economy']),
 ('isuzu','Isuzu','Isuzu Motors','japanese',['discontinued','truck']),
 ('saab','Saab','—','swedish',['discontinued','performance']),
 ('plymouth','Plymouth','Chrysler','american',['discontinued','economy']),
 ('geo','Geo','General Motors','american',['discontinued','economy']),
 ('eagle','Eagle','Chrysler','american',['discontinued']),
 ('daewoo','Daewoo','General Motors','korean',['discontinued','economy']),
 ('smart','smart','Mercedes-Benz Group','german',['discontinued','economy']),
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
