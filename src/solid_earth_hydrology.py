"""Fail-closed comparators for solid-Earth vibration, deep water and radiation scale claims."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping


class GateDecision(str, Enum):
    READY_FOR_TEST = "ready_for_test"
    BLOCKED = "blocked"
    TOKEN_VAZIO = "TOKEN_VAZIO"


class WaterCarrierState(str, Enum):
    NO_BULK_WATER_SOURCE = "no_bulk_water_source"
    FLUID_INCLUSION_RELEASE_POSSIBLE = "fluid_inclusion_release_possible"
    STRUCTURAL_HYDROGEN_RESERVOIR = "structural_hydrogen_reservoir"
    TOKEN_VAZIO = "TOKEN_VAZIO"


@dataclass(frozen=True)
class MicroseismBandComparator:
    """Approximate period-band comparator; bands can overlap."""

    period_s: float

    def validate(self) -> None:
        if not math.isfinite(self.period_s) or self.period_s <= 0:
            raise ValueError("period_s must be finite and positive")

    @property
    def frequency_hz(self) -> float:
        self.validate()
        return 1.0 / self.period_s

    @property
    def candidate_bands(self) -> tuple[str, ...]:
        self.validate()
        bands: list[str] = []
        if self.period_s < 1.0:
            bands.append("high_frequency_local_or_anthropogenic")
        if 3.0 <= self.period_s <= 12.0:
            bands.append("secondary_microseism_candidate")
        if 14.0 <= self.period_s <= 20.0:
            bands.append("primary_microseism_candidate")
        if 50.0 <= self.period_s <= 600.0:
            bands.append("earth_hum_candidate")
        return tuple(bands or ["unclassified_period"])


@dataclass(frozen=True)
class DarcyFlowComparator:
    """One-dimensional Darcy specific discharge comparator."""

    permeability_m2: float
    dynamic_viscosity_pa_s: float
    pressure_gradient_pa_m: float
    fluid_density_kg_m3: float = 1000.0
    gravity_component_m_s2: float = 0.0

    def validate(self) -> None:
        if self.permeability_m2 <= 0 or not math.isfinite(self.permeability_m2):
            raise ValueError("permeability_m2 must be finite and positive")
        if self.dynamic_viscosity_pa_s <= 0 or not math.isfinite(self.dynamic_viscosity_pa_s):
            raise ValueError("dynamic_viscosity_pa_s must be finite and positive")
        if self.fluid_density_kg_m3 <= 0 or not math.isfinite(self.fluid_density_kg_m3):
            raise ValueError("fluid_density_kg_m3 must be finite and positive")
        for value, name in (
            (self.pressure_gradient_pa_m, "pressure_gradient_pa_m"),
            (self.gravity_component_m_s2, "gravity_component_m_s2"),
        ):
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")

    @property
    def specific_discharge_m_s(self) -> float:
        self.validate()
        driving_gradient = (
            self.pressure_gradient_pa_m
            - self.fluid_density_kg_m3 * self.gravity_component_m_s2
        )
        return -(self.permeability_m2 / self.dynamic_viscosity_pa_s) * driving_gradient

    def pore_velocity_m_s(self, porosity: float) -> float:
        if not 0 < porosity <= 1:
            raise ValueError("porosity must be in (0, 1]")
        return self.specific_discharge_m_s / porosity


HYDROUS_PHASES = {
    "serpentine",
    "amphibole",
    "mica",
    "clay",
    "wadsleyite",
    "ringwoodite",
    "brucite",
    "lawsonite",
}


def classify_water_carrier(
    mineral_phase: str,
    *,
    has_fluid_inclusions: bool = False,
    measured_hydrogen_or_water: bool = False,
) -> WaterCarrierState:
    phase = mineral_phase.strip().lower()
    if not phase:
        return WaterCarrierState.TOKEN_VAZIO
    if phase in {"quartz", "sio2", "silica"}:
        if has_fluid_inclusions or measured_hydrogen_or_water:
            return WaterCarrierState.FLUID_INCLUSION_RELEASE_POSSIBLE
        return WaterCarrierState.NO_BULK_WATER_SOURCE
    if phase in HYDROUS_PHASES and measured_hydrogen_or_water:
        return WaterCarrierState.STRUCTURAL_HYDROGEN_RESERVOIR
    return WaterCarrierState.TOKEN_VAZIO


READINESS_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "solid_earth_hum": (
        "seismic_time_series",
        "station_response",
        "ocean_wave_or_pressure_series",
        "local_cultural_noise_control",
        "clock_synchronization",
    ),
    "geological_fractoemission": (
        "stress_or_fracture_timing",
        "lithology_and_mineralogy",
        "broadband_em_or_optical_waveform",
        "detector_calibration",
        "ambient_pressure",
        "material_control",
    ),
    "geological_xray_emission": (
        "xray_energy_spectrum",
        "xray_detector_calibration",
        "source_event_timing",
        "ambient_pressure",
        "background_control",
        "attenuation_model",
        "energy_budget",
    ),
    "deep_groundwater_flow": (
        "temperature_or_pressure_logs",
        "permeability",
        "porosity",
        "fluid_chemistry_or_isotopes",
        "boundary_geometry",
        "uncertainty_model",
    ),
    "offshore_relatively_fresh_groundwater": (
        "subseafloor_core_or_water_sample",
        "salinity_profile",
        "age_tracer",
        "onshore_connectivity_test",
        "recharge_or_fossil_water_model",
        "contamination_assessment",
    ),
    "hydrous_mineral_dehydration": (
        "mineral_phase_identification",
        "pressure_temperature_path",
        "water_or_hydrogen_content",
        "released_fluid_analysis",
        "mass_balance",
    ),
}


def _present(value: Any) -> bool:
    if value in (None, "", "TOKEN_VAZIO"):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def evaluate_readiness(
    mechanism: str,
    artifacts: Mapping[str, Any],
) -> tuple[GateDecision, list[str]]:
    requirements = READINESS_REQUIREMENTS.get(mechanism)
    if requirements is None:
        return GateDecision.BLOCKED, [f"unknown mechanism: {mechanism}"]
    token_vazio = [name for name in requirements if artifacts.get(name) == "TOKEN_VAZIO"]
    if token_vazio:
        return GateDecision.TOKEN_VAZIO, token_vazio
    missing = [name for name in requirements if not _present(artifacts.get(name))]
    if missing:
        return GateDecision.BLOCKED, missing
    return GateDecision.READY_FOR_TEST, []


def evaluate_geological_xray_claim(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    decision, missing = evaluate_readiness("geological_xray_emission", artifacts)
    if decision is not GateDecision.READY_FOR_TEST:
        return {
            "decision": decision.value,
            "missing_or_token_vazio": missing,
            "claim_allowed": False,
            "interpretation": "Optical, radio or charge emission cannot be relabelled as X-ray evidence.",
        }
    return {
        "decision": GateDecision.READY_FOR_TEST.value,
        "missing_or_token_vazio": [],
        "claim_allowed": False,
        "interpretation": (
            "The package is ready to test for X-rays; detection still requires a spectrum, "
            "background subtraction, uncertainty and independent replication."
        ),
    }


def validate_source_registry(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        return errors + ["sources must be a non-empty list"]
    seen_ids: set[str] = set()
    seen_dois: set[str] = set()
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
                errors.append(f"{prefix}.doi must be null or a DOI string")
            elif doi in seen_dois:
                errors.append(f"duplicate DOI: {doi}")
            else:
                seen_dois.add(doi)
        if not source.get("journal_or_authority"):
            errors.append(f"{prefix}.journal_or_authority is required")
        for field in ("supports", "does_not_support"):
            if not isinstance(source.get(field), list):
                errors.append(f"{prefix}.{field} must be a list")
        if not source.get("safe_use"):
            errors.append(f"{prefix}.safe_use is required")
    return errors


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    registry = sub.add_parser("validate-registry")
    registry.add_argument("path")
    band = sub.add_parser("classify-period")
    band.add_argument("period_s", type=float)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "validate-registry":
        errors = validate_source_registry(load_json(args.path))
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2, sort_keys=True))
        return 0 if not errors else 1
    if args.command == "classify-period":
        comparator = MicroseismBandComparator(args.period_s)
        print(json.dumps({
            "period_s": comparator.period_s,
            "frequency_hz": comparator.frequency_hz,
            "candidate_bands": comparator.candidate_bands,
        }, indent=2, sort_keys=True))
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
