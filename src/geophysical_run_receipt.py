"""Deterministic receipt builder for geophysical measurement runs.

The module validates raw CSV channels, calibration metadata and controls, then
emits a hash-pinned receipt. Integrity readiness is not causal attribution.
Synthetic fixtures can exercise the pipeline but can never become evidence.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping, Sequence

TOKEN_VAZIO = "TOKEN_VAZIO"
ALLOWED_DATA_CLASSES = {"synthetic_fixture", "physical_measurement"}
REQUIRED_CHANNELS = ("stress", "acoustic", "electric", "magnetic")
REQUIRED_CONTROL_KEYS = ("quartz_bearing_sample", "quartz_free_control")


@dataclass(frozen=True)
class ChannelSummary:
    channel_id: str
    path: str
    sha256: str
    rows: int
    timestamp_column: str
    value_columns: tuple[str, ...]
    start_s: float
    end_s: float
    duration_s: float
    median_interval_s: float
    median_sample_rate_hz: float | str
    calibration_id: str


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_present(value: Any) -> bool:
    if value in (None, "", TOKEN_VAZIO):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def _require_string(payload: Mapping[str, Any], key: str, errors: list[str]) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"{key} must be a non-empty string")


def validate_manifest_structure(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != "geophysical_run_manifest_v1":
        errors.append("schema must be geophysical_run_manifest_v1")
    if payload.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    _require_string(payload, "run_id", errors)

    data_class = payload.get("data_class")
    if data_class not in ALLOWED_DATA_CLASSES:
        errors.append(f"data_class must be one of {sorted(ALLOWED_DATA_CLASSES)}")

    channels = payload.get("channels")
    if not isinstance(channels, dict):
        errors.append("channels must be an object")
    else:
        for channel_id in REQUIRED_CHANNELS:
            channel = channels.get(channel_id)
            prefix = f"channels.{channel_id}"
            if not isinstance(channel, dict):
                errors.append(f"{prefix} is required")
                continue
            for key in ("path", "timestamp_column", "calibration_id"):
                if not isinstance(channel.get(key), str) or not channel.get(key):
                    errors.append(f"{prefix}.{key} must be a non-empty string")
            value_columns = channel.get("value_columns")
            if (
                not isinstance(value_columns, list)
                or not value_columns
                or not all(isinstance(item, str) and item for item in value_columns)
            ):
                errors.append(f"{prefix}.value_columns must be a non-empty string list")

    controls = payload.get("controls")
    if not isinstance(controls, dict):
        errors.append("controls must be an object")
    else:
        for key in REQUIRED_CONTROL_KEYS:
            control = controls.get(key)
            if not isinstance(control, dict):
                errors.append(f"controls.{key} is required")
                continue
            if not _is_present(control.get("sample_id")):
                errors.append(f"controls.{key}.sample_id is required")
            if not _is_present(control.get("composition_evidence")):
                errors.append(f"controls.{key}.composition_evidence is required")

    tolerance = payload.get("clock_sync_tolerance_s")
    if not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or tolerance < 0:
        errors.append("clock_sync_tolerance_s must be a finite non-negative number")

    return errors


def _read_numeric_csv(
    path: Path,
    timestamp_column: str,
    value_columns: Sequence[str],
) -> tuple[list[float], int]:
    if not path.is_file():
        raise ValueError(f"raw channel file not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        required = {timestamp_column, *value_columns}
        missing = sorted(required.difference(reader.fieldnames))
        if missing:
            raise ValueError(f"CSV {path} missing columns: {missing}")
        timestamps: list[float] = []
        rows = 0
        previous: float | None = None
        for line_number, row in enumerate(reader, start=2):
            try:
                timestamp = float(row[timestamp_column])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"CSV {path}:{line_number} invalid timestamp"
                ) from exc
            if not math.isfinite(timestamp):
                raise ValueError(f"CSV {path}:{line_number} timestamp is not finite")
            if previous is not None and timestamp <= previous:
                raise ValueError(
                    f"CSV {path}:{line_number} timestamps must be strictly increasing"
                )
            for column in value_columns:
                try:
                    value = float(row[column])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"CSV {path}:{line_number} invalid numeric value in {column}"
                    ) from exc
                if not math.isfinite(value):
                    raise ValueError(
                        f"CSV {path}:{line_number} non-finite value in {column}"
                    )
            timestamps.append(timestamp)
            previous = timestamp
            rows += 1
    if rows < 2:
        raise ValueError(f"CSV {path} must contain at least two data rows")
    return timestamps, rows


def summarize_channel(
    manifest_dir: Path,
    channel_id: str,
    config: Mapping[str, Any],
) -> ChannelSummary:
    declared_path = str(config["path"])
    path = (manifest_dir / declared_path).resolve()
    timestamp_column = str(config["timestamp_column"])
    value_columns = tuple(str(value) for value in config["value_columns"])
    timestamps, rows = _read_numeric_csv(path, timestamp_column, value_columns)
    intervals = [b - a for a, b in zip(timestamps, timestamps[1:])]
    interval = median(intervals)
    sample_rate: float | str = TOKEN_VAZIO
    if interval > 0:
        sample_rate = 1.0 / interval
    return ChannelSummary(
        channel_id=channel_id,
        path=declared_path,
        sha256=file_sha256(path),
        rows=rows,
        timestamp_column=timestamp_column,
        value_columns=value_columns,
        start_s=timestamps[0],
        end_s=timestamps[-1],
        duration_s=timestamps[-1] - timestamps[0],
        median_interval_s=interval,
        median_sample_rate_hz=sample_rate,
        calibration_id=str(config["calibration_id"]),
    )


def _physical_gate_missing(payload: Mapping[str, Any]) -> list[str]:
    if payload.get("data_class") != "physical_measurement":
        return []
    required_paths = {
        "device_id": payload.get("device_id"),
        "operator_id": payload.get("operator_id"),
        "location_coarsened": payload.get("location_coarsened"),
        "preregistration_id": payload.get("preregistration_id"),
        "uncertainty_model": payload.get("uncertainty_model"),
    }
    missing = [key for key, value in required_paths.items() if not _is_present(value)]
    return sorted(missing)


def build_receipt(
    payload: Mapping[str, Any],
    manifest_path: str | Path,
) -> dict[str, Any]:
    errors = validate_manifest_structure(payload)
    if errors:
        raise ValueError("; ".join(errors))

    manifest = Path(manifest_path).resolve()
    manifest_dir = manifest.parent
    channels = {
        channel_id: summarize_channel(manifest_dir, channel_id, payload["channels"][channel_id])
        for channel_id in REQUIRED_CHANNELS
    }

    starts = [summary.start_s for summary in channels.values()]
    ends = [summary.end_s for summary in channels.values()]
    overlap_start = max(starts)
    overlap_end = min(ends)
    start_skew = max(starts) - min(starts)
    end_skew = max(ends) - min(ends)
    tolerance = float(payload["clock_sync_tolerance_s"])
    synchronization_ok = (
        overlap_end > overlap_start
        and start_skew <= tolerance
        and end_skew <= tolerance
    )

    physical_missing = _physical_gate_missing(payload)
    data_class = str(payload["data_class"])
    if data_class == "synthetic_fixture":
        evidence_state = "SYNTHETIC_FIXTURE"
    elif physical_missing:
        evidence_state = TOKEN_VAZIO
    elif not synchronization_ok:
        evidence_state = "BLOCKED_CLOCK_SYNC"
    else:
        evidence_state = "READY_FOR_ANALYSIS"

    channel_payload = {
        channel_id: {
            "path": summary.path,
            "sha256": summary.sha256,
            "rows": summary.rows,
            "timestamp_column": summary.timestamp_column,
            "value_columns": list(summary.value_columns),
            "start_s": summary.start_s,
            "end_s": summary.end_s,
            "duration_s": summary.duration_s,
            "median_interval_s": summary.median_interval_s,
            "median_sample_rate_hz": summary.median_sample_rate_hz,
            "calibration_id": summary.calibration_id,
        }
        for channel_id, summary in sorted(channels.items())
    }

    receipt_core: dict[str, Any] = {
        "schema": "geophysical_run_receipt_v1",
        "run_id": payload["run_id"],
        "data_class": data_class,
        "claim_allowed": False,
        "evidence_state": evidence_state,
        "winner": TOKEN_VAZIO,
        "manifest_path": manifest.name,
        "manifest_sha256": file_sha256(manifest),
        "channels": channel_payload,
        "controls": payload["controls"],
        "clock": {
            "tolerance_s": tolerance,
            "start_skew_s": start_skew,
            "end_skew_s": end_skew,
            "overlap_start_s": overlap_start,
            "overlap_end_s": overlap_end,
            "overlap_duration_s": max(0.0, overlap_end - overlap_start),
            "synchronization_ok": synchronization_ok,
        },
        "physical_gate": {
            "missing": physical_missing,
            "ready_for_analysis": evidence_state == "READY_FOR_ANALYSIS",
        },
        "boundaries": [
            "Synthetic fixtures are pipeline tests, not physical evidence.",
            "Integrity and synchronization do not identify a causal mechanism.",
            "READY_FOR_ANALYSIS does not authorize a scientific claim.",
            "A causal winner requires preregistration, uncertainty, baselines, falsifiers, and analysis results.",
        ],
    }
    receipt_core["receipt_sha256"] = sha256(
        canonical_json_bytes(receipt_core)
    ).hexdigest()
    return receipt_core


def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _write_json(value: Mapping[str, Any], output: str | None) -> None:
    text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate-run")
    validate.add_argument("manifest")
    validate.add_argument("--output")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "validate-run":
        payload = load_json(args.manifest)
        receipt = build_receipt(payload, args.manifest)
        _write_json(receipt, args.output)
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
