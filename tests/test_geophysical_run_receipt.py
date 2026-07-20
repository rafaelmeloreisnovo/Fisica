import json
from pathlib import Path

import pytest

from src.geophysical_run_receipt import (
    TOKEN_VAZIO,
    build_receipt,
    canonical_json_bytes,
    validate_manifest_structure,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/geophysical_run/manifest.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_synthetic_fixture_builds_integrity_receipt_without_claim():
    receipt = build_receipt(load_fixture(), FIXTURE)
    assert receipt["evidence_state"] == "SYNTHETIC_FIXTURE"
    assert receipt["claim_allowed"] is False
    assert receipt["winner"] == TOKEN_VAZIO
    assert receipt["clock"]["synchronization_ok"] is True
    assert receipt["physical_gate"]["ready_for_analysis"] is False
    assert set(receipt["channels"]) == {"stress", "acoustic", "electric", "magnetic"}
    assert all(channel["rows"] == 11 for channel in receipt["channels"].values())


def test_receipt_is_deterministic():
    first = build_receipt(load_fixture(), FIXTURE)
    second = build_receipt(load_fixture(), FIXTURE)
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert first["receipt_sha256"] == second["receipt_sha256"]


def test_physical_measurement_missing_provenance_stays_token_vazio():
    payload = load_fixture()
    payload["data_class"] = "physical_measurement"
    receipt = build_receipt(payload, FIXTURE)
    assert receipt["evidence_state"] == TOKEN_VAZIO
    assert receipt["physical_gate"]["missing"] == [
        "device_id",
        "location_coarsened",
        "operator_id",
        "preregistration_id",
        "uncertainty_model",
    ]


def test_physical_measurement_with_metadata_is_only_ready_for_analysis():
    payload = load_fixture()
    payload.update(
        {
            "data_class": "physical_measurement",
            "device_id": "DEVICE-HASH-001",
            "operator_id": "OPERATOR-PSEUDONYM-001",
            "location_coarsened": "REGION-LEVEL",
            "preregistration_id": "PREREG-001",
            "uncertainty_model": "UNCERTAINTY-MODEL-001",
        }
    )
    receipt = build_receipt(payload, FIXTURE)
    assert receipt["evidence_state"] == "READY_FOR_ANALYSIS"
    assert receipt["claim_allowed"] is False
    assert receipt["winner"] == TOKEN_VAZIO


def test_missing_quartz_free_control_fails_closed():
    payload = load_fixture()
    del payload["controls"]["quartz_free_control"]
    errors = validate_manifest_structure(payload)
    assert "controls.quartz_free_control is required" in errors


def test_non_monotonic_timestamp_is_rejected(tmp_path):
    payload = load_fixture()
    for source in FIXTURE.parent.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    payload["channels"]["stress"]["path"] = "stress.csv"
    bad = tmp_path / "stress.csv"
    bad.write_text("t_s,stress_pa\n0.00,1\n0.02,2\n0.01,3\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="strictly increasing"):
        build_receipt(payload, manifest)


def test_raw_file_tamper_changes_channel_and_receipt_hash(tmp_path):
    payload = load_fixture()
    for source in FIXTURE.parent.glob("*.csv"):
        (tmp_path / source.name).write_bytes(source.read_bytes())
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    first = build_receipt(payload, manifest)
    electric = tmp_path / "electric.csv"
    electric.write_text(electric.read_text(encoding="utf-8") + "0.11,0.011\n", encoding="utf-8")
    second = build_receipt(payload, manifest)
    assert first["channels"]["electric"]["sha256"] != second["channels"]["electric"]["sha256"]
    assert first["receipt_sha256"] != second["receipt_sha256"]
