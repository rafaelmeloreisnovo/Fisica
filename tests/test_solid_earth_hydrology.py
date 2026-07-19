import json
from pathlib import Path

import pytest

from src.solid_earth_hydrology import (
    DarcyFlowComparator,
    GateDecision,
    MicroseismBandComparator,
    WaterCarrierState,
    classify_water_carrier,
    evaluate_geological_xray_claim,
    evaluate_readiness,
    validate_source_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_registry_is_valid_and_contains_brighton_boundary():
    payload = json.loads((ROOT / "data/literature/solid_earth_hydrology_sources.json").read_text())
    assert validate_source_registry(payload) == []
    twins = next(item for item in payload["sources"] if item["source_id"] == "SRC_BRIGHTON_TWINS_OFFICIAL")
    assert any("solid-Earth vibration" in item for item in twins["does_not_support"])


def test_microseism_period_bands():
    assert "secondary_microseism_candidate" in MicroseismBandComparator(8.0).candidate_bands
    assert "primary_microseism_candidate" in MicroseismBandComparator(17.0).candidate_bands
    assert "earth_hum_candidate" in MicroseismBandComparator(100.0).candidate_bands


def test_invalid_period_fails_closed():
    with pytest.raises(ValueError):
        MicroseismBandComparator(0.0).validate()


def test_darcy_flow_is_slow_for_low_permeability():
    flow = DarcyFlowComparator(
        permeability_m2=1e-15,
        dynamic_viscosity_pa_s=1e-3,
        pressure_gradient_pa_m=100.0,
    )
    assert abs(flow.specific_discharge_m_s) == pytest.approx(1e-10)
    assert abs(flow.pore_velocity_m_s(0.2)) == pytest.approx(5e-10)


def test_invalid_porosity_fails_closed():
    flow = DarcyFlowComparator(1e-15, 1e-3, 1.0)
    with pytest.raises(ValueError):
        flow.pore_velocity_m_s(0.0)


def test_quartz_is_not_bulk_water_source_without_evidence():
    assert classify_water_carrier("quartz") is WaterCarrierState.NO_BULK_WATER_SOURCE


def test_quartz_fluid_inclusion_can_release_included_water():
    assert classify_water_carrier("quartz", has_fluid_inclusions=True) is WaterCarrierState.FLUID_INCLUSION_RELEASE_POSSIBLE


def test_ringwoodite_can_store_structural_hydrogen_when_measured():
    assert classify_water_carrier("ringwoodite", measured_hydrogen_or_water=True) is WaterCarrierState.STRUCTURAL_HYDROGEN_RESERVOIR


def test_optical_or_radio_signal_does_not_become_xray_claim():
    result = evaluate_geological_xray_claim({
        "broadband_em_or_optical_waveform": "optical.csv"
    })
    assert result["claim_allowed"] is False
    assert result["decision"] in {GateDecision.BLOCKED.value, GateDecision.TOKEN_VAZIO.value}
    assert "cannot be relabelled" in result["interpretation"]


def test_complete_xray_package_is_only_ready_for_test():
    artifacts = {
        "xray_energy_spectrum": "spectrum.csv",
        "xray_detector_calibration": "calibration.json",
        "source_event_timing": "events.csv",
        "ambient_pressure": 101325,
        "background_control": "background.csv",
        "attenuation_model": "attenuation.json",
        "energy_budget": "ledger.json",
    }
    result = evaluate_geological_xray_claim(artifacts)
    assert result["decision"] == GateDecision.READY_FOR_TEST.value
    assert result["claim_allowed"] is False


def test_deep_groundwater_requires_chemistry_and_geometry():
    decision, missing = evaluate_readiness("deep_groundwater_flow", {
        "temperature_or_pressure_logs": "logs.csv",
        "permeability": 1e-15,
        "porosity": 0.2,
    })
    assert decision is GateDecision.BLOCKED
    assert "fluid_chemistry_or_isotopes" in missing
    assert "boundary_geometry" in missing


def test_unknown_mechanism_is_blocked():
    decision, missing = evaluate_readiness("planetary_magic", {})
    assert decision is GateDecision.BLOCKED
    assert missing
