import json
import math
from pathlib import Path

import pytest

from src.geophysical_transduction import (
    Decision,
    DampedOscillator,
    LinearPiezoelectricComparator,
    evaluate_manifest,
    evaluate_mechanism_readiness,
    validate_source_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_source_registry_is_valid_and_claim_bounded():
    payload = json.loads((ROOT / "data/literature/geophysical_transduction_sources.json").read_text())
    assert validate_source_registry(payload) == []
    assert payload["claim_allowed"] is False
    assert any(source["verification_status"] == "counterevidence" for source in payload["sources"])


def test_duplicate_doi_is_rejected():
    source = {
        "doi": "10.1/example",
        "verification_status": "primary_verified",
        "journal_or_authority": "A",
        "supports": [],
        "does_not_support": [],
        "safe_use": "x",
    }
    payload = {"claim_allowed": False, "sources": [dict(source, source_id="a"), dict(source, source_id="b")]}
    assert any("duplicate DOI" in error for error in validate_source_registry(payload))


def test_damped_oscillator_classifies_regimes():
    under = DampedOscillator(1.0, 0.5, 4.0)
    critical = DampedOscillator(1.0, 4.0, 4.0)
    over = DampedOscillator(1.0, 5.0, 4.0)
    assert under.regime == "underdamped"
    assert critical.regime == "critical"
    assert over.regime == "overdamped"
    assert under.natural_angular_frequency_rad_s == pytest.approx(2.0)


def test_damped_response_is_finite_with_loss():
    oscillator = DampedOscillator(2.0, 0.4, 18.0)
    amplitude = oscillator.steady_state_amplitude_m(1.0, 3.0)
    assert math.isfinite(amplitude)
    assert amplitude > 0


def test_ideal_undamped_resonance_fails_closed():
    oscillator = DampedOscillator(1.0, 0.0, 4.0)
    with pytest.raises(ZeroDivisionError):
        oscillator.steady_state_amplitude_m(1.0, 2.0)


def test_linear_piezoelectric_comparator_is_transparent():
    comparator = LinearPiezoelectricComparator(
        stress_pa=1_000.0,
        loaded_area_m2=0.01,
        charge_coefficient_c_per_n=2e-12,
        capacitance_f=1e-9,
        leakage_resistance_ohm=1e9,
        hold_time_s=0.0,
    )
    assert comparator.force_n == pytest.approx(10.0)
    assert comparator.generated_charge_c == pytest.approx(2e-11)
    assert comparator.ideal_open_circuit_voltage_v == pytest.approx(0.02)
    assert comparator.retained_voltage_v == pytest.approx(0.02)


def test_leakage_reduces_retained_voltage():
    base = dict(
        stress_pa=1_000.0,
        loaded_area_m2=0.01,
        charge_coefficient_c_per_n=2e-12,
        capacitance_f=1e-9,
        leakage_resistance_ohm=1e9,
    )
    immediate = LinearPiezoelectricComparator(**base, hold_time_s=0.0)
    delayed = LinearPiezoelectricComparator(**base, hold_time_s=2.0)
    assert delayed.retained_voltage_v < immediate.retained_voltage_v


def test_missing_controls_preserve_token_vazio():
    decision, missing = evaluate_mechanism_readiness(
        "piezoelectric_quartz",
        {"stress_time_series": "stress.csv", "quartz_fraction": 0.4, "crystal_orientation": "TOKEN_VAZIO"},
    )
    assert decision is Decision.TOKEN_VAZIO
    assert "crystal_orientation" in missing


def test_complete_readiness_does_not_select_causal_winner():
    artifacts = {
        "stress_time_series": "stress.csv",
        "quartz_fraction": 0.4,
        "crystal_orientation": "orientation.json",
        "bulk_conductivity": "conductivity.csv",
        "electric_sensor_calibration": "calibration.json",
        "quartz_free_control": "basalt-control.csv"
    }
    decision, missing = evaluate_mechanism_readiness("piezoelectric_quartz", artifacts)
    assert decision is Decision.READY_FOR_TEST
    assert missing == []


def test_example_manifest_has_no_winner():
    payload = json.loads((ROOT / "configs/geophysical_transduction_experiment.example.json").read_text())
    result = evaluate_manifest(payload)
    assert result["winner"] == "TOKEN_VAZIO"
    assert result["claim_allowed"] is False
    assert not result["ready_for_test"]
    assert all(value["decision"] == Decision.TOKEN_VAZIO.value for value in result["mechanisms"].values())


@pytest.mark.parametrize(
    "oscillator",
    [DampedOscillator(0.0, 1.0, 1.0), DampedOscillator(1.0, -1.0, 1.0), DampedOscillator(1.0, 1.0, 0.0)],
)
def test_invalid_oscillator_parameters_fail_closed(oscillator):
    with pytest.raises(ValueError):
        oscillator.validate()


def test_unknown_mechanism_is_blocked():
    decision, reasons = evaluate_mechanism_readiness("new_physics", {})
    assert decision is Decision.BLOCKED
    assert reasons
