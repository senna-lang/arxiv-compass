"""
論文スコアリングモジュール

提供:
- score_papers(papers, vecs, rated_vecs, profile_vecs, alpha, top_n): α-blend スコアで上位N件を返す
"""

from typing import Any

import numpy as np
from core.similarity import mean_cosine_similarity


def score_papers(
    papers: list[dict[str, Any]],
    vecs: np.ndarray,
    rated_vecs: list[np.ndarray],
    profile_vecs: list[np.ndarray],
    alpha: float,
    top_n: int,
) -> list[dict[str, Any]]:
    """
    各論文の埋め込みベクトルと rated_vecs / profile_vecs の cos 類似度から
    α-blend スコアを計算し、スコア降順で top_n 件を返す。

    score = α × mean_cosine(vec, rated_vecs) + (1-α) × mean_cosine(vec, profile_vecs)
    """
    scored: list[dict[str, Any]] = []
    for paper, vec in zip(papers, vecs):
        instance_score = mean_cosine_similarity(vec, rated_vecs)
        profile_score = mean_cosine_similarity(vec, profile_vecs)
        final_score = alpha * instance_score + (1 - alpha) * profile_score
        scored.append({**paper, "score": round(final_score, 4)})

    scored.sort(key=lambda p: p["score"], reverse=True)
    return scored[:top_n]

def select_with_topic_slots(papers: list[dict[str, Any]], top_n: int, topic_slots: int = 0, topic_min_score: float = 0.55) -> list[dict[str, Any]]:
    by_star = sorted(papers, key=lambda p: p["score"], reverse=True)
    slots = min(max(topic_slots, 0), top_n)
    head = by_star[: top_n - slots]
    head_ids = {p["id"] for p in head}
    pool = sorted([p for p in by_star if p["id"] not in head_ids and p.get("topic_score", 0) >= topic_min_score], key=lambda p: p["topic_score"], reverse=True)[:slots]
    chosen = head_ids | {p["id"] for p in pool}
    picked = (head + pool + [p for p in by_star if p["id"] not in chosen])[:top_n]
    out = []
    for paper in picked:
        item = dict(paper)
        if slots and paper not in pool and item.get("topic_score", 0) < topic_min_score:
            item["matched_topic"] = None
        out.append(item)
    return out


def pick_topic_reservations(candidates: list[dict[str, Any]], exclude_ids: set[str], topic_slots: int, topic_min_score: float) -> list[dict[str, Any]]:
    if topic_slots <= 0:
        return []
    pool = [c for c in candidates if c["id"] not in exclude_ids and c.get("topic_score", 0) >= topic_min_score]
    pool.sort(key=lambda c: c["topic_score"], reverse=True)
    return [dict(c) for c in pool[:topic_slots]]
