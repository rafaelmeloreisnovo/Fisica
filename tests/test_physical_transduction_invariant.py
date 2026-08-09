from src.physical_transduction_invariant import (
    InvariantState,
    TOKEN_VAZIO,
    build_invariant_receipt,
    classify_pathway,
    structural_signature,
    token_vazio_components,
    validate_pathway,
)


def pathway():
    return {
        "schema": "physical_transduction_pathway_v1",
        "pathway_id": "TEST-PIEZO-001",
        "domain": "multiphysics",
        "claim_allowed": False,
        "components": {
            "carrier": "electric polarization/charge",
            "medium": "quartz-bearing solid + electrical readout",
            "scale": {"spatial": 0.01, "unit": "m"},
            "phase_state": "solid",
            "free_energy_source": "externally applied mechanical stress",
            "coupling_operator": "linear piezoelectric constitutive coupling",
            "conservation_laws": {
                "ledger_type": "open_system_with_fluxes",
                "general": ["electric_charge", "energy_momentum"],
                "regime_specific": [],
                "scope": "sample + mechanical driver + electrical readout boundary",
                "exchange_terms": ["mechanical_work", "electrical_leakage", "heat"],
            },
            "rate_or_timescale": {"sampling_rate_hz": 1000},
            "damping_or_loss": "dielectric leakage + mechanical damping",
            "observable": "voltage transient",
            "instrument": "calibrated differential electrometer",
            "uncertainty": "propagated calibration and repeatability uncertainty",
            "baseline": "quartz-free control under matched loading",
            "falsifier": "no excess synchronized voltage over quartz-free control",
        },
    }


def test_complete_pathway_is_ready_for_test_not_claim():
    value = pathway()
    assert validate_pathway(value) == []
    assert classify_pathway(value) == InvariantState.READY_FOR_TEST
    receipt = build_invariant_receipt(value)
    assert receipt["state"] == "READY_FOR_TEST"
    assert receipt["claim_allowed"] is False
    assert receipt["structural_coverage"] == 1.0
    assert receipt["token_vazio_components"] == []
    assert len(receipt["source_sha256"]) == 64
    assert len(receipt["receipt_sha256"]) == 64


def test_declared_unknown_is_token_vazio_not_success():
    value = pathway()
    value["components"]["uncertainty"] = TOKEN_VAZIO
    assert validate_pathway(value) == []
    assert classify_pathway(value) == InvariantState.TOKEN_VAZIO
    assert token_vazio_components(value) == ["uncertainty"]


def test_absent_component_is_malformed_and_blocked():
    value = pathway()
    del value["components"]["falsifier"]
    assert any("falsifier" in error for error in validate_pathway(value))
    assert classify_pathway(value) == InvariantState.BLOCKED


def test_claim_promotion_is_blocked():
    value = pathway()
    value["claim_allowed"] = True
    assert any("claim_allowed" in error for error in validate_pathway(value))
    assert classify_pathway(value) == InvariantState.BLOCKED


def test_open_system_requires_exchange_terms():
    value = pathway()
    value["components"]["conservation_laws"]["exchange_terms"] = []
    assert any("exchange_terms" in error for error in validate_pathway(value))


def test_general_conservation_requires_charge_and_energy_momentum():
    value = pathway()
    value["components"]["conservation_laws"]["general"] = ["electric_charge"]
    assert any("energy_momentum" in error for error in validate_pathway(value))


def test_regime_specific_conservation_is_scoped_not_universal():
    value = pathway()
    value["domain"] = "nuclear"
    value["components"]["conservation_laws"]["regime_specific"] = [
        "baryon_number_where_applicable",
        "lepton_number_where_applicable",
    ]
    assert validate_pathway(value) == []
    assert classify_pathway(value) == InvariantState.READY_FOR_TEST


def test_signature_reports_structure_not_truth():
    value = pathway()
    value["components"]["observable"] = TOKEN_VAZIO
    signature = structural_signature(value)
    assert signature["observable"] is False
    assert signature["carrier"] is True
    receipt = build_invariant_receipt(value)
    assert receipt["state"] == TOKEN_VAZIO
    assert receipt["structural_coverage"] < 1.0
