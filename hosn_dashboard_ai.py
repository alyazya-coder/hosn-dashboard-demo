"""Cloud-safe loading and inference helpers for the HOSN dashboard.

This module intentionally has no Mininet-WiFi or VM dependency. It loads the
accepted measured-data model and routes decisions through the same normalized
feature contract used during training.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import joblib

import hosn_heterogeneous_controller as controller


FEATURE_ORDER = tuple(controller.AI_FEATURE_ORDER)
WIFI_SERVICE_FLOOR_DBM = -80.0
EMULATED_5G_SERVICE_FLOOR_DBM = -105.0
REQUIRED_TRAINING_DATA_KIND = controller.REQUIRED_TRAINING_DATA_KIND


@dataclass(frozen=True)
class ModelBundle:
    model: Any
    report: dict[str, Any]
    model_path: Path
    report_path: Path
    sha256: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_model_bundle(root: Path) -> ModelBundle:
    """Load only an accepted measured-data model with an intact hash."""
    candidates = sorted(
        (root / "results").glob(
            "measured_dataset_campaign_*/hosn_conflict_ai_model.joblib"
        ),
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            "No results/measured_dataset_campaign_*/hosn_conflict_ai_model.joblib was found."
        )

    for model_path in candidates:
        report_path = model_path.with_name("conflict_ai_training_report.json")
        if not report_path.is_file():
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("acceptance_gate", {}).get("accepted") is not True:
            continue
        if report.get("synthetic_data") is not False:
            continue
        if report.get("label_source") != "HUMAN_PAIRED_OUTCOME_REVIEW":
            continue
        if tuple(report.get("features", ())) != FEATURE_ORDER:
            raise ValueError("Training report feature order does not match the controller contract.")

        actual_hash = _sha256(model_path)
        if report.get("model_sha256") != actual_hash:
            raise ValueError("Model hash does not match conflict_ai_training_report.json.")

        model = joblib.load(model_path)
        if getattr(model, "hosn_schema_version", None) != controller.MODEL_SCHEMA_VERSION:
            raise ValueError("Model schema version does not match the HOSN controller.")
        if tuple(getattr(model, "feature_order", ())) != FEATURE_ORDER:
            raise ValueError("Model feature order does not match the HOSN controller.")
        if getattr(model, "training_data_kind", None) != REQUIRED_TRAINING_DATA_KIND:
            raise ValueError("Model was not trained on the measured HOSN data contract.")

        return ModelBundle(model, report, model_path, report_path, actual_hash)

    raise ValueError("No accepted measured-data model passed the dashboard validation checks.")


def load_scenario_summaries(root: Path) -> dict[str, dict[str, Any]]:
    """Load the newest real recording summary for scenarios 1, 2, and 3."""
    paths = sorted(
        (root / "results").glob(
            "atp_recording_demo_*/scenario_*/recording_summary.json"
        ),
        reverse=True,
    )
    scenarios: dict[str, dict[str, Any]] = {}
    for path in paths:
        summary = json.loads(path.read_text(encoding="utf-8"))
        number = str(summary.get("recording_demo", {}).get("scenario_number", ""))
        if number in {"1", "2", "3"} and number not in scenarios:
            summary["_dashboard_source_path"] = str(path.relative_to(root))
            scenarios[number] = summary

    missing = sorted({"1", "2", "3"} - set(scenarios))
    if missing:
        raise FileNotFoundError(
            "Missing real recording summary file(s) for scenario(s): " + ", ".join(missing)
        )
    return {number: scenarios[number] for number in ("1", "2", "3")}


def final_recording_check(summary: Mapping[str, Any]) -> dict[str, Any]:
    checks = summary.get("recording_checks", ())
    for item in reversed(checks):
        if item.get("final") is True:
            return dict(item)
    if checks:
        return dict(checks[-1])
    return {
        "controller_decision": summary.get("controller_decision", {}),
        "action": summary.get("action"),
        "final": True,
    }


def recorded_features(summary: Mapping[str, Any]) -> dict[str, Any]:
    check = final_recording_check(summary)
    decision = check.get("controller_decision", {})
    result = decision.get("controller_result", {})
    features = result.get("features")
    if not isinstance(features, dict):
        features = {}
    return {name: features.get(name) for name in FEATURE_ORDER}


def _number_or_none(value: Any) -> Any:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _raw_signal(margin: Any, floor: float) -> float | None:
    value = _number_or_none(margin)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) + floor
    return None


def decision_from_features(features: Mapping[str, Any], model: Any = None):
    """Run the exact rules-first controller on normalized dashboard features."""
    values = {name: _number_or_none(features.get(name)) for name in FEATURE_ORDER}
    current = controller.AccessObservation(
        access_name="wifi",
        technology="Wi-Fi RSSI",
        signal_dbm=_raw_signal(values["current_signal_margin_db"], WIFI_SERVICE_FLOOR_DBM),
        service_floor_dbm=WIFI_SERVICE_FLOOR_DBM,
        latency_ms=values["current_latency_ms"],
        loss_pct=values["current_loss_pct"],
        trend_db_per_s=values["current_trend_db_per_s"],
    )
    candidate = controller.AccessObservation(
        access_name="emulated_5g",
        technology="emulated cellular/5G-like IP path",
        signal_dbm=_raw_signal(
            values["candidate_signal_margin_db"], EMULATED_5G_SERVICE_FLOOR_DBM
        ),
        service_floor_dbm=EMULATED_5G_SERVICE_FLOOR_DBM,
        latency_ms=values["candidate_latency_ms"],
        loss_pct=values["candidate_loss_pct"],
        trend_db_per_s=values["candidate_trend_db_per_s"],
    )
    return controller.decide(current, candidate, ai_model=model)

