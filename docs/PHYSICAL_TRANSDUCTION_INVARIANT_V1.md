# Physical Transduction Invariant v1

**Date:** 2026-08-09  
**State:** `EXECUTABLE_STRUCTURAL_INVARIANT`  
**Claim boundary:** `claim_allowed=false`  
**Important:** this is not a newly discovered conserved scalar, force or law of nature.

## 1. What is invariant?

Across mechanics, fluids, electromagnetism, plasma, chemistry, nuclear physics, geophysics and astrophysical observation, the carriers and equations change. What can remain invariant is the **minimum audit structure required for a proposed physical pathway to be meaningful, measurable and falsifiable**.

```text
source / free-energy gradient
  -> carrier
  -> medium / phase
  -> coupling operator
  -> rate or timescale
  -> transport and losses
  -> observable
  -> instrument
  -> uncertainty
  -> baseline
  -> falsifier
```

Changing domain does not remove these obligations.

## 2. Canonical pathway vector

```math
\mathcal P=(C,M,L,S,E,K,\mathcal C,\tau,D,O,I,U,B,F)
```

| Symbol | Executable field | Meaning |
|---|---|---|
| C | `carrier` | matter, charge, field, photon, phonon, reaction species, etc. |
| M | `medium` | material, vacuum, plasma, fluid, detector chain, etc. |
| L | `scale` | declared spatial/physical scale and units |
| S | `phase_state` | solid/liquid/gas/plasma/mixed/field regime |
| E | `free_energy_source` | boundary forcing, gradient or external work |
| K | `coupling_operator` | constitutive/reaction/transport operator linking stages |
| C | `conservation_laws` | scoped physical ledgers |
| tau | `rate_or_timescale` | rate law, relaxation time or sampling/interaction scale |
| D | `damping_or_loss` | leakage, viscosity, scattering, radiation, heat, etc. |
| O | `observable` | measurable consequence |
| I | `instrument` | calibrated measurement channel |
| U | `uncertainty` | uncertainty model and propagation |
| B | `baseline` | null/control/comparator |
| F | `falsifier` | result that would count against the pathway |

The repeated compact symbol `C` is disambiguated in code by explicit field names.

## 3. Conservation ledger

The previous geophysical note used, schematically:

```math
\sum Z_{in}=\sum Z_{out},\qquad
\sum A_{in}=\sum A_{out},\qquad
\sum q_{in}=\sum q_{out}.
```

That cannot be universal across the complete chemical -> atomic -> plasma -> particle hierarchy. In particular, nuclear charge number `Z` changes in beta processes, and `A` is not the appropriate universal invariant for arbitrary particle reactions.

The executable invariant therefore requires the general ledger to contain at least:

```math
Q_{in}=Q_{out}
```

and

```math
P^\mu_{in}=P^\mu_{out}
```

for the declared closed system, or the corresponding balance including explicit boundary fluxes for an open system.

Additional quantities are **regime-specific**, for example baryon/lepton number where applicable. Any such rule must declare its scope.

## 4. Open-system rule

Most experiments are not isolated. The correct statement is a balance law:

```math
\frac{d\mathcal Q_{system}}{dt}=\Phi_{in}-\Phi_{out}+S
```

where `Q` can represent mass, energy, momentum, charge or species inventory as appropriate. A pathway marked `open_system_with_fluxes` must list the exchange terms.

This prevents apparent creation/destruction caused merely by drawing the system boundary incorrectly.

## 5. Structural invariance vs physical truth

A structurally complete pathway can still be false.

```text
STRUCTURAL_COMPLETE
!= effect observed
!= causal attribution
!= replicated
!= new physics
```

The executable states are:

```text
malformed contract        -> BLOCKED
explicit unknown fields   -> TOKEN_VAZIO
all structural fields set -> READY_FOR_TEST
```

`READY_FOR_TEST` is deliberately below `MEASURED`.

## 6. Example: quartz pathway

```text
mechanical driver
  -> stress in quartz-bearing solid
  -> piezoelectric constitutive coupling
  -> polarization / charge
  -> leakage and dielectric loss
  -> voltage transient
  -> calibrated electrometer
  -> uncertainty propagation
  -> quartz-free matched control
  -> falsifier: no excess synchronized response
```

This pathway can be structurally complete while the measured effect is zero. That zero is scientifically valid evidence.

## 7. Cross-domain transformation

Two pathways from very different domains can be compared by their structural signature rather than by pretending their carriers are identical:

```math
\Sigma(\mathcal P)=
(1_C,1_M,1_L,1_S,1_E,1_K,1_{\mathcal C},1_\tau,1_D,1_O,1_I,1_U,1_B,1_F)
```

Each component is `1` only when that obligation is materially declared. This is a **coverage signature**, not a probability of truth.

The useful invariant is therefore:

> every promoted physical explanation must preserve the complete chain from available free energy to a falsifiable calibrated observation, with scoped conservation and explicit losses.

## 8. Why this helps RLL

The invariant supplies a common gate between local physics and cosmological analysis without collapsing scales:

```text
local geophysical pathway
  -> physical receipt
  -> structural invariant receipt
  -> observational/systematics comparator in RLL
  -X-> automatic cosmological promotion
```

A local mechanism may become an environmental or instrumental null model. It cannot become background-cosmology evidence merely because its structural chain is complete.

## 9. Executable implementation

```text
src/physical_transduction_invariant.py
tests/test_physical_transduction_invariant.py
configs/physical_transduction_pathway.example.json
```

Run:

```bash
python src/physical_transduction_invariant.py \
  configs/physical_transduction_pathway.example.json
python -m pytest -q tests/test_physical_transduction_invariant.py
```

The example starts entirely in `TOKEN_VAZIO` by design.

## 10. Promotion ladder

```text
HISTORICAL_CONCEPTUAL
      ↓
HYPOTHESIS
      ↓
STRUCTURAL / TOKEN_VAZIO audit
      ↓
READY_FOR_TEST
      ↓
MEASURED
      ↓
REPLICATED
      ↓
MODEL_COMPARISON
```

There is no direct edge from symbolic/conceptual text to scientific claim.

## 11. Canonical boundary

The invariant is a reusable **epistemic-physical contract**. It is valuable precisely because it remains valid when a candidate mechanism fails: missing information stays `TOKEN_VAZIO`, malformed reasoning is `BLOCKED`, and a complete but unsupported mechanism remains only `READY_FOR_TEST` until data arrive.
