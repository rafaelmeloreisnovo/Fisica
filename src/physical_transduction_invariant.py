"""Executable structural invariant for auditable physical transduction pathways.

This module defines an epistemic/structural invariant, not a newly discovered
conserved scalar or force. A pathway is READY_FOR_TEST only when the same
minimum evidence-bearing structure is present across physical domains.
"""
from __future__ import annotations

import argparse
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

TOKEN_VAZIO = "TOKEN_VAZIO"
SCHEMA = "physical_transduction_pathway_v1"

REQUIRED_COMPONENTS = (
    "carrier",
    "medium",
    "scale",
    "phase_state",
    "free_energy_source",
    "coupling_operator",
    "conservation_laws",
    "rate_or_timescale",
    "damping_or_loss",
    "observable",
    "instrument",
    "uncertainty",
    "baseline",
    "falsifier",
)

ALLOWED_LEDGER_TYPES = {"closed_system", "open_system_with_fluxes"}
GENERAL_CONSERVATION = {"electric_charge", "energy_momentum"}


class InvariantState(str, Enum):
    READY_FOR_TEST = "READY_FOR_TEST"
    TOKEN_VAZIO = TOKEN_VAZIO
    BLOCKED = "BLOCKED"


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _present(value: Any) -> bool:
    if value in (None, "", TOKEN_VAZIO):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def _validate_conservation(value: Any) -> list[str]:
    errors: list[str] = []
    if value == TOKEN_VAZIO:
        return errors
    if not isinstance(value, dict):
        return ["components.conservation_laws must be TOKEN_VAZIO or an object"]

    ledger_type = value.get("ledger_type")
    if ledger_type not in ALLOWED_LEDGER_TYPES:
        errors.append(
            "components.conservation_laws.ledger_type must be closed_system or "
            "open_system_with_fluxes"
        )

    general = value.get("general")
    if not isinstance(general, list) or not all(
        isinstance(item, str) and item for item in general
    ):
        errors.append("components.conservation_laws.general must be a non-empty string list")
    else:
        missing = sorted(GENERAL_CONSERVATION.difference(general))
        if missing:
            errors.append(
                "components.conservation_laws.general missing: " + ", ".join(missing)
            )

    scope = value.get("scope")
    if not isinstance(scope, str) or not scope:
        errors.append("components.conservation_laws.scope is required")

    if ledger_type == "open_system_with_fluxes":
        exchange_terms = value.get("exchange_terms")
        if not isinstance(exchange_terms, list) or not exchange_terms:
            errors.append(
                "open_system_with_fluxes requires non-empty exchange_terms"
            )

    regime_specific = value.get("regime_specific", [])
    if not isinstance(regime_specific, list) or not all(
        isinstance(item, str) and item for item in regime_specific
    ):
        errors.append(
            "components.conservation_laws.regime_specific must be a string list"
        )
    return errors


def validate_pathway(payload: Mapping[str, Any]) -> list[str]:
    """Validate contract structure. TOKEN_VAZIO is valid but not promotable."""
    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    pathway_id = payload.get("pathway_id")
    if not isinstance(pathway_id, str) or not pathway_id:
        errors.append("pathway_id must be a non-empty string")
    domain = payload.get("domain")
    if not isinstance(domain, str) or not domain:
        errors.append("domain must be a non-empty string")

    components = payload.get("components")
    if not isinstance(components, dict):
        errors.append("components must be an object")
        return errors

    for name in REQUIRED_COMPONENTS:
        if name not in components:
            errors.append(f"components.{name} is required; use TOKEN_VAZIO if unknown")
            continue
        value = components[name]
        if value != TOKEN_VAZIO and not _present(value):
            errors.append(f"components.{name} must be meaningful or TOKEN_VAZIO")

    if "conservation_laws" in components:
        errors.extend(_validate_conservation(components["conservation_laws"]))
    return errors


def token_vazio_components(payload: Mapping[str, Any]) -> list[str]:
    components = payload.get("components")
    if not isinstance(components, dict):
        return list(REQUIRED_COMPONENTS)
    return [name for name in REQUIRED_COMPONENTS if components.get(name) == TOKEN_VAZIO]


def classify_pathway(payload: Mapping[str, Any]) -> InvariantState:
    if validate_pathway(payload):
        return InvariantState.BLOCKED
    if token_vazio_components(payload):
        return InvariantState.TOKEN_VAZIO
    return InvariantState.READY_FOR_TEST


def structural_signature(payload: Mapping[str, Any]) -> dict[str, bool]:
    """Return the cross-domain invariant signature without asserting truth."""
    components = payload.get("components")
    if not isinstance(components, dict):
        components = {}
    return {
        name: name in components and _present(components.get(name))
        for name in REQUIRED_COMPONENTS
    }


def build_invariant_receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_pathway(payload)
    missing = token_vazio_components(payload)
    state = InvariantState.BLOCKED if errors else classify_pathway(payload)
    signature = structural_signature(payload)
    coverage = sum(signature.values()) / len(REQUIRED_COMPONENTS)

    core: dict[str, Any] = {
        "schema": "physical_transduction_invariant_receipt_v1",
        "pathway_id": payload.get("pathway_id", TOKEN_VAZIO),
        "state": state.value,
        "claim_allowed": False,
        "structural_coverage": coverage,
        "token_vazio_components": missing,
        "validation_errors": errors,
        "signature": signature,
        "source_sha256": sha256(_canonical_json_bytes(payload)).hexdigest(),
        "boundaries": [
            "Structural completeness is not evidence that a mechanism occurs in nature.",
            "READY_FOR_TEST is not MEASURED, causal attribution, replication or new physics.",
            "The invariant is a reusable audit structure, not a new conserved quantity.",
            "Regime-specific conservation laws must be scoped; Z and A are not universal invariants across all particle processes.",
        ],
    }
    core["receipt_sha256"] = sha256(_canonical_json_bytes(core)).hexdigest()
    return core


def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = load_json(args.path)
    receipt = build_invariant_receipt(payload)
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    return 1 if receipt["state"] == InvariantState.BLOCKED.value else 0


if __name__ == "__main__":
    raise SystemExit(main())
