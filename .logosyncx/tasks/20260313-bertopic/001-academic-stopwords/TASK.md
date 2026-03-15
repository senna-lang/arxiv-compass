---
id: t-bertopic-001
date: 2026-03-13T00:00:00.000000+09:00
title: "プランA: 学術ストップワード追加"
seq: 1
status: open
priority: medium
plan: 20260313-bertopic
tags:
  - python
  - bertopic
assignee: ""
completed_at: null
---

## What

`scripts/map.py` の `CountVectorizer` に学術論文特有の汎用語ストップワードを追加し、`min_df` と `max_df` を調整する。

## Why

c-TF-IDF のデフォルト設定では "model", "method", "propose" 等の論文特有汎用語が除去されず、クラスタを特徴づけないキーワードが上位に来てしまう。

## Scope

- `scripts/map.py`（`CountVectorizer` 設定部分のみ）

OUT: BERTopic モデル設定、UMAP/HDBSCAN パラメータ、出力スキーマ

## Changes

```python
ACADEMIC_STOPWORDS = [
    "model", "method", "approach", "propose", "proposed",
    "result", "results", "paper", "work", "task", "performance",
    "training", "dataset", "data", "experiment", "experiments",
    "demonstrate", "achieve", "achieved", "using", "based",
    "learning", "neural", "deep", "large", "new", "existing",
    "different", "various", "show", "present", "study",
]

BASE_STOPWORDS = list(CountVectorizer(stop_words="english").get_stop_words())

vectorizer = CountVectorizer(
    stop_words=BASE_STOPWORDS + ACADEMIC_STOPWORDS,
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.85,
)
```

## Acceptance Criteria

- [ ] `npm run map` が正常終了する
- [ ] `data/map.json` の `keywords` に "model", "method" 等が出現しない
- [ ] `/map` ページのツールチップでクラスタラベルが改善されている

## Checklist

- [ ] `ACADEMIC_STOPWORDS` 定数を `map.py` に追加
- [ ] `CountVectorizer` の `min_df=3`, `max_df=0.85` に変更
- [ ] `npm run map`（1000件）で動作確認
- [ ] `data/map.json` の keywords を目視確認

## Notes

- spaCy は未インストール。sklearn の318語（`stop_words="english"`）をベースとして使用
- `max_df=0.85` の効果が薄い場合は `0.5〜0.7` に下げて再確認
- プランB（KeyBERTInspired）はこのタスク完了後に別タスクで検討
