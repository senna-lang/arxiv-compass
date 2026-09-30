"""shadow Jev の日次 JSON 契約。Modal も GPU も使わない。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from shadow_jev.cli import run_shadow
from shadow_jev.predicate import context_sha256, shared_state
from shadow_jev.ranking import (
    InvalidJevResult,
    StaleDailyJson,
    apply_complete,
    apply_unavailable,
    require_digest,
    sha256_bytes,
)

MODEL = {
    "base_id": "Qwen/Qwen3-4B-Instruct-2507",
    "base_revision": "a" * 40,
    "adapter_id": "e2-lr-1e-4-epoch-3-quarter-3",
    "adapter_sha256": "b" * 64,
    "inference_version": "1",
}
PREDICATE = {
    "id": "arxiv-current-research-usefulness",
    "version": "1",
    "context_sha256": "c" * 64,
}


def daily(scores):
    return {
        "date": "2026-09-30",
        "papers": [
            {"id": f"p{index}", "score": score, "title": f"paper {index}"}
            for index, score in enumerate(scores, start=1)
        ],
        "meta": {"total": len(scores), "model": "allenai/specter2_base"},
    }


def probabilities(papers, values):
    return {paper["id"]: value for paper, value in zip(papers, values)}


class TestCompleteResult:
    def test_preserves_specter_order_and_scores(self):
        source = daily([0.9 - index * 0.01 for index in range(20)])
        values = [index / 19 for index in range(20)]
        result = apply_complete(source, probabilities(source["papers"], values), MODEL, PREDICATE)

        assert [paper["id"] for paper in result["papers"]] == [paper["id"] for paper in source["papers"]]
        assert [paper["score"] for paper in result["papers"]] == [paper["score"] for paper in source["papers"]]
        assert "jev" not in source["papers"][0]
        assert "jev" not in source["meta"]

    def test_ranks_are_contiguous_and_delta_matches(self):
        source = daily([0.5] * 20)
        values = [index / 19 for index in range(20)]
        result = apply_complete(source, probabilities(source["papers"], values), MODEL, PREDICATE)

        ranks = [paper["jev"]["rank"] for paper in result["papers"]]
        assert sorted(ranks) == list(range(1, 21))
        for index, paper in enumerate(result["papers"], start=1):
            assert paper["jev"]["specter_rank"] == index
            assert paper["jev"]["rank_delta"] == index - paper["jev"]["rank"]
        assert result["papers"][0]["jev"]["rank"] == 20
        assert result["papers"][-1]["jev"]["rank"] == 1

    def test_ties_keep_lower_specter_rank_ahead(self):
        source = daily([0.5] * 20)
        values = [0.5] * 20
        result = apply_complete(source, probabilities(source["papers"], values), MODEL, PREDICATE)

        assert [paper["jev"]["rank"] for paper in result["papers"]] == list(range(1, 21))
        assert all(paper["jev"]["rank_delta"] == 0 for paper in result["papers"])

    def test_identity_is_written_only_on_complete(self):
        source = daily([0.5] * 20)
        result = apply_complete(source, probabilities(source["papers"], [0.1] * 20), MODEL, PREDICATE)

        assert result["meta"]["jev"] == {"status": "complete", "model": MODEL, "predicate": PREDICATE}
        assert result["meta"]["model"] == "allenai/specter2_base"


class TestUnavailableResult:
    @pytest.mark.parametrize(
        ("builder", "reason"),
        [
            (lambda papers: {}, "invalid_result"),
            (lambda papers: {papers[0]["id"]: 0.5}, "invalid_result"),
            (lambda papers: {**probabilities(papers, [0.5] * 20), "extra": 0.5}, "invalid_result"),
            (lambda papers: {**probabilities(papers, [0.5] * 19), papers[-1]["id"]: math_nan()}, "invalid_result"),
            (lambda papers: probabilities(papers, [-0.01] + [0.5] * 19), "invalid_result"),
            (lambda papers: probabilities(papers, [True] + [0.5] * 19), "invalid_result"),
        ],
    )
    def test_invalid_response_writes_no_partial_ranks(self, builder, reason):
        source = daily([0.5] * 20)
        source["papers"][0]["jev"] = {"rank": 1}
        with pytest.raises(InvalidJevResult):
            apply_complete(source, builder(source["papers"]), MODEL, PREDICATE)
        result = apply_unavailable(source, reason)

        assert result["meta"]["jev"] == {"status": "unavailable", "reason": reason}
        assert all("jev" not in paper for paper in result["papers"])
        assert "model" not in result["meta"]["jev"]

    def test_timeout_and_inference_error_are_atomic(self):
        source = daily([0.5] * 20)
        source["papers"][3]["jev"] = {"rank": 9}
        for reason in ("timeout", "inference_error"):
            result = apply_unavailable(source, reason)
            assert result["meta"]["jev"] == {"status": "unavailable", "reason": reason}
            assert all("jev" not in paper for paper in result["papers"])

    def test_wrong_selection_size_is_invalid(self):
        source = daily([0.5] * 19)
        with pytest.raises(InvalidJevResult):
            apply_complete(source, probabilities(source["papers"], [0.5] * 19), MODEL, PREDICATE)


class TestDigest:
    def test_matching_digest_is_accepted(self):
        raw = b'{"date":"2026-09-30"}'
        require_digest(sha256_bytes(raw), sha256_bytes(raw))

    def test_mismatch_rejects_update(self):
        with pytest.raises(StaleDailyJson):
            require_digest(sha256_bytes(b"new"), sha256_bytes(b"baseline"))


def math_nan():
    return float("nan")


def shadow_config():
    return {
        "interest_profile": ["LLM inference"],
        "shadow_jev": {
            "model": MODEL,
            "predicate": {**PREDICATE, "current_project_context": ["tree-packed inference"], "preference": "Act on concrete decisions.", "question": "Useful now?", "options": ["No", "Yes"]},
            "batch_size": 2,
        },
    }


class FunctionTimeoutError(Exception):
    pass


class TestShadowRun:
    def test_second_attempt_can_complete(self):
        source = daily([0.5] * 20)
        calls = {"n": 0}

        def rank(papers, request):
            calls["n"] += 1
            if calls["n"] == 1:
                raise FunctionTimeoutError("attempt timed out")
            return {"probabilities": {paper["id"]: 0.2 for paper in papers}, "execution_time_ms": 10, "gpu": "L4"}

        updated, evidence, code = run_shadow(source, rank, shadow_config(), b"{}", None)
        assert code == 0
        assert evidence["status"] == "complete"
        assert evidence["attempt_count"] == 2
        assert updated["meta"]["jev"]["status"] == "complete"
        assert updated["meta"]["jev"]["predicate"]["context_sha256"] == context_sha256(shadow_config())

    def test_two_timeouts_are_atomic(self):
        source = daily([0.5] * 20)

        def rank(papers, request):
            raise FunctionTimeoutError("timed out")

        updated, evidence, code = run_shadow(source, rank, shadow_config(), b"{}", None)
        assert code == 0
        assert evidence["reason"] == "timeout"
        assert evidence["attempt_count"] == 2
        assert updated["meta"]["jev"] == {"status": "unavailable", "reason": "timeout"}
        assert all("jev" not in paper for paper in updated["papers"])

    def test_stale_digest_does_not_rank_or_write(self):
        source = daily([0.5] * 20)

        def rank(papers, request):
            raise AssertionError("stale baseline must not call Jev")

        updated, evidence, code = run_shadow(source, rank, shadow_config(), b"baseline", "different")
        assert updated is None
        assert code == 1
        assert evidence["reason"] == "stale_baseline"

    def test_predicate_hash_changes_when_project_context_changes(self):
        config = shadow_config()
        changed = shadow_config()
        changed["shadow_jev"]["predicate"]["current_project_context"] = ["different project"]
        assert context_sha256(config) != context_sha256(changed)
        assert "Current project:" in shared_state(config)
