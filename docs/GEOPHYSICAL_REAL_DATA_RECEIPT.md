# Geophysical Real-Data Receipt v1

## Purpose

This component closes the gap between an experimental protocol and an auditable raw-data run:

```text
manifest
→ raw CSV channels
→ structural validation
→ clock-overlap validation
→ SHA-256 per channel
→ deterministic receipt
→ later scientific analysis
```

It does **not** choose a physical mechanism and does not promote a scientific claim.

## Required channels

Every run must provide synchronized numeric CSV files for:

- `stress`;
- `acoustic`;
- `electric`;
- `magnetic`.

Each CSV must contain a declared timestamp column, at least one declared value column, at least two rows, finite numeric values and strictly increasing timestamps.

## Mandatory controls

The manifest requires both:

```text
quartz-bearing sample
quartz-free control
```

Each control needs a `sample_id` and `composition_evidence`. A basalt label alone is not proof that a sample is quartz-free; the field must point to the actual composition record used by the experiment.

## Data classes

### `synthetic_fixture`

Used only to test the pipeline. A complete synthetic fixture always emits:

```text
evidence_state = SYNTHETIC_FIXTURE
claim_allowed = false
winner = TOKEN_VAZIO
```

### `physical_measurement`

Requires, in addition to valid raw files:

- `device_id`;
- pseudonymous `operator_id`;
- coarsened location;
- `preregistration_id`;
- `uncertainty_model`;
- channel calibration IDs.

Missing provenance remains `TOKEN_VAZIO`. A valid synchronized physical run may become `READY_FOR_ANALYSIS`, which still does not authorize a causal or scientific claim.

## Receipt contents

The receipt records:

- run and data class;
- manifest SHA-256;
- SHA-256 for each raw channel;
- row counts;
- declared columns;
- start, end and duration;
- median interval and sample rate;
- start/end skew and common time overlap;
- controls;
- missing physical provenance;
- explicit epistemic boundaries;
- deterministic receipt SHA-256.

Paths stored in the receipt are manifest-relative, so identical material produces the same receipt across Termux, CI and another checkout.

## Usage

Copy the template and place the CSV files relative to the manifest:

```bash
cp configs/geophysical_run_manifest.template.json /path/to/run/manifest.json
python3 src/geophysical_run_receipt.py validate-run \
  /path/to/run/manifest.json \
  --output /path/to/run/receipt.json
```

Pipeline self-test:

```bash
python3 src/geophysical_run_receipt.py validate-run \
  tests/fixtures/geophysical_run/manifest.json
python3 -m pytest -q tests/test_geophysical_run_receipt.py
```

## Promotion boundary

```text
READY_FOR_ANALYSIS
!= mechanism selected
!= effect detected
!= piezoelectric dominance
!= earthquake precursor
!= cosmological evidence
```

A causal winner remains blocked until a later analysis provides preregistered metrics, uncertainty propagation, baselines, falsifiers, raw-data hashes and preserved positive and negative results.
