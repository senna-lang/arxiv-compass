---
id: 6f247a
topic: fetch_daily.py 実装完了
tags:
    - python
    - arxiv
agent: claude-code
related: []
tasks_dir: .logosyncx/tasks/20260315-fetch_dailypy
distilled: false
---

## Background

外部の `daily-news` skill が生成する `trend.md` への依存をなくし、arXiv API から直接最新論文を取得して
ユーザーのレーティングと interest_profile の α-blend スコアでトップ20件を選ぶ
`scripts/fetch_daily.py` を新規作成した。

## Spec

- `scripts/fetch_daily.py`: メインスクリプト（TDD実装）
- `scripts/tests/test_fetch_daily.py`: 14テスト全通過
- `config.jsonc`: `fetch_daily` セクション追加（look_back_days=2, max_candidates=300, top_n=20, dedupe_days=30）
- `package.json`: `"daily": "python scripts/fetch_daily.py"` 追加

スコアリング: `α = min(1.0, n_high_rated/50)`, `score = α×instance + (1-α)×profile`

## Key Decisions

- Decision: score_papers は純粋関数として設計。Rationale: テスタビリティ確保とDDD原則に従うため。
- Decision: load_seen_ids は days パラメータで除外期間を制御。Rationale: 日付フィルタで古い論文IDは無視し、コールドスタート時も正しく動作するため。
- Decision: arXiv API の SubmittedDate降順で取得し、cutoff より古い時点で break。Rationale: 不要な API コールを抑制するため。

## Notes

- 出力スキーマは parse.py と互換（source: "fetch_daily" で識別可能）
- rated_vecs が空で α=1 のとき instance_score=0.0 → profile-only 相当になる（コールドスタート安全）
