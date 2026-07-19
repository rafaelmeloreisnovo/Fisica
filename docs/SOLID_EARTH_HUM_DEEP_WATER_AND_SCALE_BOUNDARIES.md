# Solid-Earth Hum, Deep Water and Scale Boundaries

**Date:** 2026-07-19  
**State:** executable extension  
**Claim boundary:** `claim_allowed=false`

## 1. Brighton correction

The sculpture outside Churchill Square is **Twins**, by Charlie Hooker. The official record identifies granite, glass, bronze and audio electronics. Sunlight sensors trigger sound derived from local weather patterns recorded in 1997–1998.

Therefore:

```text
Twins = solar/weather-driven sound artwork
Twins != direct solid-Earth vibration detector
```

Architecture can nevertheless reveal or amplify ambient vibration when its own resonant modes couple to ground motion. That is a separate structural-dynamics mechanism and requires accelerometers or seismometers.

## 2. The Earth really vibrates continuously

Three useful bands are kept separate:

```text
secondary microseism candidate: approximately 3–12 s period
primary microseism candidate:   approximately 14–20 s period
Earth hum candidate:            approximately 50–600 s period
```

The bands are approximate and may overlap with local sources. Ocean waves forcing the seafloor and continental shelves are major sources of the globally observed background seismic field.

The implementation exposes `MicroseismBandComparator`, but period alone never proves a source. A test requires:

```text
seismic time series
+ station transfer function
+ ocean-wave or pressure data
+ local cultural-noise control
+ synchronized clock
```

## 3. Quartz under geological vibration

A geological vibration can load quartz-bearing rock, but electrical output is not determined by stress alone. The observable depends on:

```text
quartz fraction
+ crystal orientation distribution
+ stress tensor and time derivative
+ domain coherence
+ fracture state
+ conductivity and leakage
+ electrode or field geometry
+ sensor transfer function
```

Random crystal orientations and conductive pathways can strongly cancel or discharge the polarization. The work therefore does not infer useful power from the mere existence of microseisms.

## 4. Fracture emission and X-ray boundary

Rock fracture can produce charge separation, radio-frequency transients and optical emission. These observations do not automatically establish X-rays.

A geological X-ray claim requires:

```text
energy-resolved X-ray spectrum
+ detector calibration
+ event synchronization
+ ambient pressure
+ background control
+ attenuation model
+ energy budget
```

Even a complete package becomes only `ready_for_test`. Detection and source attribution still require uncertainty and independent replication.

## 5. Planetary scale is not a linear multiplier

Earth's equatorial diameter is about 12,756 km. Larger rocky or partly rocky planets can have greater gravity and pressure, but the relevant mineral phases, temperature, conductivity and interior structure change with depth.

Therefore:

```text
larger planet
!= proportionally larger quartz-piezoelectric output
```

At sufficiently high pressure and temperature, quartz is no longer the stable silica phase. A planetary model must recompute mineralogy and constitutive laws rather than enlarge an Earth model geometrically.

## 6. Deep groundwater and the Hamza flow

The so-called Rio Hamza is best represented as regional groundwater movement through porous sedimentary rocks inferred from geothermal data, not a conventional underground channel.

A minimal comparator uses Darcy flow:

```math
q=-\frac{k}{\mu}(\nabla P-\rho\mathbf g)
```

The published continental-margin estimate is about 3,287 cubic metres per second, much smaller than the Amazon River discharge. The large width reflects a distributed basin-scale flow system.

## 7. Offshore relatively fresh groundwater

Electromagnetic surveys mapped low-salinity aquifers extending offshore on the U.S. Atlantic continental shelf. Expedition 501 later recovered cores and water samples beneath the seafloor.

The implementation avoids assuming that this water is:

- potable;
- renewable;
- abyssal;
- connected to modern recharge;
- safe to exploit.

Those questions require salinity, age tracers, connectivity tests, geochemistry and contamination assessment.

## 8. Quartz does not manufacture water

Bulk quartz is `SiO2`. Pressure and temperature do not create hydrogen atoms from pure silica.

Water associated with quartz may occur as:

- molecular water or OH defects;
- fluid inclusions;
- hydrothermal fluid surrounding or forming the quartz vein.

Deep-Earth water storage is more strongly associated with hydrous minerals and nominally anhydrous high-pressure phases such as wadsleyite and ringwoodite, which can store hydrogen in their crystal structures.

The implemented gate returns:

```text
quartz without measured H2O/inclusions -> no_bulk_water_source
quartz with fluid inclusions           -> fluid_inclusion_release_possible
measured hydrous ringwoodite           -> structural_hydrogen_reservoir
```

## 9. Planetary water is not universally salty

Long-lived water-rock interaction commonly adds dissolved ions, but planetary water chemistry is diverse. Rain-like condensate, brines, hydrothermal fluids, ice-melt reservoirs and isolated deep oceans can have very different salinities.

Thus:

```text
rocky planet + water != guaranteed Earth-like seawater
```

## 10. Commands

```bash
python3 src/solid_earth_hydrology.py validate-registry \
  data/literature/solid_earth_hydrology_sources.json

python3 src/solid_earth_hydrology.py classify-period 100

python3 -m pytest -q tests/test_solid_earth_hydrology.py
```

## 11. Next measurable package

The next experiment should couple both branches:

```text
seismometer/accelerometer
+ quartz-bearing sample
+ quartz-free control
+ stress and acoustic channel
+ electric and magnetic channels
+ energy-resolved radiation detector
+ temperature, pressure and conductivity
+ blind event windows
+ raw-data hashes
```

The geological vibration is treated as a real input. The transduced electrical or radiative output remains an experimentally measured response, not an automatic consequence.
