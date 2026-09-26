"""Model lineups per make, and the brand-specific angle each page argues.

This file is what stops the brand pages being one article with the name
swapped. The model list is real and different for every make, and the flags on
each model drive which coverage points that model's card shows — a Wrangler
raises modifications, an F-150 raises business use, a Model Y raises the
approved repair network. None of that is written 60 times; it is derived.

Model rows are (name, body, label, flags).

  body   — one of the shapes in vehiclesvg.BODY_SHAPE
  label  — what the card shows under the name ("Full-size pickup"), as a key:
           the words are makes.labels.<key> in locales/<lang>/makes.json, and
           models() hands them back in the language being rendered. Model
           names are proper nouns and stay here, the same in both languages.
  flags  — 'ev', 'perf', 'offroad', 'work', 'lux', 'value', 'old'

What is deliberately NOT in here: model years, prices, premiums, repair costs,
MPG, theft rankings. Lineups shift year to year and a stale model year on a
page is a small lie; the pages say what a model IS, not what it costs.

`accent` is a tasteful page tint chosen to sit well with the brand. It is not
a logo color and no manufacturer mark is used anywhere on these pages.
"""
import i18n

# ---------------------------------------------------------------- lineups ---
L = {

# ============================== American ==============================
'ford': dict(accent='#1B4C8C', models=[
  ('F-150', 'truck', 'full-size-pickup', ['work', 'value']),
  ('Super Duty', 'truck', 'heavy-duty-pickup', ['work']),
  ('Ranger', 'truck', 'mid-size-pickup', ['work']),
  ('Maverick', 'truck', 'compact-pickup', ['work']),
  ('Bronco', 'suv', 'off-road-suv', ['offroad']),
  ('Bronco Sport', 'suv', 'compact-suv', []),
  ('Explorer', 'suv', 'three-row-suv', []),
  ('Expedition', 'suv-large', 'full-size-suv', []),
  ('Escape', 'suv', 'compact-suv', []),
  ('Mustang', 'sports', 'sports-car', ['perf']),
  ('Mustang Mach-E', 'suv', 'electric-suv', ['ev']),
  ('Edge', 'suv', 'mid-size-suv', []),
  ('Transit', 'van', 'cargo-and-passenger-van', ['work']),
]),

'chevrolet': dict(accent='#B8892A', models=[
  ('Silverado', 'truck', 'full-size-pickup', ['work', 'value']),
  ('Colorado', 'truck', 'mid-size-pickup', ['work']),
  ('Tahoe', 'suv-large', 'full-size-suv', []),
  ('Suburban', 'suv-large', 'extended-full-size-suv', []),
  ('Traverse', 'suv', 'three-row-suv', []),
  ('Equinox', 'suv', 'compact-suv', []),
  ('Blazer', 'suv', 'mid-size-suv', []),
  ('Trailblazer', 'suv', 'subcompact-suv', []),
  ('Trax', 'suv', 'subcompact-suv', []),
  ('Malibu', 'sedan', 'mid-size-sedan', []),
  ('Camaro', 'sports', 'sports-car', ['perf']),
  ('Corvette', 'sports', 'sports-car', ['perf', 'value']),
  ('Equinox EV', 'suv', 'electric-suv', ['ev']),
  ('Blazer EV', 'suv', 'electric-suv', ['ev']),
  ('Silverado EV', 'truck', 'electric-pickup', ['ev', 'work']),
  ('Express', 'van', 'cargo-and-passenger-van', ['work']),
]),

'gmc': dict(accent='#8C2F39', models=[
  ('Sierra', 'truck', 'full-size-pickup', ['work', 'value']),
  ('Sierra HD', 'truck', 'heavy-duty-pickup', ['work']),
  ('Canyon', 'truck', 'mid-size-pickup', ['work']),
  ('Yukon', 'suv-large', 'full-size-suv', ['lux']),
  ('Yukon XL', 'suv-large', 'extended-full-size-suv', ['lux']),
  ('Acadia', 'suv', 'three-row-suv', []),
  ('Terrain', 'suv', 'compact-suv', []),
  ('Hummer EV', 'truck', 'electric-pickup', ['ev', 'offroad']),
  ('Sierra EV', 'truck', 'electric-pickup', ['ev', 'work']),
  ('Savana', 'van', 'cargo-and-passenger-van', ['work']),
]),

'ram': dict(accent='#7A2E2E', models=[
  ('1500', 'truck', 'full-size-pickup', ['work', 'value']),
  ('2500', 'truck', 'heavy-duty-pickup', ['work']),
  ('3500', 'truck', 'heavy-duty-pickup', ['work']),
  ('ProMaster', 'van', 'cargo-van', ['work']),
]),

'jeep': dict(accent='#3E5C3A', models=[
  ('Wrangler', 'suv', 'off-road-suv', ['offroad', 'value']),
  ('Gladiator', 'truck', 'off-road-pickup', ['offroad', 'work']),
  ('Grand Cherokee', 'suv', 'mid-size-suv', []),
  ('Cherokee', 'suv', 'mid-size-suv', []),
  ('Compass', 'suv', 'compact-suv', []),
  ('Renegade', 'suv', 'subcompact-suv', []),
  ('Wagoneer', 'suv-large', 'full-size-suv', ['lux']),
  ('Grand Wagoneer', 'suv-large', 'full-size-luxury-suv', ['lux']),
]),

'dodge': dict(accent='#8A2331', models=[
  ('Charger', 'sedan', 'performance-sedan', ['perf']),
  ('Challenger', 'sports', 'muscle-coupe', ['perf']),
  ('Durango', 'suv', 'three-row-suv', ['perf']),
  ('Hornet', 'suv', 'compact-suv', []),
  ('Journey', 'suv', 'mid-size-suv', ['old']),
  ('Grand Caravan', 'minivan', 'minivan', ['old']),
]),

'chrysler': dict(accent='#2F4E6E', models=[
  ('Pacifica', 'minivan', 'minivan', []),
  ('Voyager', 'minivan', 'minivan', []),
  ('300', 'sedan', 'full-size-sedan', ['old']),
  ('Town & Country', 'minivan', 'minivan', ['old']),
]),

'cadillac': dict(accent='#6E2639', models=[
  ('Escalade', 'suv-large', 'full-size-luxury-suv', ['lux']),
  ('XT6', 'suv', 'three-row-luxury-suv', ['lux']),
  ('XT5', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('XT4', 'suv', 'compact-luxury-suv', ['lux']),
  ('CT5', 'sedan', 'luxury-sedan', ['lux', 'perf']),
  ('CT4', 'sedan', 'compact-luxury-sedan', ['lux', 'perf']),
  ('LYRIQ', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
]),

'buick': dict(accent='#7A2C3E', models=[
  ('Envista', 'suv', 'compact-suv', []),
  ('Encore GX', 'suv', 'subcompact-suv', []),
  ('Envision', 'suv', 'compact-suv', []),
  ('Enclave', 'suv-large', 'three-row-suv', ['lux']),
]),

'lincoln': dict(accent='#354A66', models=[
  ('Navigator', 'suv-large', 'full-size-luxury-suv', ['lux']),
  ('Aviator', 'suv', 'three-row-luxury-suv', ['lux']),
  ('Nautilus', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('Corsair', 'suv', 'compact-luxury-suv', ['lux']),
]),

'tesla': dict(accent='#8E2A2A', models=[
  ('Model 3', 'sedan', 'electric-sedan', ['ev']),
  ('Model Y', 'suv', 'electric-suv', ['ev']),
  ('Model S', 'sedan', 'electric-luxury-sedan', ['ev', 'lux', 'perf']),
  ('Model X', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
  ('Cybertruck', 'truck', 'electric-pickup', ['ev', 'work']),
]),

'rivian': dict(accent='#3F6152', models=[
  ('R1T', 'truck', 'electric-pickup', ['ev', 'offroad', 'work']),
  ('R1S', 'suv-large', 'electric-three-row-suv', ['ev', 'offroad']),
]),

'lucid': dict(accent='#4A4E7C', models=[
  ('Air', 'sedan', 'electric-luxury-sedan', ['ev', 'lux', 'perf']),
  ('Gravity', 'suv-large', 'electric-three-row-suv', ['ev', 'lux']),
]),

# ============================== Japanese ==============================
'toyota': dict(accent='#9A2B2B', models=[
  ('RAV4', 'suv', 'compact-suv', ['value']),
  ('Camry', 'sedan', 'mid-size-sedan', ['value']),
  ('Corolla', 'sedan', 'compact-sedan', ['value']),
  ('Tacoma', 'truck', 'mid-size-pickup', ['work', 'value']),
  ('Tundra', 'truck', 'full-size-pickup', ['work']),
  ('Highlander', 'suv', 'three-row-suv', []),
  ('Grand Highlander', 'suv-large', 'three-row-suv', []),
  ('4Runner', 'suv', 'off-road-suv', ['offroad', 'value']),
  ('Sequoia', 'suv-large', 'full-size-suv', []),
  ('Land Cruiser', 'suv', 'off-road-suv', ['offroad', 'value']),
  ('Sienna', 'minivan', 'minivan', []),
  ('Prius', 'hatch', 'hybrid-hatchback', []),
  ('Corolla Cross', 'suv', 'subcompact-suv', []),
  ('bZ4X', 'suv', 'electric-suv', ['ev']),
  ('GR Supra', 'sports', 'sports-car', ['perf']),
]),

'honda': dict(accent='#8C2727', models=[
  ('CR-V', 'suv', 'compact-suv', ['value']),
  ('Civic', 'sedan', 'compact-sedan', ['value']),
  ('Accord', 'sedan', 'mid-size-sedan', ['value']),
  ('Pilot', 'suv', 'three-row-suv', []),
  ('HR-V', 'suv', 'subcompact-suv', []),
  ('Passport', 'suv', 'mid-size-suv', []),
  ('Odyssey', 'minivan', 'minivan', []),
  ('Ridgeline', 'truck', 'mid-size-pickup', ['work']),
  ('Prologue', 'suv', 'electric-suv', ['ev']),
]),

'nissan': dict(accent='#8A2E38', models=[
  ('Rogue', 'suv', 'compact-suv', []),
  ('Altima', 'sedan', 'mid-size-sedan', []),
  ('Sentra', 'sedan', 'compact-sedan', []),
  ('Versa', 'sedan', 'subcompact-sedan', []),
  ('Kicks', 'suv', 'subcompact-suv', []),
  ('Murano', 'suv', 'mid-size-suv', []),
  ('Pathfinder', 'suv', 'three-row-suv', []),
  ('Armada', 'suv-large', 'full-size-suv', []),
  ('Frontier', 'truck', 'mid-size-pickup', ['work']),
  ('Titan', 'truck', 'full-size-pickup', ['work']),
  ('Maxima', 'sedan', 'full-size-sedan', ['old']),
  ('Leaf', 'hatch', 'electric-hatchback', ['ev']),
  ('Ariya', 'suv', 'electric-suv', ['ev']),
  ('Z', 'sports', 'sports-car', ['perf']),
  ('GT-R', 'sports', 'high-performance-sports-car', ['perf']),
]),

'mazda': dict(accent='#7B2B3B', models=[
  ('CX-5', 'suv', 'compact-suv', []),
  ('CX-50', 'suv', 'compact-suv', ['offroad']),
  ('CX-30', 'suv', 'subcompact-suv', []),
  ('CX-70', 'suv', 'two-row-mid-size-suv', ['lux']),
  ('CX-90', 'suv-large', 'three-row-suv', ['lux']),
  ('Mazda3', 'sedan', 'compact-sedan-and-hatchback', []),
  ('MX-5 Miata', 'sports', 'roadster', ['perf']),
]),

'subaru': dict(accent='#2F4C7A', models=[
  ('Outback', 'wagon', 'all-wheel-drive-wagon', ['offroad', 'value']),
  ('Forester', 'suv', 'compact-suv', ['value']),
  ('Crosstrek', 'suv', 'subcompact-suv', ['offroad', 'value']),
  ('Ascent', 'suv', 'three-row-suv', []),
  ('Impreza', 'hatch', 'compact-hatchback', []),
  ('Legacy', 'sedan', 'mid-size-sedan', []),
  ('WRX', 'sedan', 'performance-sedan', ['perf']),
  ('BRZ', 'sports', 'sports-car', ['perf']),
  ('Solterra', 'suv', 'electric-suv', ['ev']),
]),

'mitsubishi': dict(accent='#8A2A2A', models=[
  ('Outlander', 'suv', 'compact-suv', []),
  ('Outlander Sport', 'suv', 'subcompact-suv', []),
  ('Eclipse Cross', 'suv', 'subcompact-suv', []),
  ('Mirage', 'hatch', 'subcompact-hatchback', []),
]),

'lexus': dict(accent='#4C4F5C', models=[
  ('RX', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('NX', 'suv', 'compact-luxury-suv', ['lux']),
  ('TX', 'suv-large', 'three-row-luxury-suv', ['lux']),
  ('GX', 'suv', 'off-road-luxury-suv', ['lux', 'offroad', 'value']),
  ('LX', 'suv-large', 'full-size-luxury-suv', ['lux', 'offroad']),
  ('UX', 'suv', 'subcompact-luxury-suv', ['lux']),
  ('ES', 'sedan', 'luxury-sedan', ['lux']),
  ('IS', 'sedan', 'compact-luxury-sedan', ['lux', 'perf']),
  ('LS', 'sedan', 'full-size-luxury-sedan', ['lux']),
  ('RZ', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
]),

'acura': dict(accent='#3C4F63', models=[
  ('MDX', 'suv', 'three-row-luxury-suv', ['lux']),
  ('RDX', 'suv', 'compact-luxury-suv', ['lux']),
  ('Integra', 'hatch', 'sport-compact', ['perf']),
  ('TLX', 'sedan', 'luxury-sedan', ['lux', 'perf']),
  ('ZDX', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
]),

'infiniti': dict(accent='#4A5570', models=[
  ('QX60', 'suv', 'three-row-luxury-suv', ['lux']),
  ('QX80', 'suv-large', 'full-size-luxury-suv', ['lux']),
  ('QX50', 'suv', 'compact-luxury-suv', ['lux']),
  ('QX55', 'suv', 'coupe-style-luxury-suv', ['lux']),
  ('Q50', 'sedan', 'luxury-sport-sedan', ['lux', 'perf']),
]),

# ============================== Korean ==============================
'hyundai': dict(accent='#2E5A7A', models=[
  ('Tucson', 'suv', 'compact-suv', []),
  ('Santa Fe', 'suv', 'mid-size-suv', []),
  ('Palisade', 'suv-large', 'three-row-suv', []),
  ('Kona', 'suv', 'subcompact-suv', []),
  ('Venue', 'suv', 'subcompact-suv', []),
  ('Elantra', 'sedan', 'compact-sedan', []),
  ('Sonata', 'sedan', 'mid-size-sedan', []),
  ('Santa Cruz', 'truck', 'compact-pickup', ['work']),
  ('IONIQ 5', 'suv', 'electric-suv', ['ev']),
  ('IONIQ 6', 'sedan', 'electric-sedan', ['ev']),
]),

'kia': dict(accent='#7B2F3F', models=[
  ('Sportage', 'suv', 'compact-suv', []),
  ('Sorento', 'suv', 'three-row-suv', []),
  ('Telluride', 'suv-large', 'three-row-suv', []),
  ('Seltos', 'suv', 'subcompact-suv', []),
  ('Soul', 'hatch', 'compact-hatchback', []),
  ('Forte', 'sedan', 'compact-sedan', []),
  ('K4', 'sedan', 'compact-sedan', []),
  ('K5', 'sedan', 'mid-size-sedan', []),
  ('Carnival', 'minivan', 'minivan', []),
  ('Niro', 'suv', 'hybrid-and-electric-crossover', ['ev']),
  ('EV6', 'suv', 'electric-suv', ['ev']),
  ('EV9', 'suv-large', 'electric-three-row-suv', ['ev']),
]),

'genesis': dict(accent='#5A4A63', models=[
  ('GV70', 'suv', 'compact-luxury-suv', ['lux']),
  ('GV80', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('GV60', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
  ('G70', 'sedan', 'compact-luxury-sedan', ['lux', 'perf']),
  ('G80', 'sedan', 'luxury-sedan', ['lux']),
  ('G90', 'sedan', 'full-size-luxury-sedan', ['lux']),
]),

# ============================== German ==============================
'bmw': dict(accent='#2B5580', models=[
  ('3 Series', 'sedan', 'compact-luxury-sedan', ['lux']),
  ('5 Series', 'sedan', 'mid-size-luxury-sedan', ['lux']),
  ('7 Series', 'sedan', 'full-size-luxury-sedan', ['lux']),
  ('X1', 'suv', 'subcompact-luxury-suv', ['lux']),
  ('X3', 'suv', 'compact-luxury-suv', ['lux']),
  ('X5', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('X7', 'suv-large', 'full-size-luxury-suv', ['lux']),
  ('4 Series', 'sports', 'luxury-coupe-and-convertible', ['lux', 'perf']),
  ('M3', 'sedan', 'high-performance-sedan', ['perf', 'lux']),
  ('Z4', 'sports', 'roadster', ['perf']),
  ('i4', 'sedan', 'electric-sedan', ['ev', 'lux']),
  ('iX', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
]),

'mercedes-benz': dict(accent='#4A5560', models=[
  ('C-Class', 'sedan', 'compact-luxury-sedan', ['lux']),
  ('E-Class', 'sedan', 'mid-size-luxury-sedan', ['lux']),
  ('S-Class', 'sedan', 'full-size-luxury-sedan', ['lux']),
  ('GLA', 'suv', 'subcompact-luxury-suv', ['lux']),
  ('GLB', 'suv', 'compact-luxury-suv', ['lux']),
  ('GLC', 'suv', 'compact-luxury-suv', ['lux']),
  ('GLE', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('GLS', 'suv-large', 'full-size-luxury-suv', ['lux']),
  ('G-Class', 'suv', 'off-road-luxury-suv', ['lux', 'offroad', 'value']),
  ('EQE', 'sedan', 'electric-luxury-sedan', ['ev', 'lux']),
  ('EQS', 'sedan', 'electric-flagship-sedan', ['ev', 'lux']),
  ('AMG GT', 'sports', 'high-performance-sports-car', ['perf', 'lux']),
  ('Sprinter', 'van', 'cargo-and-passenger-van', ['work']),
]),

'audi': dict(accent='#6E3540', models=[
  ('A3', 'sedan', 'compact-luxury-sedan', ['lux']),
  ('A4', 'sedan', 'compact-luxury-sedan', ['lux']),
  ('A5', 'sports', 'luxury-coupe-and-sportback', ['lux']),
  ('A6', 'sedan', 'mid-size-luxury-sedan', ['lux']),
  ('Q3', 'suv', 'subcompact-luxury-suv', ['lux']),
  ('Q5', 'suv', 'compact-luxury-suv', ['lux']),
  ('Q7', 'suv-large', 'three-row-luxury-suv', ['lux']),
  ('Q8', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('Q4 e-tron', 'suv', 'electric-suv', ['ev', 'lux']),
  ('e-tron GT', 'sedan', 'electric-performance-sedan', ['ev', 'perf', 'lux']),
]),

'volkswagen': dict(accent='#2C5480', models=[
  ('Tiguan', 'suv', 'compact-suv', []),
  ('Atlas', 'suv-large', 'three-row-suv', []),
  ('Atlas Cross Sport', 'suv', 'two-row-mid-size-suv', []),
  ('Taos', 'suv', 'subcompact-suv', []),
  ('Jetta', 'sedan', 'compact-sedan', []),
  ('Golf GTI', 'hatch', 'performance-hatchback', ['perf']),
  ('ID.4', 'suv', 'electric-suv', ['ev']),
]),

'porsche': dict(accent='#6B4A2E', models=[
  ('911', 'sports', 'sports-car', ['perf', 'lux', 'value']),
  ('718 Cayman', 'sports', 'sports-car', ['perf', 'lux']),
  ('Cayenne', 'suv', 'luxury-performance-suv', ['lux', 'perf']),
  ('Macan', 'suv', 'compact-luxury-suv', ['lux', 'perf']),
  ('Panamera', 'sedan', 'luxury-performance-sedan', ['lux', 'perf']),
  ('Taycan', 'sedan', 'electric-performance-sedan', ['ev', 'perf', 'lux']),
]),

# ============================== European ==============================
'volvo': dict(accent='#33506B', models=[
  ('XC90', 'suv-large', 'three-row-luxury-suv', ['lux']),
  ('XC60', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('XC40', 'suv', 'compact-luxury-suv', ['lux']),
  ('S60', 'sedan', 'compact-luxury-sedan', ['lux']),
  ('V60', 'wagon', 'luxury-wagon', ['lux']),
  ('EX30', 'suv', 'electric-compact-suv', ['ev', 'lux']),
  ('EX90', 'suv-large', 'electric-three-row-suv', ['ev', 'lux']),
]),

'polestar': dict(accent='#41586B', models=[
  ('Polestar 2', 'hatch', 'electric-fastback', ['ev', 'lux']),
  ('Polestar 3', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
  ('Polestar 4', 'suv', 'electric-luxury-suv', ['ev', 'lux', 'perf']),
]),

'land-rover': dict(accent='#3F5644', models=[
  ('Range Rover', 'suv-large', 'full-size-luxury-suv', ['lux', 'offroad']),
  ('Range Rover Sport', 'suv', 'luxury-performance-suv', ['lux', 'offroad', 'perf']),
  ('Range Rover Velar', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('Range Rover Evoque', 'suv', 'compact-luxury-suv', ['lux']),
  ('Defender', 'suv', 'off-road-luxury-suv', ['lux', 'offroad']),
  ('Discovery', 'suv', 'three-row-luxury-suv', ['lux', 'offroad']),
  ('Discovery Sport', 'suv', 'compact-luxury-suv', ['lux']),
]),

'jaguar': dict(accent='#4B5D50', models=[
  ('F-PACE', 'suv', 'mid-size-luxury-suv', ['lux']),
  ('E-PACE', 'suv', 'compact-luxury-suv', ['lux']),
  ('I-PACE', 'suv', 'electric-luxury-suv', ['ev', 'lux']),
  ('XF', 'sedan', 'luxury-sedan', ['lux']),
  ('F-TYPE', 'sports', 'sports-car', ['perf', 'lux']),
]),

'mini': dict(accent='#7A3340', models=[
  ('Cooper', 'hatch', 'compact-hatchback', ['perf']),
  ('Countryman', 'suv', 'subcompact-suv', []),
  ('Clubman', 'wagon', 'compact-wagon', []),
  ('Convertible', 'sports', 'convertible', ['perf']),
]),

'alfa-romeo': dict(accent='#8A2634', models=[
  ('Giulia', 'sedan', 'luxury-sport-sedan', ['lux', 'perf']),
  ('Stelvio', 'suv', 'luxury-performance-suv', ['lux', 'perf']),
  ('Tonale', 'suv', 'compact-luxury-suv', ['lux']),
]),

'maserati': dict(accent='#3E4A6B', models=[
  ('Grecale', 'suv', 'compact-luxury-suv', ['lux', 'perf']),
  ('Levante', 'suv', 'mid-size-luxury-suv', ['lux', 'perf']),
  ('Ghibli', 'sedan', 'luxury-sport-sedan', ['lux', 'perf']),
  ('Quattroporte', 'sedan', 'full-size-luxury-sedan', ['lux']),
  ('GranTurismo', 'sports', 'luxury-grand-tourer', ['lux', 'perf']),
  ('MC20', 'sports', 'mid-engine-sports-car', ['perf', 'lux']),
]),

'fiat': dict(accent='#7A3A2E', models=[
  ('500e', 'hatch', 'electric-city-car', ['ev']),
  ('500X', 'suv', 'subcompact-suv', []),
  ('124 Spider', 'sports', 'roadster', ['perf', 'old']),
]),

'ferrari': dict(accent='#8E2321', models=[
  ('296', 'sports', 'mid-engine-sports-car', ['perf', 'lux']),
  ('SF90', 'sports', 'hybrid-supercar', ['perf', 'lux']),
  ('Roma', 'sports', 'grand-tourer', ['perf', 'lux']),
  ('Purosangue', 'suv', 'four-door-performance-vehicle', ['perf', 'lux']),
]),

'lamborghini': dict(accent='#8A6A1F', models=[
  ('Urus', 'suv', 'performance-suv', ['perf', 'lux']),
  ('Huracan', 'sports', 'mid-engine-sports-car', ['perf', 'lux']),
  ('Revuelto', 'sports', 'hybrid-supercar', ['perf', 'lux']),
]),

'bentley': dict(accent='#3D5245', models=[
  ('Bentayga', 'suv-large', 'luxury-suv', ['lux']),
  ('Continental GT', 'sports', 'luxury-grand-tourer', ['lux', 'perf']),
  ('Flying Spur', 'sedan', 'full-size-luxury-sedan', ['lux']),
]),

'rolls-royce': dict(accent='#3B4560', models=[
  ('Cullinan', 'suv-large', 'ultra-luxury-suv', ['lux']),
  ('Ghost', 'sedan', 'ultra-luxury-sedan', ['lux']),
  ('Phantom', 'sedan', 'flagship-ultra-luxury-sedan', ['lux']),
  ('Spectre', 'sports', 'electric-ultra-luxury-coupe', ['ev', 'lux']),
]),

'aston-martin': dict(accent='#31584F', models=[
  ('DB12', 'sports', 'grand-tourer', ['lux', 'perf']),
  ('Vantage', 'sports', 'sports-car', ['perf', 'lux']),
  ('DBX', 'suv', 'luxury-performance-suv', ['lux', 'perf']),
]),

'mclaren': dict(accent='#8A5A1E', models=[
  ('Artura', 'sports', 'hybrid-supercar', ['perf', 'lux']),
  ('750S', 'sports', 'mid-engine-supercar', ['perf', 'lux']),
  ('GT', 'sports', 'grand-tourer', ['perf', 'lux']),
]),

'lotus': dict(accent='#4E6B3A', models=[
  ('Emira', 'sports', 'mid-engine-sports-car', ['perf']),
  ('Eletre', 'suv', 'electric-performance-suv', ['ev', 'perf', 'lux']),
  ('Evora', 'sports', 'sports-car', ['perf', 'old']),
]),

'vinfast': dict(accent='#2F6070', models=[
  ('VF 8', 'suv', 'electric-suv', ['ev']),
  ('VF 9', 'suv-large', 'electric-three-row-suv', ['ev']),
]),

# ==================== No longer sold new in the US ====================
'pontiac': dict(accent='#5A6270', models=[
  ('G6', 'sedan', 'mid-size-sedan', ['old']),
  ('Grand Prix', 'sedan', 'mid-size-sedan', ['old']),
  ('G8', 'sedan', 'performance-sedan', ['old', 'perf']),
  ('Vibe', 'hatch', 'compact-hatchback', ['old']),
  ('Torrent', 'suv', 'mid-size-suv', ['old']),
  ('Solstice', 'sports', 'roadster', ['old', 'perf']),
]),

'saturn': dict(accent='#5E6875', models=[
  ('Ion', 'sedan', 'compact-sedan', ['old']),
  ('Aura', 'sedan', 'mid-size-sedan', ['old']),
  ('Vue', 'suv', 'compact-suv', ['old']),
  ('Outlook', 'suv-large', 'three-row-suv', ['old']),
  ('Sky', 'sports', 'roadster', ['old', 'perf']),
]),

'mercury': dict(accent='#5B6472', models=[
  ('Grand Marquis', 'sedan', 'full-size-sedan', ['old']),
  ('Milan', 'sedan', 'mid-size-sedan', ['old']),
  ('Sable', 'sedan', 'mid-size-sedan', ['old']),
  ('Mariner', 'suv', 'compact-suv', ['old']),
  ('Mountaineer', 'suv', 'mid-size-suv', ['old']),
]),

'oldsmobile': dict(accent='#5C6473', models=[
  ('Alero', 'sedan', 'compact-sedan', ['old']),
  ('Intrigue', 'sedan', 'mid-size-sedan', ['old']),
  ('Aurora', 'sedan', 'full-size-sedan', ['old']),
  ('Bravada', 'suv', 'mid-size-suv', ['old']),
  ('Silhouette', 'minivan', 'minivan', ['old']),
]),

'hummer': dict(accent='#6B6A45', models=[
  ('H2', 'suv-large', 'full-size-off-road-suv', ['old', 'offroad']),
  ('H3', 'suv', 'mid-size-off-road-suv', ['old', 'offroad']),
  ('H3T', 'truck', 'mid-size-off-road-pickup', ['old', 'offroad']),
  ('H1', 'suv-large', 'full-size-off-road-suv', ['old', 'offroad']),
]),

'scion': dict(accent='#4F5A66', models=[
  ('tC', 'sports', 'sport-coupe', ['old']),
  ('xB', 'hatch', 'compact-hatchback', ['old']),
  ('xD', 'hatch', 'subcompact-hatchback', ['old']),
  ('FR-S', 'sports', 'sports-car', ['old', 'perf']),
  ('iA', 'sedan', 'subcompact-sedan', ['old']),
]),

'suzuki': dict(accent='#5E6A78', models=[
  ('Grand Vitara', 'suv', 'compact-suv', ['old', 'offroad']),
  ('SX4', 'hatch', 'compact-hatchback', ['old']),
  ('Kizashi', 'sedan', 'mid-size-sedan', ['old']),
  ('Forenza', 'sedan', 'compact-sedan', ['old']),
  ('Equator', 'truck', 'mid-size-pickup', ['old', 'work']),
]),

'isuzu': dict(accent='#5A6668', models=[
  ('Rodeo', 'suv', 'mid-size-suv', ['old', 'offroad']),
  ('Trooper', 'suv', 'full-size-suv', ['old', 'offroad']),
  ('Ascender', 'suv', 'mid-size-suv', ['old']),
  ('Amigo', 'suv', 'compact-suv', ['old', 'offroad']),
  ('i-Series', 'truck', 'mid-size-pickup', ['old', 'work']),
]),

'saab': dict(accent='#3F5A6B', models=[
  ('9-3', 'sedan', 'compact-luxury-sedan', ['old', 'perf']),
  ('9-5', 'sedan', 'mid-size-luxury-sedan', ['old']),
  ('9-7X', 'suv', 'mid-size-suv', ['old']),
  ('9-2X', 'wagon', 'compact-wagon', ['old']),
]),

'plymouth': dict(accent='#5C6675', models=[
  ('Voyager', 'minivan', 'minivan', ['old']),
  ('Grand Voyager', 'minivan', 'extended-minivan', ['old']),
  ('Neon', 'sedan', 'compact-sedan', ['old']),
  ('Breeze', 'sedan', 'mid-size-sedan', ['old']),
  ('Prowler', 'sports', 'retro-roadster', ['old', 'perf']),
]),

'geo': dict(accent='#5A6A6E', models=[
  ('Metro', 'hatch', 'subcompact-hatchback', ['old']),
  ('Prizm', 'sedan', 'compact-sedan', ['old']),
  ('Tracker', 'suv', 'compact-suv', ['old', 'offroad']),
  ('Storm', 'sports', 'sport-coupe', ['old']),
]),

'eagle': dict(accent='#5E6672', models=[
  ('Talon', 'sports', 'sport-coupe', ['old', 'perf']),
  ('Vision', 'sedan', 'full-size-sedan', ['old']),
  ('Summit', 'sedan', 'compact-sedan', ['old']),
  ('Premier', 'sedan', 'mid-size-sedan', ['old']),
]),

'daewoo': dict(accent='#5B6773', models=[
  ('Lanos', 'sedan', 'subcompact-sedan', ['old']),
  ('Nubira', 'sedan', 'compact-sedan', ['old']),
  ('Leganza', 'sedan', 'mid-size-sedan', ['old']),
]),

'smart': dict(accent='#5A6470', models=[
  ('fortwo', 'hatch', 'two-seat-city-car', ['old']),
  ('fortwo cabrio', 'sports', 'two-seat-convertible', ['old']),
]),
}

# --------------------------------------------------------------- coverage ---
# What a model's body style and flags actually change about a policy. These are
# coverage mechanics, not prices — every line here is true of the coverage
# itself, not a claim about what anybody pays.

# The lines themselves — per body style (kit.points.body.<body>) and per flag
# (kit.points.flag.<flag>) — are in locales/<lang>/kit.json, in English and
# Spanish. brandkit.selector() reads them there.

def get(slug):
    return L.get(slug)

def _rows(slug):
    """The lineup as stored: labels still as keys."""
    d = L.get(slug)
    return d['models'] if d else []

def models(slug):
    """(name, body, label, flags) per model, the label in the language being
    rendered — brandkit prints it under the model name as it comes."""
    return [(n, body, i18n.t('makes.labels.' + label), fl) for n, body, label, fl in _rows(slug)]

def accent(slug):
    d = L.get(slug)
    return d['accent'] if d else '#2F4E6E'

def dominant_body(slug):
    """The body style the brand mostly sells — drives the hero illustration."""
    ms = _rows(slug)
    if not ms:
        return 'suv'
    counts = {}
    for _, body, _, _ in ms:
        counts[body] = counts.get(body, 0) + 1
    return max(counts, key=lambda k: (counts[k], -[m[1] for m in ms].index(k)))

def body_mix(slug):
    """Rough shape of the lineup, for copy that describes the brand honestly."""
    ms = _rows(slug)
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
    for _, _, _, fl in _rows(slug):
        out.update(fl)
    return out
