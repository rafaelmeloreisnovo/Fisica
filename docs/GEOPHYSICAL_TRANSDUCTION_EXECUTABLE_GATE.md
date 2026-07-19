# Executable Geophysical Transduction Gate

**Date:** 2026-07-19  
**State:** implemented comparator and evidence gate  
**Claim boundary:** `claim_allowed=false`

## Purpose

This package converts the geophysical, piezoelectric, fracture, radiation and observer material into a small executable contract.

It deliberately does **not** implement an earthquake predictor. It implements:

1. a DOI-centered source registry containing supportive and contradictory evidence;
2. a transparent damped-oscillator comparator;
3. a transparent lumped piezoelectric comparator with leakage;
4. a mechanism-readiness tournament;
5. an experiment manifest that begins entirely as `TOKEN_VAZIO`;
6. adversarial tests that block causal promotion without controls.

## Files

```text
data/literature/geophysical_transduction_sources.json
src/geophysical_transduction.py
configs/geophysical_transduction_experiment.example.json
tests/test_geophysical_transduction.py
.github/workflows/geophysical-transduction.yml
```

## Literature tournament

The registry includes distinct mechanisms and counterevidence:

```text
quartz piezoelectricity
fracture/contact electrification
positive-hole charge carriers
electrokinetic flow
solar-ionospheric modulation
instrumental/anthropogenic contamination
```

Quartz-free basalt emission is preserved as mandatory counterevidence. Therefore:

```text
electromagnetic signal + quartz-bearing rock
!= proof that quartz piezoelectricity dominated
```

## Physical comparators

### Damped oscillator

```math
m\ddot x+c\dot x+kx=F_0\cos(\omega t)
```

The implementation returns natural frequency, damping ratio, damping regime and steady-state amplitude.

### Lumped piezoelectric comparator

```math
F=\sigma A,\qquad Q=dF,\qquad V_{\rm ideal}=Q/C
```

Leakage is represented by:

```math
V(t)=V_{\rm ideal}\exp[-t/(RC)]
```

Every coefficient must be supplied by the caller. No quartz constant is silently invented.

## Mechanism gate

A mechanism becomes `ready_for_test` only when its own artifacts and controls exist. Examples:

- `piezoelectric_quartz` requires mineral fraction, crystal orientation, conductivity, calibrated electric sensors and a quartz-free control;
- `fracture_contact_electrification` requires synchronized fracture/stick-slip, force/acoustic and EM channels;
- `solar_ionospheric_modulation` requires solar, ionospheric, lightning and ELF records on a synchronized clock;
- `instrumental_or_anthropogenic` requires grid, weather and independent-station controls.

Readiness never chooses a physical winner. A winner requires preregistered metrics, observed data, uncertainty and falsifiers.

## Commands

```bash
python3 src/geophysical_transduction.py validate-registry \
  data/literature/geophysical_transduction_sources.json

python3 src/geophysical_transduction.py evaluate-manifest \
  configs/geophysical_transduction_experiment.example.json

python3 -m pytest -q tests/test_geophysical_transduction.py
```

Expected example state:

```text
registry valid = true
winner = TOKEN_VAZIO
ready_for_test = []
claim_allowed = false
```

## Next data-bearing step

The first real run should remain small:

```text
one stressed sample
+ one quartz-free control
+ synchronized force/acoustic/electric/magnetic channels
+ temperature and conductivity
+ raw waveform hashes
+ blind event windows
```

Only after this local comparator is reproducible should the work add field stations, solar/ionospheric series or RLL environmental residuals.
