"""baseline 日次 JSON へ shadow 結果を付ける。SPECTER の選出と順序は変えない。"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from core.config import JST, ROOT, load_config
from core.io import save_json

from .predicate import canonical_predicate, context_sha256, shared_state
from .ranking import InvalidJevResult, StaleDailyJson, apply_complete, apply_unavailable, require_digest, sha256_bytes

ATTEMPTS = 2


def classify_failure(error: Exception) -> str:
    if isinstance(error, InvalidJevResult):
        return "invalid_result"
    if type(error).__name__ == "FunctionTimeoutError":
        return "timeout"
    return "inference_error"


def run_shadow(
    daily: dict[str, Any],
    rank: Callable[[list[dict], dict[str, Any]], dict[str, Any]],
    config: dict[str, Any],
    raw_daily: bytes,
    expected_digest: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any], int]:
    """成功・graceful failure は新しい daily を返す。stale は None と exit code 1。"""
    evidence: dict[str, Any] = {
        "date": daily.get("date"),
        "status": "unavailable",
        "reason": None,
        "attempt_count": 0,
        "started_at": datetime.now(JST).isoformat(),
        "finished_at": None,
        "wall_time_ms": None,
        "attempts": [],
        "result_validation": {"expected_paper_count": 20, "returned_paper_count": 0, "complete": False},
        "model": dict(config["shadow_jev"]["model"]),
        "predicate": {
            "id": config["shadow_jev"]["predicate"]["id"],
            "version": config["shadow_jev"]["predicate"]["version"],
            "context_sha256": context_sha256(config),
        },
    }
    started = time.perf_counter()
    try:
        if expected_digest is not None:
            require_digest(sha256_bytes(raw_daily), expected_digest)
    except StaleDailyJson:
        evidence["reason"] = "stale_baseline"
        evidence["finished_at"] = datetime.now(JST).isoformat()
        evidence["wall_time_ms"] = round((time.perf_counter() - started) * 1000)
        return None, evidence, 1

    predicate = canonical_predicate(config)
    request = {
        "state": shared_state(config),
        "question": predicate["question"],
        "options": predicate["options"],
        "batch_size": config["shadow_jev"]["batch_size"],
        "expected_adapter_sha256": config["shadow_jev"]["model"]["adapter_sha256"],
    }
    model = evidence["model"]
    identity = evidence["predicate"]
    failure = "inference_error"
    for attempt in range(1, ATTEMPTS + 1):
        evidence["attempt_count"] = attempt
        attempt_started = time.perf_counter()
        try:
            payload = rank(daily["papers"], request)
            probabilities = payload["probabilities"]
            evidence["attempts"].append({
                "number": attempt,
                "execution_time_ms": payload.get("execution_time_ms", round((time.perf_counter() - attempt_started) * 1000)),
                "gpu": payload.get("gpu", "L4"),
                "peak_cuda_memory_bytes": payload.get("peak_cuda_memory_bytes"),
                "modal_invocation_id": payload.get("modal_invocation_id"),
            })
            updated = apply_complete(daily, probabilities, model, identity)
            evidence["status"] = "complete"
            evidence["reason"] = None
            evidence["result_validation"] = {
                "expected_paper_count": 20,
                "returned_paper_count": len(probabilities),
                "complete": True,
            }
            evidence["finished_at"] = datetime.now(JST).isoformat()
            evidence["wall_time_ms"] = round((time.perf_counter() - started) * 1000)
            return updated, evidence, 0
        except Exception as error:
            failure = classify_failure(error)
            evidence["attempts"].append({
                "number": attempt,
                "execution_time_ms": round((time.perf_counter() - attempt_started) * 1000),
                "gpu": "L4",
                "peak_cuda_memory_bytes": None,
                "modal_invocation_id": None,
                "failure": failure,
            })
    updated = apply_unavailable(daily, failure)
    evidence["reason"] = failure
    evidence["finished_at"] = datetime.now(JST).isoformat()
    evidence["wall_time_ms"] = round((time.perf_counter() - started) * 1000)
    return updated, evidence, 0


def modal_rank(papers: list[dict], request: dict[str, Any]) -> dict[str, Any]:
    from shadow_jev.modal_app import JevRanker, app

    with app.run():
        call = JevRanker().rank.spawn(
            papers,
            request["state"],
            request["question"],
            request["options"],
            request["batch_size"],
            request["expected_adapter_sha256"],
        )
        payload = call.get()
        payload["modal_invocation_id"] = call.object_id
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Attach shadow Jev ranks to one SPECTER daily JSON file")
    parser.add_argument("--date", required=True, help="YYYYMMDD")
    parser.add_argument("--expected-base-sha256")
    parser.add_argument("--evidence", type=Path, default=Path("shadow-jev-run.json"))
    args = parser.parse_args()
    config = load_config()
    path = ROOT / config["output_dir"] / f"{args.date}.json"
    try:
        raw = path.read_bytes()
        daily = json.loads(raw)
    except (OSError, ValueError) as error:
        args.evidence.write_text(
            json.dumps({"date": args.date, "status": "not_run", "reason": "baseline_unreadable",
                        "detail": type(error).__name__}, indent=2) + "\n",
            encoding="utf-8",
        )
        return 1
    updated, evidence, code = run_shadow(daily, modal_rank, config, raw, args.expected_base_sha256)
    args.evidence.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if updated is not None:
        save_json(path, updated)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
