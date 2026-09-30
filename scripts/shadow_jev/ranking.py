"""SPECTER 日次 JSON へ Jev 順位を付ける純粋関数。Modal もモデルも呼ばない。"""
from __future__ import annotations

import hashlib
import math
from copy import deepcopy
from typing import Any

UNAVAILABLE_REASONS = frozenset({"timeout", "inference_error", "invalid_result"})


class InvalidJevResult(ValueError):
    """20 件全体の順位として使えない Jev 応答。"""


class StaleDailyJson(ValueError):
    """baseline が commit した日次 JSON と digest が一致しない。"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_digest(actual: str, expected: str) -> None:
    if actual != expected:
        raise StaleDailyJson("daily JSON digest does not match the baseline commit")


def apply_complete(
    daily: dict[str, Any],
    probabilities: dict[str, float],
    model: dict[str, str],
    predicate: dict[str, str],
) -> dict[str, Any]:
    """SPECTER 順と score を保ったまま、全論文へ jev を付ける。入力は変更しない。"""
    result = deepcopy(daily)
    papers = result["papers"]
    ranks = _ranks(papers, probabilities)
    for paper, fields in zip(papers, ranks):
        paper.pop("jev", None)
        paper["jev"] = fields
    result.setdefault("meta", {})["jev"] = {
        "status": "complete",
        "model": dict(model),
        "predicate": dict(predicate),
    }
    return result


def apply_unavailable(daily: dict[str, Any], reason: str) -> dict[str, Any]:
    """全 paper.jev を除き、日次 metadata だけを unavailable にする。入力は変更しない。"""
    if reason not in UNAVAILABLE_REASONS:
        raise ValueError(f"unknown unavailable reason: {reason}")
    result = deepcopy(daily)
    for paper in result["papers"]:
        paper.pop("jev", None)
    result.setdefault("meta", {})["jev"] = {"status": "unavailable", "reason": reason}
    return result


def _ranks(papers: list[dict[str, Any]], probabilities: dict[str, float]) -> list[dict[str, Any]]:
    ids = [paper["id"] for paper in papers]
    if len(ids) != 20 or len(set(ids)) != 20:
        raise InvalidJevResult("SPECTER selection must contain exactly 20 unique papers")
    if set(probabilities) != set(ids):
        raise InvalidJevResult("Jev result paper IDs do not match the SPECTER selection")
    scored = []
    for specter_rank, paper in enumerate(papers, start=1):
        probability = probabilities[paper["id"]]
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise InvalidJevResult("relevance probability must be a finite number")
        value = float(probability)
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise InvalidJevResult("relevance probability must be finite and within [0, 1]")
        scored.append((value, specter_rank, paper["id"]))
    order = sorted(scored, key=lambda item: (-item[0], item[1]))
    by_id = {
        paper_id: {
            "specter_rank": specter_rank,
            "rank": rank,
            "rank_delta": specter_rank - rank,
            "relevance_probability": probability,
        }
        for rank, (probability, specter_rank, paper_id) in enumerate(order, start=1)
    }
    return [by_id[paper["id"]] for paper in papers]
