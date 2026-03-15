---
id: 88d3a4
topic: arXiv新聞アプリ Phase 1実装
tags: []
agent: ""
related: []
tasks_dir: .logosyncx/tasks/20260311-arxiv-phase-1
distilled: true
---

## Background

arXivには毎日数百件の論文が投稿される。daily-newsスキルがtrend.mdを生成しているが、
論文のスコアリング・レーティング蓄積・セマンティック発見の仕組みがない。
Phase 1では「毎日論文を読んで星をつける習慣」を作るための基盤を構築する。

**入力**: daily-newsスキルが生成する`YYYYMMDD-trend.md`（arXiv論文のMarkdownテーブル）
**出力**: Astro製Webアプリ（論文カード + 星UI + 評価データ蓄積）

trend.mdのarXivセクション形式:
```
| [日本語タイトル](https://arxiv.org/abs/2603.08659) | 2603.08659 | 2026-03-10 | Author et al. | ★★★ | タグ | メモ |
```
abstractはtrend.mdに含まれない → arXiv APIで取得する。

## Spec

### scripts/parse.py（毎朝実行）
1. `config.json`の`trend_dir`から`YYYYMMDD-trend.md`を読み込む
2. `## 📄 arXiv 注目論文`セクションのMarkdownテーブルをパース → arXiv IDを抽出
3. arXiv APIで各論文のtitle・abstract・authors・categories・submitted・URLを取得
4. abstractをsentence-transformers（all-MiniLM-L6-v2）でEmbedding
5. `interest_profile`の各文章とcos類似度を計算し平均をscoreとして付与
6. scoreの降順でソートして`data/YYYYMMDD.json`に保存

### Astroアプリ（ローカルdev + hybrid mode）
- `src/pages/index.astro`: 最新日付にリダイレクト
- `src/pages/[date].astro`: 日付別論文一覧（前日/翌日ナビ）
- `src/components/PaperCard.astro`: 論文カード（タイトル/著者/スコア/星UI/abstract展開）
- `src/components/RecommendSection.astro`: Phase 1はstub
- `src/pages/api/rate.ts`: 星評価保存API（ratings.json書き込み + git push）

### ファイル構成
```
config.json, data/ratings.json
scripts/parse.py, scripts/tests/test_parse.py
src/lib/data.ts
src/pages/index.astro, src/pages/[date].astro
src/pages/api/rate.ts
src/components/PaperCard.astro, src/components/RecommendSection.astro
package.json, astro.config.mjs, tsconfig.json
```

## Key Decisions

Decision: Astroをhybridモードで使用。Rationale: API Route（rate.ts）でgit操作が必要なため、SSRが必要。ローカルdev用途なのでnode adapterで十分。

Decision: Phase 1のembedding modelはall-MiniLM-L6-v2。Rationale: Phase 2のmap.py実装前はspecter2との空間統一が不要。軽量・高速で開発サイクルが速い。

Decision: TDD必須（test_parse.pyを先に書く）。Rationale: CLAUDE.mdのコーディングルールに従う。parse_trend_section・compute_score・build_paper_dictをユニットテスト。

Decision: abstractはarXiv APIで取得。Rationale: trend.mdにはabstractが含まれないため。arXiv IDがあれば取得可能。

## Notes

- ratings.jsonはGitで管理 → 履歴が資産になる
- interest_profileはconfig.jsonで管理 → バージョン管理される
- Phase 2以降: map.py（BERTopic）+ recommend.py（instance-based scoring）
- config.jsonのembedding_modelはPhase 2でallenai/specter2に変更する
