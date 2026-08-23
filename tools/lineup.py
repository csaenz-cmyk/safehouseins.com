"""Model lineups per make, and the brand-specific angle each page argues.

This file is what stops the brand pages being one article with the name
swapped. The model list is real and different for every make, and the flags on
each model drive which coverage points that model's card shows — a Wrangler
raises modifications, an F-150 raises business use, a Model Y raises the
approved repair network. None of that is written 60 times; it is derived.

Model rows are (name, body, label, flags).

  body   — one of the shapes in vehiclesvg.BODY_SHAPE
  label  — what the card shows under the name
  flags  — 'ev', 'perf', 'offroad', 'work', 'lux', 'value', 'old'

What is deliberately NOT in here: model years, prices, premiums, repair costs,
MPG, theft rankings. Lineups shift year to year and a stale model year on a
page is a small lie; the pages say what a model IS, not what it costs.

`accent` is a tasteful page tint chosen to sit well with the brand. It is not
a logo color and no manufacturer mark is used anywhere on these pages.
"""

# ---------------------------------------------------------------- lineups ---
L = {

# ============================== American ==============================
'ford': dict(accent='#1B4C8C', models=[
  ('F-150', 'truck', 'Full-size pickup', ['work', 'value']),
  ('Super Duty', 'truck', 'Heavy-duty pickup', ['work']),
  ('Ranger', 'truck', 'Mid-size pickup', ['work']),
  ('Maverick', 'truck', 'Compact pickup', ['work']),
  ('Bronco', 'suv', 'Off-road SUV', ['offroad']),
  ('Bronco Sport', 'suv', 'Compact SUV', []),
  ('Explorer', 'suv', 'Three-row SUV', []),
  ('Expedition', 'suv-large', 'Full-size SUV', []),
  ('Escape', 'suv', 'Compact SUV', []),
  ('Mustang', 'sports', 'Sports car', ['perf']),
  ('Mustang Mach-E', 'suv', 'Electric SUV', ['ev']),
  ('Edge', 'suv', 'Mid-size SUV', []),
  ('Transit', 'van', 'Cargo and passenger van', ['work']),
]),

'chevrolet': dict(accent='#B8892A', models=[
  ('Silverado', 'truck', 'Full-size pickup', ['work', 'value']),
  ('Colorado', 'truck', 'Mid-size pickup', ['work']),
  ('Tahoe', 'suv-large', 'Full-size SUV', []),
  ('Suburban', 'suv-large', 'Extended full-size SUV', []),
  ('Traverse', 'suv', 'Three-row SUV', []),
  ('Equinox', 'suv', 'Compact SUV', []),
  ('Blazer', 'suv', 'Mid-size SUV', []),
  ('Trailblazer', 'suv', 'Subcompact SUV', []),
  ('Trax', 'suv', 'Subcompact SUV', []),
  ('Malibu', 'sedan', 'Mid-size sedan', []),
  ('Camaro', 'sports', 'Sports car', ['perf']),
  ('Corvette', 'sports', 'Sports car', ['perf', 'value']),
  ('Equinox EV', 'suv', 'Electric SUV', ['ev']),
  ('Blazer EV', 'suv', 'Electric SUV', ['ev']),
  ('Silverado EV', 'truck', 'Electric pickup', ['ev', 'work']),
  ('Express', 'van', 'Cargo and passenger van', ['work']),
]),

'gmc': dict(accent='#8C2F39', models=[
  ('Sierra', 'truck', 'Full-size pickup', ['work', 'value']),
  ('Sierra HD', 'truck', 'Heavy-duty pickup', ['work']),
  ('Canyon', 'truck', 'Mid-size pickup', ['work']),
  ('Yukon', 'suv-large', 'Full-size SUV', ['lux']),
  ('Yukon XL', 'suv-large', 'Extended full-size SUV', ['lux']),
  ('Acadia', 'suv', 'Three-row SUV', []),
  ('Terrain', 'suv', 'Compact SUV', []),
  ('Hummer EV', 'truck', 'Electric pickup', ['ev', 'offroad']),
  ('Sierra EV', 'truck', 'Electric pickup', ['ev', 'work']),
  ('Savana', 'van', 'Cargo and passenger van', ['work']),
]),

'ram': dict(accent='#7A2E2E', models=[
  ('1500', 'truck', 'Full-size pickup', ['work', 'value']),
  ('2500', 'truck', 'Heavy-duty pickup', ['work']),
  ('3500', 'truck', 'Heavy-duty pickup', ['work']),
  ('ProMaster', 'van', 'Cargo van', ['work']),
]),

'jeep': dict(accent='#3E5C3A', models=[
  ('Wrangler', 'suv', 'Off-road SUV', ['offroad', 'value']),
  ('Gladiator', 'truck', 'Off-road pickup', ['offroad', 'work']),
  ('Grand Cherokee', 'suv', 'Mid-size SUV', []),
  ('Cherokee', 'suv', 'Mid-size SUV', []),
  ('Compass', 'suv', 'Compact SUV', []),
  ('Renegade', 'suv', 'Subcompact SUV', []),
  ('Wagoneer', 'suv-large', 'Full-size SUV', ['lux']),
  ('Grand Wagoneer', 'suv-large', 'Full-size luxury SUV', ['lux']),
]),

'dodge': dict(accent='#8A2331', models=[
  ('Charger', 'sedan', 'Performance sedan', ['perf']),
  ('Challenger', 'sports', 'Muscle coupe', ['perf']),
  ('Durango', 'suv', 'Three-row SUV', ['perf']),
  ('Hornet', 'suv', 'Compact SUV', []),
  ('Journey', 'suv', 'Mid-size SUV', ['old']),
  ('Grand Caravan', 'minivan', 'Minivan', ['old']),
]),

'chrysler': dict(accent='#2F4E6E', models=[
  ('Pacifica', 'minivan', 'Minivan', []),
  ('Voyager', 'minivan', 'Minivan', []),
  ('300', 'sedan', 'Full-size sedan', ['old']),
  ('Town & Country', 'minivan', 'Minivan', ['old']),
]),

'cadillac': dict(accent='#6E2639', models=[
  ('Escalade', 'suv-large', 'Full-size luxury SUV', ['lux']),
  ('XT6', 'suv', 'Three-row luxury SUV', ['lux']),
  ('XT5', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('XT4', 'suv', 'Compact luxury SUV', ['lux']),
  ('CT5', 'sedan', 'Luxury sedan', ['lux', 'perf']),
  ('CT4', 'sedan', 'Compact luxury sedan', ['lux', 'perf']),
  ('LYRIQ', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
]),

'buick': dict(accent='#7A2C3E', models=[
  ('Envista', 'suv', 'Compact SUV', []),
  ('Encore GX', 'suv', 'Subcompact SUV', []),
  ('Envision', 'suv', 'Compact SUV', []),
  ('Enclave', 'suv-large', 'Three-row SUV', ['lux']),
]),

'lincoln': dict(accent='#354A66', models=[
  ('Navigator', 'suv-large', 'Full-size luxury SUV', ['lux']),
  ('Aviator', 'suv', 'Three-row luxury SUV', ['lux']),
  ('Nautilus', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('Corsair', 'suv', 'Compact luxury SUV', ['lux']),
]),

'tesla': dict(accent='#8E2A2A', models=[
  ('Model 3', 'sedan', 'Electric sedan', ['ev']),
  ('Model Y', 'suv', 'Electric SUV', ['ev']),
  ('Model S', 'sedan', 'Electric luxury sedan', ['ev', 'lux', 'perf']),
  ('Model X', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
  ('Cybertruck', 'truck', 'Electric pickup', ['ev', 'work']),
]),

'rivian': dict(accent='#3F6152', models=[
  ('R1T', 'truck', 'Electric pickup', ['ev', 'offroad', 'work']),
  ('R1S', 'suv-large', 'Electric three-row SUV', ['ev', 'offroad']),
]),

'lucid': dict(accent='#4A4E7C', models=[
  ('Air', 'sedan', 'Electric luxury sedan', ['ev', 'lux', 'perf']),
  ('Gravity', 'suv-large', 'Electric three-row SUV', ['ev', 'lux']),
]),

# ============================== Japanese ==============================
'toyota': dict(accent='#9A2B2B', models=[
  ('RAV4', 'suv', 'Compact SUV', ['value']),
  ('Camry', 'sedan', 'Mid-size sedan', ['value']),
  ('Corolla', 'sedan', 'Compact sedan', ['value']),
  ('Tacoma', 'truck', 'Mid-size pickup', ['work', 'value']),
  ('Tundra', 'truck', 'Full-size pickup', ['work']),
  ('Highlander', 'suv', 'Three-row SUV', []),
  ('Grand Highlander', 'suv-large', 'Three-row SUV', []),
  ('4Runner', 'suv', 'Off-road SUV', ['offroad', 'value']),
  ('Sequoia', 'suv-large', 'Full-size SUV', []),
  ('Land Cruiser', 'suv', 'Off-road SUV', ['offroad', 'value']),
  ('Sienna', 'minivan', 'Minivan', []),
  ('Prius', 'hatch', 'Hybrid hatchback', []),
  ('Corolla Cross', 'suv', 'Subcompact SUV', []),
  ('bZ4X', 'suv', 'Electric SUV', ['ev']),
  ('GR Supra', 'sports', 'Sports car', ['perf']),
]),

'honda': dict(accent='#8C2727', models=[
  ('CR-V', 'suv', 'Compact SUV', ['value']),
  ('Civic', 'sedan', 'Compact sedan', ['value']),
  ('Accord', 'sedan', 'Mid-size sedan', ['value']),
  ('Pilot', 'suv', 'Three-row SUV', []),
  ('HR-V', 'suv', 'Subcompact SUV', []),
  ('Passport', 'suv', 'Mid-size SUV', []),
  ('Odyssey', 'minivan', 'Minivan', []),
  ('Ridgeline', 'truck', 'Mid-size pickup', ['work']),
  ('Prologue', 'suv', 'Electric SUV', ['ev']),
]),

'nissan': dict(accent='#8A2E38', models=[
  ('Rogue', 'suv', 'Compact SUV', []),
  ('Altima', 'sedan', 'Mid-size sedan', []),
  ('Sentra', 'sedan', 'Compact sedan', []),
  ('Versa', 'sedan', 'Subcompact sedan', []),
  ('Kicks', 'suv', 'Subcompact SUV', []),
  ('Murano', 'suv', 'Mid-size SUV', []),
  ('Pathfinder', 'suv', 'Three-row SUV', []),
  ('Armada', 'suv-large', 'Full-size SUV', []),
  ('Frontier', 'truck', 'Mid-size pickup', ['work']),
  ('Titan', 'truck', 'Full-size pickup', ['work']),
  ('Maxima', 'sedan', 'Full-size sedan', ['old']),
  ('Leaf', 'hatch', 'Electric hatchback', ['ev']),
  ('Ariya', 'suv', 'Electric SUV', ['ev']),
  ('Z', 'sports', 'Sports car', ['perf']),
  ('GT-R', 'sports', 'High-performance sports car', ['perf']),
]),

'mazda': dict(accent='#7B2B3B', models=[
  ('CX-5', 'suv', 'Compact SUV', []),
  ('CX-50', 'suv', 'Compact SUV', ['offroad']),
  ('CX-30', 'suv', 'Subcompact SUV', []),
  ('CX-70', 'suv', 'Two-row mid-size SUV', ['lux']),
  ('CX-90', 'suv-large', 'Three-row SUV', ['lux']),
  ('Mazda3', 'sedan', 'Compact sedan and hatchback', []),
  ('MX-5 Miata', 'sports', 'Roadster', ['perf']),
]),

'subaru': dict(accent='#2F4C7A', models=[
  ('Outback', 'wagon', 'All-wheel-drive wagon', ['offroad', 'value']),
  ('Forester', 'suv', 'Compact SUV', ['value']),
  ('Crosstrek', 'suv', 'Subcompact SUV', ['offroad', 'value']),
  ('Ascent', 'suv', 'Three-row SUV', []),
  ('Impreza', 'hatch', 'Compact hatchback', []),
  ('Legacy', 'sedan', 'Mid-size sedan', []),
  ('WRX', 'sedan', 'Performance sedan', ['perf']),
  ('BRZ', 'sports', 'Sports car', ['perf']),
  ('Solterra', 'suv', 'Electric SUV', ['ev']),
]),

'mitsubishi': dict(accent='#8A2A2A', models=[
  ('Outlander', 'suv', 'Compact SUV', []),
  ('Outlander Sport', 'suv', 'Subcompact SUV', []),
  ('Eclipse Cross', 'suv', 'Subcompact SUV', []),
  ('Mirage', 'hatch', 'Subcompact hatchback', []),
]),

'lexus': dict(accent='#4C4F5C', models=[
  ('RX', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('NX', 'suv', 'Compact luxury SUV', ['lux']),
  ('TX', 'suv-large', 'Three-row luxury SUV', ['lux']),
  ('GX', 'suv', 'Off-road luxury SUV', ['lux', 'offroad', 'value']),
  ('LX', 'suv-large', 'Full-size luxury SUV', ['lux', 'offroad']),
  ('UX', 'suv', 'Subcompact luxury SUV', ['lux']),
  ('ES', 'sedan', 'Luxury sedan', ['lux']),
  ('IS', 'sedan', 'Compact luxury sedan', ['lux', 'perf']),
  ('LS', 'sedan', 'Full-size luxury sedan', ['lux']),
  ('RZ', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
]),

'acura': dict(accent='#3C4F63', models=[
  ('MDX', 'suv', 'Three-row luxury SUV', ['lux']),
  ('RDX', 'suv', 'Compact luxury SUV', ['lux']),
  ('Integra', 'hatch', 'Sport compact', ['perf']),
  ('TLX', 'sedan', 'Luxury sedan', ['lux', 'perf']),
  ('ZDX', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
]),

'infiniti': dict(accent='#4A5570', models=[
  ('QX60', 'suv', 'Three-row luxury SUV', ['lux']),
  ('QX80', 'suv-large', 'Full-size luxury SUV', ['lux']),
  ('QX50', 'suv', 'Compact luxury SUV', ['lux']),
  ('QX55', 'suv', 'Coupe-style luxury SUV', ['lux']),
  ('Q50', 'sedan', 'Luxury sport sedan', ['lux', 'perf']),
]),

# ============================== Korean ==============================
'hyundai': dict(accent='#2E5A7A', models=[
  ('Tucson', 'suv', 'Compact SUV', []),
  ('Santa Fe', 'suv', 'Mid-size SUV', []),
  ('Palisade', 'suv-large', 'Three-row SUV', []),
  ('Kona', 'suv', 'Subcompact SUV', []),
  ('Venue', 'suv', 'Subcompact SUV', []),
  ('Elantra', 'sedan', 'Compact sedan', []),
  ('Sonata', 'sedan', 'Mid-size sedan', []),
  ('Santa Cruz', 'truck', 'Compact pickup', ['work']),
  ('IONIQ 5', 'suv', 'Electric SUV', ['ev']),
  ('IONIQ 6', 'sedan', 'Electric sedan', ['ev']),
]),

'kia': dict(accent='#7B2F3F', models=[
  ('Sportage', 'suv', 'Compact SUV', []),
  ('Sorento', 'suv', 'Three-row SUV', []),
  ('Telluride', 'suv-large', 'Three-row SUV', []),
  ('Seltos', 'suv', 'Subcompact SUV', []),
  ('Soul', 'hatch', 'Compact hatchback', []),
  ('Forte', 'sedan', 'Compact sedan', []),
  ('K4', 'sedan', 'Compact sedan', []),
  ('K5', 'sedan', 'Mid-size sedan', []),
  ('Carnival', 'minivan', 'Minivan', []),
  ('Niro', 'suv', 'Hybrid and electric crossover', ['ev']),
  ('EV6', 'suv', 'Electric SUV', ['ev']),
  ('EV9', 'suv-large', 'Electric three-row SUV', ['ev']),
]),

'genesis': dict(accent='#5A4A63', models=[
  ('GV70', 'suv', 'Compact luxury SUV', ['lux']),
  ('GV80', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('GV60', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
  ('G70', 'sedan', 'Compact luxury sedan', ['lux', 'perf']),
  ('G80', 'sedan', 'Luxury sedan', ['lux']),
  ('G90', 'sedan', 'Full-size luxury sedan', ['lux']),
]),

# ============================== German ==============================
'bmw': dict(accent='#2B5580', models=[
  ('3 Series', 'sedan', 'Compact luxury sedan', ['lux']),
  ('5 Series', 'sedan', 'Mid-size luxury sedan', ['lux']),
  ('7 Series', 'sedan', 'Full-size luxury sedan', ['lux']),
  ('X1', 'suv', 'Subcompact luxury SUV', ['lux']),
  ('X3', 'suv', 'Compact luxury SUV', ['lux']),
  ('X5', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('X7', 'suv-large', 'Full-size luxury SUV', ['lux']),
  ('4 Series', 'sports', 'Luxury coupe and convertible', ['lux', 'perf']),
  ('M3', 'sedan', 'High-performance sedan', ['perf', 'lux']),
  ('Z4', 'sports', 'Roadster', ['perf']),
  ('i4', 'sedan', 'Electric sedan', ['ev', 'lux']),
  ('iX', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
]),

'mercedes-benz': dict(accent='#4A5560', models=[
  ('C-Class', 'sedan', 'Compact luxury sedan', ['lux']),
  ('E-Class', 'sedan', 'Mid-size luxury sedan', ['lux']),
  ('S-Class', 'sedan', 'Full-size luxury sedan', ['lux']),
  ('GLA', 'suv', 'Subcompact luxury SUV', ['lux']),
  ('GLB', 'suv', 'Compact luxury SUV', ['lux']),
  ('GLC', 'suv', 'Compact luxury SUV', ['lux']),
  ('GLE', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('GLS', 'suv-large', 'Full-size luxury SUV', ['lux']),
  ('G-Class', 'suv', 'Off-road luxury SUV', ['lux', 'offroad', 'value']),
  ('EQE', 'sedan', 'Electric luxury sedan', ['ev', 'lux']),
  ('EQS', 'sedan', 'Electric flagship sedan', ['ev', 'lux']),
  ('AMG GT', 'sports', 'High-performance sports car', ['perf', 'lux']),
  ('Sprinter', 'van', 'Cargo and passenger van', ['work']),
]),

'audi': dict(accent='#6E3540', models=[
  ('A3', 'sedan', 'Compact luxury sedan', ['lux']),
  ('A4', 'sedan', 'Compact luxury sedan', ['lux']),
  ('A5', 'sports', 'Luxury coupe and sportback', ['lux']),
  ('A6', 'sedan', 'Mid-size luxury sedan', ['lux']),
  ('Q3', 'suv', 'Subcompact luxury SUV', ['lux']),
  ('Q5', 'suv', 'Compact luxury SUV', ['lux']),
  ('Q7', 'suv-large', 'Three-row luxury SUV', ['lux']),
  ('Q8', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('Q4 e-tron', 'suv', 'Electric SUV', ['ev', 'lux']),
  ('e-tron GT', 'sedan', 'Electric performance sedan', ['ev', 'perf', 'lux']),
]),

'volkswagen': dict(accent='#2C5480', models=[
  ('Tiguan', 'suv', 'Compact SUV', []),
  ('Atlas', 'suv-large', 'Three-row SUV', []),
  ('Atlas Cross Sport', 'suv', 'Two-row mid-size SUV', []),
  ('Taos', 'suv', 'Subcompact SUV', []),
  ('Jetta', 'sedan', 'Compact sedan', []),
  ('Golf GTI', 'hatch', 'Performance hatchback', ['perf']),
  ('ID.4', 'suv', 'Electric SUV', ['ev']),
]),

'porsche': dict(accent='#6B4A2E', models=[
  ('911', 'sports', 'Sports car', ['perf', 'lux', 'value']),
  ('718 Cayman', 'sports', 'Sports car', ['perf', 'lux']),
  ('Cayenne', 'suv', 'Luxury performance SUV', ['lux', 'perf']),
  ('Macan', 'suv', 'Compact luxury SUV', ['lux', 'perf']),
  ('Panamera', 'sedan', 'Luxury performance sedan', ['lux', 'perf']),
  ('Taycan', 'sedan', 'Electric performance sedan', ['ev', 'perf', 'lux']),
]),

# ============================== European ==============================
'volvo': dict(accent='#33506B', models=[
  ('XC90', 'suv-large', 'Three-row luxury SUV', ['lux']),
  ('XC60', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('XC40', 'suv', 'Compact luxury SUV', ['lux']),
  ('S60', 'sedan', 'Compact luxury sedan', ['lux']),
  ('V60', 'wagon', 'Luxury wagon', ['lux']),
  ('EX30', 'suv', 'Electric compact SUV', ['ev', 'lux']),
  ('EX90', 'suv-large', 'Electric three-row SUV', ['ev', 'lux']),
]),

'polestar': dict(accent='#41586B', models=[
  ('Polestar 2', 'hatch', 'Electric fastback', ['ev', 'lux']),
  ('Polestar 3', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
  ('Polestar 4', 'suv', 'Electric luxury SUV', ['ev', 'lux', 'perf']),
]),

'land-rover': dict(accent='#3F5644', models=[
  ('Range Rover', 'suv-large', 'Full-size luxury SUV', ['lux', 'offroad']),
  ('Range Rover Sport', 'suv', 'Luxury performance SUV', ['lux', 'offroad', 'perf']),
  ('Range Rover Velar', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('Range Rover Evoque', 'suv', 'Compact luxury SUV', ['lux']),
  ('Defender', 'suv', 'Off-road luxury SUV', ['lux', 'offroad']),
  ('Discovery', 'suv', 'Three-row luxury SUV', ['lux', 'offroad']),
  ('Discovery Sport', 'suv', 'Compact luxury SUV', ['lux']),
]),

'jaguar': dict(accent='#4B5D50', models=[
  ('F-PACE', 'suv', 'Mid-size luxury SUV', ['lux']),
  ('E-PACE', 'suv', 'Compact luxury SUV', ['lux']),
  ('I-PACE', 'suv', 'Electric luxury SUV', ['ev', 'lux']),
  ('XF', 'sedan', 'Luxury sedan', ['lux']),
  ('F-TYPE', 'sports', 'Sports car', ['perf', 'lux']),
]),

'mini': dict(accent='#7A3340', models=[
  ('Cooper', 'hatch', 'Compact hatchback', ['perf']),
  ('Countryman', 'suv', 'Subcompact SUV', []),
  ('Clubman', 'wagon', 'Compact wagon', []),
  ('Convertible', 'sports', 'Convertible', ['perf']),
]),

'alfa-romeo': dict(accent='#8A2634', models=[
  ('Giulia', 'sedan', 'Luxury sport sedan', ['lux', 'perf']),
  ('Stelvio', 'suv', 'Luxury performance SUV', ['lux', 'perf']),
  ('Tonale', 'suv', 'Compact luxury SUV', ['lux']),
]),

'maserati': dict(accent='#3E4A6B', models=[
  ('Grecale', 'suv', 'Compact luxury SUV', ['lux', 'perf']),
  ('Levante', 'suv', 'Mid-size luxury SUV', ['lux', 'perf']),
  ('Ghibli', 'sedan', 'Luxury sport sedan', ['lux', 'perf']),
  ('Quattroporte', 'sedan', 'Full-size luxury sedan', ['lux']),
  ('GranTurismo', 'sports', 'Luxury grand tourer', ['lux', 'perf']),
  ('MC20', 'sports', 'Mid-engine sports car', ['perf', 'lux']),
]),

'fiat': dict(accent='#7A3A2E', models=[
  ('500e', 'hatch', 'Electric city car', ['ev']),
  ('500X', 'suv', 'Subcompact SUV', []),
  ('124 Spider', 'sports', 'Roadster', ['perf', 'old']),
]),

'ferrari': dict(accent='#8E2321', models=[
  ('296', 'sports', 'Mid-engine sports car', ['perf', 'lux']),
  ('SF90', 'sports', 'Hybrid supercar', ['perf', 'lux']),
  ('Roma', 'sports', 'Grand tourer', ['perf', 'lux']),
  ('Purosangue', 'suv', 'Four-door performance vehicle', ['perf', 'lux']),
]),

'lamborghini': dict(accent='#8A6A1F', models=[
  ('Urus', 'suv', 'Performance SUV', ['perf', 'lux']),
  ('Huracan', 'sports', 'Mid-engine sports car', ['perf', 'lux']),
  ('Revuelto', 'sports', 'Hybrid supercar', ['perf', 'lux']),
]),

'bentley': dict(accent='#3D5245', models=[
  ('Bentayga', 'suv-large', 'Luxury SUV', ['lux']),
  ('Continental GT', 'sports', 'Luxury grand tourer', ['lux', 'perf']),
  ('Flying Spur', 'sedan', 'Full-size luxury sedan', ['lux']),
]),

'rolls-royce': dict(accent='#3B4560', models=[
  ('Cullinan', 'suv-large', 'Ultra-luxury SUV', ['lux']),
  ('Ghost', 'sedan', 'Ultra-luxury sedan', ['lux']),
  ('Phantom', 'sedan', 'Flagship ultra-luxury sedan', ['lux']),
  ('Spectre', 'sports', 'Electric ultra-luxury coupe', ['ev', 'lux']),
]),

'aston-martin': dict(accent='#31584F', models=[
  ('DB12', 'sports', 'Grand tourer', ['lux', 'perf']),
  ('Vantage', 'sports', 'Sports car', ['perf', 'lux']),
  ('DBX', 'suv', 'Luxury performance SUV', ['lux', 'perf']),
]),

'mclaren': dict(accent='#8A5A1E', models=[
  ('Artura', 'sports', 'Hybrid supercar', ['perf', 'lux']),
  ('750S', 'sports', 'Mid-engine supercar', ['perf', 'lux']),
  ('GT', 'sports', 'Grand tourer', ['perf', 'lux']),
]),

'lotus': dict(accent='#4E6B3A', models=[
  ('Emira', 'sports', 'Mid-engine sports car', ['perf']),
  ('Eletre', 'suv', 'Electric performance SUV', ['ev', 'perf', 'lux']),
  ('Evora', 'sports', 'Sports car', ['perf', 'old']),
]),

'vinfast': dict(accent='#2F6070', models=[
  ('VF 8', 'suv', 'Electric SUV', ['ev']),
  ('VF 9', 'suv-large', 'Electric three-row SUV', ['ev']),
]),

# ==================== No longer sold new in the US ====================
'pontiac': dict(accent='#5A6270', models=[
  ('G6', 'sedan', 'Mid-size sedan', ['old']),
  ('Grand Prix', 'sedan', 'Mid-size sedan', ['old']),
  ('G8', 'sedan', 'Performance sedan', ['old', 'perf']),
  ('Vibe', 'hatch', 'Compact hatchback', ['old']),
  ('Torrent', 'suv', 'Mid-size SUV', ['old']),
  ('Solstice', 'sports', 'Roadster', ['old', 'perf']),
]),

'saturn': dict(accent='#5E6875', models=[
  ('Ion', 'sedan', 'Compact sedan', ['old']),
  ('Aura', 'sedan', 'Mid-size sedan', ['old']),
  ('Vue', 'suv', 'Compact SUV', ['old']),
  ('Outlook', 'suv-large', 'Three-row SUV', ['old']),
  ('Sky', 'sports', 'Roadster', ['old', 'perf']),
]),

'mercury': dict(accent='#5B6472', models=[
  ('Grand Marquis', 'sedan', 'Full-size sedan', ['old']),
  ('Milan', 'sedan', 'Mid-size sedan', ['old']),
  ('Sable', 'sedan', 'Mid-size sedan', ['old']),
  ('Mariner', 'suv', 'Compact SUV', ['old']),
  ('Mountaineer', 'suv', 'Mid-size SUV', ['old']),
]),

'oldsmobile': dict(accent='#5C6473', models=[
  ('Alero', 'sedan', 'Compact sedan', ['old']),
  ('Intrigue', 'sedan', 'Mid-size sedan', ['old']),
  ('Aurora', 'sedan', 'Full-size sedan', ['old']),
  ('Bravada', 'suv', 'Mid-size SUV', ['old']),
  ('Silhouette', 'minivan', 'Minivan', ['old']),
]),

'hummer': dict(accent='#6B6A45', models=[
  ('H2', 'suv-large', 'Full-size off-road SUV', ['old', 'offroad']),
  ('H3', 'suv', 'Mid-size off-road SUV', ['old', 'offroad']),
  ('H3T', 'truck', 'Mid-size off-road pickup', ['old', 'offroad']),
  ('H1', 'suv-large', 'Full-size off-road SUV', ['old', 'offroad']),
]),

'scion': dict(accent='#4F5A66', models=[
  ('tC', 'sports', 'Sport coupe', ['old']),
  ('xB', 'hatch', 'Compact hatchback', ['old']),
  ('xD', 'hatch', 'Subcompact hatchback', ['old']),
  ('FR-S', 'sports', 'Sports car', ['old', 'perf']),
  ('iA', 'sedan', 'Subcompact sedan', ['old']),
]),

'suzuki': dict(accent='#5E6A78', models=[
  ('Grand Vitara', 'suv', 'Compact SUV', ['old', 'offroad']),
  ('SX4', 'hatch', 'Compact hatchback', ['old']),
  ('Kizashi', 'sedan', 'Mid-size sedan', ['old']),
  ('Forenza', 'sedan', 'Compact sedan', ['old']),
  ('Equator', 'truck', 'Mid-size pickup', ['old', 'work']),
]),

'isuzu': dict(accent='#5A6668', models=[
  ('Rodeo', 'suv', 'Mid-size SUV', ['old', 'offroad']),
  ('Trooper', 'suv', 'Full-size SUV', ['old', 'offroad']),
  ('Ascender', 'suv', 'Mid-size SUV', ['old']),
  ('Amigo', 'suv', 'Compact SUV', ['old', 'offroad']),
  ('i-Series', 'truck', 'Mid-size pickup', ['old', 'work']),
]),

'saab': dict(accent='#3F5A6B', models=[
  ('9-3', 'sedan', 'Compact luxury sedan', ['old', 'perf']),
  ('9-5', 'sedan', 'Mid-size luxury sedan', ['old']),
  ('9-7X', 'suv', 'Mid-size SUV', ['old']),
  ('9-2X', 'wagon', 'Compact wagon', ['old']),
]),

'plymouth': dict(accent='#5C6675', models=[
  ('Voyager', 'minivan', 'Minivan', ['old']),
  ('Grand Voyager', 'minivan', 'Extended minivan', ['old']),
  ('Neon', 'sedan', 'Compact sedan', ['old']),
  ('Breeze', 'sedan', 'Mid-size sedan', ['old']),
  ('Prowler', 'sports', 'Retro roadster', ['old', 'perf']),
]),

'geo': dict(accent='#5A6A6E', models=[
  ('Metro', 'hatch', 'Subcompact hatchback', ['old']),
  ('Prizm', 'sedan', 'Compact sedan', ['old']),
  ('Tracker', 'suv', 'Compact SUV', ['old', 'offroad']),
  ('Storm', 'sports', 'Sport coupe', ['old']),
]),

'eagle': dict(accent='#5E6672', models=[
  ('Talon', 'sports', 'Sport coupe', ['old', 'perf']),
  ('Vision', 'sedan', 'Full-size sedan', ['old']),
  ('Summit', 'sedan', 'Compact sedan', ['old']),
  ('Premier', 'sedan', 'Mid-size sedan', ['old']),
]),

'daewoo': dict(accent='#5B6773', models=[
  ('Lanos', 'sedan', 'Subcompact sedan', ['old']),
  ('Nubira', 'sedan', 'Compact sedan', ['old']),
  ('Leganza', 'sedan', 'Mid-size sedan', ['old']),
]),

'smart': dict(accent='#5A6470', models=[
  ('fortwo', 'hatch', 'Two-seat city car', ['old']),
  ('fortwo cabrio', 'sports', 'Two-seat convertible', ['old']),
]),
}

# --------------------------------------------------------------- coverage ---
# What a model's body style and flags actually change about a policy. These are
# coverage mechanics, not prices — every line here is true of the coverage
# itself, not a claim about what anybody pays.

BODY_POINTS = {
  'truck':   ['Liability, collision and comprehensive',
              'Anything permanently mounted &mdash; racks, toolboxes, a bed liner &mdash; needs listing',
              'A lender will require collision and comprehensive while it is financed'],
  'van':     ['Liability, collision and comprehensive',
              'Personal or business use is the question that decides which policy it belongs on',
              'Shelving, racks and equipment are not covered by default'],
  'minivan': ['Liability, collision and comprehensive',
              'Everyone in the household who drives it has to be on the policy',
              'A lender will require collision and comprehensive while it is financed'],
  'suv-large': ['Liability, collision and comprehensive',
              'Higher limits are worth pricing &mdash; a heavier vehicle does more damage in a collision',
              'A lender will require collision and comprehensive while it is financed'],
  'suv':     ['Liability, collision and comprehensive',
              'Uninsured and underinsured motorist coverage',
              'A lender will require collision and comprehensive while it is financed'],
  'sedan':   ['Liability, collision and comprehensive',
              'Uninsured and underinsured motorist coverage',
              'A lender will require collision and comprehensive while it is financed'],
  'hatch':   ['Liability, collision and comprehensive',
              'Uninsured and underinsured motorist coverage',
              'If it is paid off, whether collision still earns its place'],
  'wagon':   ['Liability, collision and comprehensive',
              'Uninsured and underinsured motorist coverage',
              'A lender will require collision and comprehensive while it is financed'],
  'sports':  ['Liability, collision and comprehensive',
              'Rated on the engine and trim, not on the badge',
              'Agreed value is worth asking about if it is not an everyday car'],
}

FLAG_POINTS = {
  'ev':      'Battery and high-voltage components &mdash; ask how a battery claim is handled',
  'perf':    'Performance trims are rated separately from the base model',
  'offroad': 'Lifts, tyres, bumpers and winches have to be declared to be covered',
  'work':    'If it carries anything for pay, a personal policy may not answer the claim',
  'lux':     'Certified repair networks and calibration after a sensor replacement',
  'value':   'Holds value well, which keeps collision worth carrying for longer',
  'old':     'Worth checking whether collision still earns its premium at this age',
}

def get(slug):
    return L.get(slug)

def models(slug):
    d = L.get(slug)
    return d['models'] if d else []

def accent(slug):
    d = L.get(slug)
    return d['accent'] if d else '#2F4E6E'

def dominant_body(slug):
    """The body style the brand mostly sells — drives the hero illustration."""
    ms = models(slug)
    if not ms:
        return 'suv'
    counts = {}
    for _, body, _, _ in ms:
        counts[body] = counts.get(body, 0) + 1
    return max(counts, key=lambda k: (counts[k], -[m[1] for m in ms].index(k)))

def body_mix(slug):
    """Rough shape of the lineup, for copy that describes the brand honestly."""
    ms = models(slug)
    out = {}
    for _, body, _, _ in ms:
        k = ('truck' if body == 'truck' else
             'van' if body in ('van', 'minivan') else
             'suv' if body in ('suv', 'suv-large') else
             'sports' if body == 'sports' else 'car')
        out[k] = out.get(k, 0) + 1
    return out

def flag_set(slug):
    out = set()
    for _, _, _, fl in models(slug):
        out.update(fl)
    return out
