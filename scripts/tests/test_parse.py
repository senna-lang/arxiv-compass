"""
scripts/parse.py のユニットテスト

テスト対象:
- parse_trend_section: trend.mdのarXivテーブルからarXiv IDリストを抽出
- compute_score: abstractベクトルとinterest_profileベクトルのcos類似度平均を計算
- build_paper_dict: 論文データをJSONスキーマ準拠のdictに変換
"""

import sys
import os
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parse import parse_trend_section, compute_score, build_paper_dict


SAMPLE_TREND_MD = """
# トレンドネタ: 2026-03-11

## 📄 arXiv 注目論文

### 注目論文

| タイトル（日本語訳） | arXiv ID | 投稿日時 | 著者 | 興味度 | タグ | メモ |
|---------------------|----------|---------|------|--------|-----|------|
| [効率的なアテンション](https://arxiv.org/abs/2603.08659) | 2603.08659 | 2026-03-10 | Alice Smith et al. (MIT) | ★★★ | LLM | スパースアテンション |
| [教師なしRL](https://arxiv.org/abs/2603.08660) | 2603.08660 | 2026-03-10 | Bob Jones et al. (CMU) | ★★★ | RL | スケーリング |
| [長文脈推論](https://arxiv.org/abs/2603.08453) | 2603.08453 | 2026-03-09 | Carol Lee (Stanford) | ★★☆ | Infra | KVキャッシュ |

## 他のセクション

ここはarXivセクションではないのでパース不要。
"""

SAMPLE_TREND_MD_NO_ARXIV = """
# トレンドネタ: 2026-03-11

## 📰 ニュース

特にarXivセクションなし。
"""


class TestParseTrendSection:
    def test_extracts_arxiv_ids(self):
        ids = parse_trend_section(SAMPLE_TREND_MD)
        assert ids == ["2603.08659", "2603.08660", "2603.08453"]

    def test_returns_empty_when_no_arxiv_section(self):
        ids = parse_trend_section(SAMPLE_TREND_MD_NO_ARXIV)
        assert ids == []

    def test_returns_empty_on_empty_string(self):
        ids = parse_trend_section("")
        assert ids == []

    def test_deduplicates_ids(self):
        md = SAMPLE_TREND_MD.replace("2603.08660", "2603.08659")
        ids = parse_trend_section(md)
        assert len(ids) == len(set(ids))


class TestComputeScore:
    def test_identical_vectors_score_one(self):
        v = np.array([1.0, 0.0, 0.0])
        score = compute_score(v, [v, v])
        assert abs(score - 1.0) < 1e-6

    def test_orthogonal_vectors_score_zero(self):
        abstract_vec = np.array([1.0, 0.0, 0.0])
        profile_vecs = [np.array([0.0, 1.0, 0.0])]
        score = compute_score(abstract_vec, profile_vecs)
        assert abs(score) < 1e-6

    def test_score_is_average_of_similarities(self):
        abstract_vec = np.array([1.0, 0.0, 0.0])
        p1 = np.array([1.0, 0.0, 0.0])   # cos_sim = 1.0
        p2 = np.array([0.0, 1.0, 0.0])   # cos_sim = 0.0
        score = compute_score(abstract_vec, [p1, p2])
        assert abs(score - 0.5) < 1e-6

    def test_score_between_zero_and_one(self):
        rng = np.random.default_rng(42)
        abstract_vec = rng.random(128)
        profile_vecs = [rng.random(128) for _ in range(5)]
        score = compute_score(abstract_vec, profile_vecs)
        assert 0.0 <= score <= 1.0


class TestBuildPaperDict:
    def _sample_arxiv_result(self):
        result = MagicMock()
        result.entry_id = "https://arxiv.org/abs/2603.08659v1"
        result.title = "Efficient Attention via Sparse Patterns"
        result.summary = "We propose a sparse attention mechanism..."
        author1 = MagicMock()
        author1.name = "Alice Smith"
        author2 = MagicMock()
        author2.name = "Bob Jones"
        result.authors = [author1, author2]
        result.categories = ["cs.CL", "cs.LG"]
        result.published = MagicMock()
        result.published.strftime = MagicMock(return_value="2026-03-10")
        result.links = [
            MagicMock(href="https://arxiv.org/abs/2603.08659", rel="alternate"),
        ]
        return result

    def test_required_keys_present(self):
        paper = build_paper_dict(self._sample_arxiv_result(), score=0.82)
        for key in ["id", "title", "authors", "abstract", "url", "categories", "submitted", "score"]:
            assert key in paper, f"Missing key: {key}"

    def test_id_stripped_of_version(self):
        paper = build_paper_dict(self._sample_arxiv_result(), score=0.82)
        assert paper["id"] == "2603.08659"
        assert "v1" not in paper["id"]

    def test_score_value(self):
        paper = build_paper_dict(self._sample_arxiv_result(), score=0.82)
        assert abs(paper["score"] - 0.82) < 1e-6

    def test_authors_is_list_of_strings(self):
        paper = build_paper_dict(self._sample_arxiv_result(), score=0.5)
        assert isinstance(paper["authors"], list)
        assert all(isinstance(a, str) for a in paper["authors"])

    def test_categories_is_list(self):
        paper = build_paper_dict(self._sample_arxiv_result(), score=0.5)
        assert isinstance(paper["categories"], list)
