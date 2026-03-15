---
id: k-08a416
date: 2026-03-14T13:48:20.552535Z
topic: arXiv新聞アプリ Phase 2実装
plan: 20260312-arxiv-phase-2.md
tasks:
    - 005-map.astro 地図可視化
    - 004-RecommendSection実装
    - 003-recommend.py TDD実装
    - 002-map.py TDD実装
    - 001-embedding_modelをspecter2に移行
tags: []
---

<!-- SOURCE MATERIAL — read this, fill in the sections below, then remove this block. -->
<!--
## Plan: arXiv新聞アプリ Phase 2実装

## Background

Phase 1でratings.jsonへの評価蓄積基盤ができた。
Phase 2ではarXiv論文群をBERTopicで地図化し、ratings履歴から近傍クラスタを推定して
おすすめ論文を自動生成する。ratings 20件以上で本領を発揮する。

## Spec

### scripts/map.py（月次）
1. arXiv APIでcs.CL/cs.LG/cs.AI/cs.CR の過去N件（デフォルト10,000件）を取得
2. abstractをallenai/specter2でEmbedding
3. BERTopicでトピック抽出（UMAP random_state=42、HDBSCAN、c-TF-IDF）
4. 各クラスタのcentroid・UMAP 2D座標・キーワードを集約
5. data/map.jsonに保存

### scripts/recommend.py（週次）
1. ratings.jsonからrating>=2の論文を抽出
2. abstractをspecter2でEmbedding（再計算）
3. map.jsonの各クラスタをinstance-based scoringで評価
   `score(c) = mean(cos_sim(centroid_c, v_i) for v_i in rated_vecs)`
4. ratings件数に応じてinterest_profileスコアと加重合成
   `α = min(1.0, 件数/50)`
   `final = α * instance_score + (1-α) * profile_score`
5. 上位クラスタ内の論文をスコアリングしてrecommendations.jsonに保存

### Astroフロントエンド
- `src/pages/map.astro`: UMAPの2D座標でクラスタを散布図表示（Canvas/SVG）
- `src/components/RecommendSection.astro`: recommendations.jsonを読んで表示

## Key Decisions

Decision: Embeddingモデルをspecter2に統一。Rationale: map.py・recommend.pyで同一ベクトル空間を使う必要がある。parse.pyもspecter2に変更する（config.jsonのembedding_model更新のみ）。

Decision: クラスタの安定識別子はlabel（キーワード文字列）。Rationale: 月次再生成でtopic_idは変わりうる。labelはキーワードベースで意味的に安定。

Decision: map.astroの描画はCanvas（vanilla JS）。Rationale: D3等の外部ライブラリを避けてシンプルに保つ。

## Notes

- BERTopicはUMAP・HDBSCANを内包するため個別インストール不要
- 初回のspecter2 Embeddingは10,000件で数十分かかる
- Phase 3: ratings 50件以上でratings自体をHDBSCANでクラスタリングし興味ペルソナを自動分離

---
## Walkthrough: 005 map.astro 地図可視化

## Key Specification

map.astroでUMAP 2D座標をCanvasに散布図描画。近傍クラスタをオレンジでハイライト。

## What Was Done

- `src/pages/map.astro`: Canvas描画 + ツールチップ + 近傍ハイライト
- `[date].astro`に地図へのリンクを追加

## How It Was Done

`define:vars`でAstroのサーバーサイドデータをクライアントJSに渡す。
UMAP座標をCanvas座標にスケーリングして描画。円サイズはsqrt(size/maxSize)*22。

## Gotchas & Lessons Learned

- `define:vars={{ clustersJson, nearLabelsJson }}`でJSON文字列をクライアントに渡す

## Reusable Patterns

```astro
<script define:vars={{ dataJson }}>
  const data = JSON.parse(dataJson);
  // クライアントサイドで使用
</script>
```

---
## Walkthrough: 004 RecommendSection実装

## Key Specification

RecommendSection.astroを実装。recommendations.jsonを読み込み近傍クラスタとおすすめ論文を表示。

## What Was Done

- `src/lib/types.ts`にCluster/MapData/Recommendation/TopCluster/RecommendationsData型を追加
- `src/lib/data.ts`にgetMap() / getRecommendations()を追加
- `src/components/RecommendSection.astro`を実装（データなし時は非表示）

## How It Was Done

AstroのフロントマターでgetRecommendations()を呼び、nullまたは空配列なら何も描画しない。
クラスタタグはblue、近傍クラスタはハイライト表示。

## Reusable Patterns

```astro
// データなし時に丸ごと非表示
{data && data.recommendations.length > 0 && (
  <section>...</section>
)}
```

---
## Walkthrough: 003 recommend.py TDD実装

## Key Specification

recommend.pyをTDDで実装。instance-based scoring + α加重合成。

## What Was Done

- `scripts/tests/test_recommend.py`: 15テスト（Red→Green）
- `scripts/recommend.py`: compute_instance_score / compute_alpha / compute_final_score / rank_clusters / main を実装

## How It Was Done

各関数を独立してテスト。rank_clustersはscore フィールドを追加して降順ソートして返す。

## Gotchas & Lessons Learned

- rank_clustersはクラスタdictに`score`フィールドを追加して返すため、テストで`"score" in ranked[0]`を確認
- arXiv APIのid_list上限を考慮して100件に制限

## Reusable Patterns

```python
# α加重合成
alpha = min(1.0, n_ratings / 50)
final = alpha * instance_score + (1 - alpha) * profile_score
```

---
## Walkthrough: 002 map.py TDD実装

## Key Specification

map.pyをTDDで実装。build_cluster_dict / generate_label / build_map_outputをユニットテスト済み。

## What Was Done

- `scripts/tests/test_map.py`: 11テスト（Red→Green）
- `scripts/map.py`: fetch_arxiv_papers / generate_label / build_cluster_dict / build_map_output / main を実装

## How It Was Done

BERTopicにUMAP（random_state=42固定）とHDBSCANを明示的に渡して再現性を確保。
ノイズクラスタ（topic_id=-1）はスキップ。

## Gotchas & Lessons Learned

- BERTopicのデフォルトUMAPはrandom_stateが固定されないため、明示的にUMAP(random_state=42)を渡す必要がある
- `pip install bertopic`でumap-learn・hdbscanも自動インストールされる

## Reusable Patterns

```python
# UMAPのrandom_state固定
from umap import UMAP
from hdbscan import HDBSCAN
topic_model = BERTopic(
    umap_model=UMAP(n_components=2, random_state=42, metric="cosine"),
    hdbscan_model=HDBSCAN(min_cluster_size=10, metric="euclidean", prediction_data=True),
)
# ノイズクラスタをスキップ
for topic_id in unique_topics:
    if topic_id == -1:
        continue
```

---
## Walkthrough: 001 embedding_modelをspecter2に移行

## Key Specification

config.jsonのembedding_modelをall-MiniLM-L6-v2からallenai/specter2に変更。

## What Was Done

- `config.json`の`embedding_model`を`"allenai/specter2"`に変更（1行のみ）

## How It Was Done

parse.pyはconfig.jsonからモデル名を読み込むため本体変更不要。

## Gotchas & Lessons Learned

- 既存data/YYYYMMDD.jsonはall-MiniLM-L6-v2製なので、Phase 2移行後はparse.pyを再実行して再生成する必要がある

## Reusable Patterns

なし（設定変更のみ）
-->

## Summary

## Implemented Features

## Key Specification

## Key Learnings

## Reusable Patterns

## Gotchas

## Source Walkthroughs

- .logosyncx/tasks/20260312-arxiv-phase-2/005-mapastro/WALKTHROUGH.md
- .logosyncx/tasks/20260312-arxiv-phase-2/004-recommendsection/WALKTHROUGH.md
- .logosyncx/tasks/20260312-arxiv-phase-2/003-recommendpy-tdd/WALKTHROUGH.md
- .logosyncx/tasks/20260312-arxiv-phase-2/002-mappy-tdd/WALKTHROUGH.md
- .logosyncx/tasks/20260312-arxiv-phase-2/001-embedding_modelspecter2/WALKTHROUGH.md
