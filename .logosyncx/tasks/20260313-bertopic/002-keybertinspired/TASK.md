---
id: t-bertopic-002
date: 2026-03-13T00:00:00.000000+09:00
title: "プランB: KeyBERTInspired representation導入"
seq: 2
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

`scripts/map.py` の `BERTopic` に `KeyBERTInspired` representation_model を設定し、c-TF-IDF候補をEmbeddingの意味的近さで再ランキングする。

## Why

c-TF-IDF はTF-IDFスコアで語を選ぶため、クラスタのembeddingと意味的に近い語が必ずしも上位に来ない。KeyBERTInspiredはspecter2のembeddingを流用してcos similarityで再ランキングするため、クラスタの意味をより正確に表すキーワードが得られる。

## Scope

- `scripts/map.py`（`BERTopic` 初期化部分のみ）

OUT: CountVectorizer 設定（プランA範囲）、UMAP/HDBSCAN パラメータ、出力スキーマ

## Changes

```python
from bertopic.representation import KeyBERTInspired

representation_model = KeyBERTInspired(
    nr_repr_docs=10,        # 代表文書数（デフォルト5）
    nr_candidate_words=20,  # c-TF-IDFから渡す候補数
    top_n_words=10,         # 最終キーワード数
)
topic_model = BERTopic(
    umap_model=umap_cluster,
    hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer,
    representation_model=representation_model,
    calculate_probabilities=False,
    verbose=True,
)
```

## Acceptance Criteria

- [ ] `npm run map` が正常終了する
- [ ] `data/map.json` の `keywords` がプランA単体より意味的に明確になっている
- [ ] `/map` ページのツールチップでクラスタラベルの品質が向上している

## Checklist

- [ ] プランA（001-academic-stopwords）が完了済みであること
- [ ] `KeyBERTInspired` を import
- [ ] `representation_model` を `BERTopic` に渡す
- [ ] `npm run map`（1000件）で動作確認
- [ ] `data/map.json` の keywords をプランA結果と比較・目視確認

## Notes

- `bertopic.representation` はBERTopic標準同梱。追加依存なし
- specter2のembeddingを流用するため追加のembedding計算は不要。処理時間増加は再ランキングのみ（+10〜20%程度）
- クラスタが小さい場合（論文数が少ない）は代表embeddingが不安定になる可能性あり
- 効果不十分なら `nr_candidate_words` を増やす（30〜50）
