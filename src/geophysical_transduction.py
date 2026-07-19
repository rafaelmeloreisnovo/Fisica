"""Evidence-gated geophysical transduction primitives.

This module does not predict earthquakes and does not establish a universal
precursor. It validates literature registries and experimental manifests,
provides transparent physical comparators, and fails closed when evidence is absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping


class EvidenceState(str, Enum):
    PRIMARY_VERIFIED = "primary_verified"
    INSTITUTIONAL_VERIFIED = "institutional_verified"
    COUNTEREVIDENCE = "counterevidence"
    PENDING_FULLTEXT = "pending_fulltext"
    TOKEN_VAZIO = "TOKEN_VAZIO"


class Decision(str, Enum):
    READY_FOR_TEST = "ready_for_test"
    BLOCKED = "blocked"
    TOKEN_VAZIO = "TOKEN_VAZIO"


@dataclass(frozen=True)
class DampedOscillator:
    """Single-degree-of-freedom comparator: m*x'' + c*x' + k*x = F."""

    mass_kg: float
    damping_n_s_m: float
    stiffness_n_m: float

    def validate(self) -> None:
        if self.mass_kg <= 0:
            raise ValueError("mass_kg must be positive")
        if self.damping_n_s_m < 0:
            raise ValueError("damping_n_s_m must be non-negative")
        if self.stiffness_n_m <= 0:
            raise ValueError("stiffness_n_m must be positive")

    @property
    def natural_angular_frequency_rad_s(self) -> float:
        self.validate()
        return math.sqrt(self.stiffness_n_m / self.mass_kg)

    @property
    def damping_ratio(self) -> float:
        self.validate()
        return self.damping_n_s_m / (
            2.0 * math.sqrt(self.mass_kg * self.stiffness_n_m)
        )

    @property
    def regime(self) -> str:
        zeta = self.damping_ratio
        if math.isclose(zeta, 1.0, rel_tol=1e-12, abs_tol=1e-12):
            return "critical"
        return "underdamped" if zeta < 1.0 else "overdamped"

    def steady_state_amplitude_m(
        self,
        forcing_amplitude_n: float,
        forcing_angular_frequency_rad_s: float,
    ) -> float:
        self.validate()
        if forcing_amplitude_n < 0:
            raise ValueError("forcing_amplitude_n must be non-negative")
        if forcing_angular_frequency_rad_s < 0:
            raise ValueError("forcing_angular_frequency_rad_s must be non-negative")
        omega = forcing_angular_frequency_rad_s
        denominator = math.sqrt(
            (self.stiffness_n_m - self.mass_kg * omega * omega) ** 2
            + (self.damping_n_s_m * omega) ** 2
        )
        if denominator == 0:
            raise ZeroDivisionError("ideal undamped resonance is singular")
        return forcing_amplitude_n / denominator


@dataclass(frozen=True)
class LinearPiezoelectricComparator:
    """Lumped linear comparator with explicit supplied coefficients.

    Q=dF, V_ideal=Q/C and V(t)=V_ideal*exp[-t/(RC)]. This does not replace
    anisotropic tensor constitutive models.
    """

    stress_pa: float
    loaded_area_m2: float
    charge_coefficient_c_per_n: float
    capacitance_f: float
    leakage_resistance_ohm: float
    hold_time_s: float

    def validate(self) -> None:
        if self.stress_pa < 0:
            raise ValueError("stress_pa must be non-negative")
        if self.loaded_area_m2 <= 0:
            raise ValueError("loaded_area_m2 must be positive")
        if not math.isfinite(self.charge_coefficient_c_per_n):
            raise ValueError("charge coefficient must be finite")
        if self.capacitance_f <= 0:
            raise ValueError("capacitance_f must be positive")
        if self.leakage_resistance_ohm <= 0:
            raise ValueError("leakage_resistance_ohm must be positive")
        if self.hold_time_s < 0:
            raise ValueError("hold_time_s must be non-negative")

    @property
    def force_n(self) -> float:
        self.validate()
        return self.stress_pa * self.loaded_area_m2

    @property
    def generated_charge_c(self) -> float:
        return self.charge_coefficient_c_per_n * self.force_n

    @property
    def ideal_open_circuit_voltage_v(self) -> float:
        return self.generated_charge_c / self.capacitance_f

    @property
    def retained_voltage_v(self) -> float:
        tau = self.leakage_resistance_ohm * self.capacitance_f
        return self.ideal_open_circuit_voltage_v * math.exp(-self.hold_time_s / tau)


MECHANISM_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "piezoelectric_quartz": (
        "stress_time_series", "quartz_fraction", "crystal_orientation",
        "bulk_conductivity", "electric_sensor_calibration", "quartz_free_control",
    ),
    "fracture_contact_electrification": (
        "fracture_or_stick_slip_timing", "ambient_pressure",
        "force_or_acoustic_channel", "electromagnetic_sensor_calibration",
        "material_control",
    ),
    "positive_hole_carriers": (
        "rock_lithology", "stress_time_series", "surface_current_or_air_ion_channel",
        "electric_sensor_calibration", "quartz_free_control",
    ),
    "electrokinetic_flow": (
        "pore_fluid_composition", "permeability", "pressure_gradient",
        "bulk_conductivity", "electrode_calibration", "dry_control",
    ),
    "solar_ionospheric_modulation": (
        "solar_xray_or_solar_wind_series", "ionospheric_conductivity_proxy",
        "lightning_or_source_activity", "schumann_or_elf_series",
        "clock_synchronization",
    ),
    "instrumental_or_anthropogenic": (
        "raw_waveform", "sensor_calibration", "power_grid_monitor",
        "weather_log", "independent_station", "clock_synchronization",
    ),
}


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return payload


def validate_source_registry(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    seen_dois: set[str] = set()
    allowed_states = {state.value for state in EvidenceState}
    for index, source in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{prefix}.source_id is required")
        elif source_id in seen_ids:
            errors.append(f"duplicate source_id: {source_id}")
        else:
            seen_ids.add(source_id)
        doi = source.get("doi")
        if doi is not None:
            if not isinstance(doi, str) or not doi.startswith("10."):
                errors.append(f"{prefix}.doi must be a DOI string or null")
            elif doi in seen_dois:
                errors.append(f"duplicate DOI: {doi}")
            else:
                seen_dois.add(doi)
        if source.get("verification_status") not in allowed_states:
            errors.append(f"{prefix}.verification_status invalid")
        if not source.get("journal_or_authority"):
            errors.append(f"{prefix}.journal_or_authority is required")
        if not isinstance(source.get("supports"), list):
            errors.append(f"{prefix}.supports must be a list")
        if not isinstance(source.get("does_not_support"), list):
            errors.append(f"{prefix}.does_not_support must be a list")
        if not source.get("safe_use"):
            errors.append(f"{prefix}.safe_use is required")
    return errors


def _artifact_present(value: Any) -> bool:
    if value in (None, "", "TOKEN_VAZIO"):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) > 0
    return True


def evaluate_mechanism_readiness(
    mechanism: str,
    artifacts: Mapping[str, Any],
) -> tuple[Decision, list[str]]:
    if mechanism not in MECHANISM_REQUIREMENTS:
        return Decision.BLOCKED, [f"unknown mechanism: {mechanism}"]
    required = MECHANISM_REQUIREMENTS[mechanism]
    token_vazio = [
        name for name in required if artifacts.get(name) == EvidenceState.TOKEN_VAZIO.value
    ]
    if token_vazio:
        return Decision.TOKEN_VAZIO, token_vazio
    missing = [name for name in required if not _artifact_present(artifacts.get(name))]
    if missing:
        return Decision.BLOCKED, missing
    return Decision.READY_FOR_TEST, []


def evaluate_manifest(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("claim_allowed") is not False:
        raise ValueError("manifest claim_allowed must be false")
    artifacts = payload.get("artifacts")
    mechanisms = payload.get("candidate_mechanisms")
    if not isinstance(artifacts, dict):
        raise ValueError("manifest artifacts must be an object")
    if not isinstance(mechanisms, list) or not mechanisms:
        raise ValueError("manifest candidate_mechanisms must be a non-empty list")
    decisions: dict[str, Any] = {}
    for mechanism in mechanisms:
        decision, reasons = evaluate_mechanism_readiness(str(mechanism), artifacts)
        decisions[str(mechanism)] = {
            "decision": decision.value,
            "missing_or_token_vazio": reasons,
        }
    ready = [
        mechanism for mechanism, result in decisions.items()
        if result["decision"] == Decision.READY_FOR_TEST.value
    ]
    return {
        "run_id": payload.get("run_id", "TOKEN_VAZIO"),
        "claim_allowed": False,
        "mechanisms": decisions,
        "ready_for_test": ready,
        "winner": "TOKEN_VAZIO",
        "winner_rule": (
            "A causal winner requires preregistered metrics, controls, uncertainty, "
            "and observed data. Readiness alone never selects a physical cause."
        ),
    }


def _write_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    registry_parser = subparsers.add_parser("validate-registry")
    registry_parser.add_argument("path")
    manifest_parser = subparsers.add_parser("evaluate-manifest")
    manifest_parser.add_argument("path")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "validate-registry":
        errors = validate_source_registry(load_json(args.path))
        _write_json({"valid": not errors, "errors": errors})
        return 0 if not errors else 1
    if args.command == "evaluate-manifest":
        _write_json(evaluate_manifest(load_json(args.path)))
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
