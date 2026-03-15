---
id: k-7c8af0
date: 2026-03-14T13:48:15.796068Z
topic: arXiv新聞アプリ Phase 1実装
plan: 20260311-arxiv-phase-1.md
tasks:
    - 006-星評価APIと動作確認
    - 005-日付別ページ実装
    - 004-PaperCardコンポーネント実装
    - 003-Astroデータアクセス層実装
    - 002-parse.py TDD実装
    - 001-プロジェクト基盤セットアップ
tags: []
---

<!-- SOURCE MATERIAL — read this, fill in the sections below, then remove this block. -->
<!--
## Plan: arXiv新聞アプリ Phase 1実装

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

---
## Walkthrough: 006 星評価APIと動作確認

## Key Specification

POST /api/rate でratings.jsonに星評価を保存し、git add/commit/pushする。

## What Was Done

- `src/pages/api/rate.ts`: 評価保存 + git push（best effort）

## How It Was Done

- readFileSync/writeFileSyncで同期的にratings.jsonを読み書き
- execSyncでgit操作（失敗してもAPIは200を返す）

## Gotchas & Lessons Learned

- execSyncはstdio: "pipe"を指定しないとgitの出力がサーバーのstdoutに出てしまう
- git pushはネットワーク状況で失敗するのでtry/catchでbest effort処理

## Reusable Patterns

```ts
// best effort git push
try {
  execSync(`git add data/ratings.json && git commit -m "rate: ${dateStr}" && git push`, {
    cwd: process.cwd(),
    stdio: "pipe",
  });
} catch {
  // 失敗してもAPIは成功を返す
}
```

---
## Walkthrough: 005 日付別ページ実装

## Key Specification

index.astro（最新日付へリダイレクト）+ [date].astro（日付別論文一覧）を実装。

## What Was Done

- `src/pages/index.astro`: getAvailableDates()で最新日付を取得してリダイレクト
- `src/pages/[date].astro`: 日付別論文一覧、前日/翌日ナビ、PaperCard/RecommendSection利用

## How It Was Done

- [date].astroは `export const prerender = false` でSSRモード
- 前日/翌日はgetAvailableDates()のindexで判定

## Gotchas & Lessons Learned

- `<script src="/rate.js">` はpublicファイルへの参照なので `is:inline` が必要（Astroのバンドル対象外にする）
- Astroのリダイレクトは `return Astro.redirect(...)` で行う（returnが必要）

## Reusable Patterns

```astro
// SSRページの基本形
export const prerender = false;
const { date } = Astro.params;
if (!date) return Astro.redirect("/");
```

---
## Walkthrough: 004 PaperCardコンポーネント実装

## Key Specification

PaperCard.astro（論文カード）・RecommendSection.astro（stub）・public/rate.js（星クリックAPI呼び出し）を実装。

## What Was Done

- `src/components/PaperCard.astro`: タイトル/著者/スコア/星UI/abstract展開
- `src/components/RecommendSection.astro`: Phase 2用のstub
- `public/rate.js`: 星クリック → POST /api/rate + 楽観的UI更新

## How It Was Done

- 星UIはAstroでHTMLに初期状態を埋め込み、rate.jsでインタラクティブにする
- 楽観的UI更新: API呼び出し前にUIを更新し、失敗時に元に戻す

## Gotchas & Lessons Learned

- `<script src="/rate.js">` でpublicの静的ファイルを読み込む
- Astroのscopd CSSは`<style>`タグに書くだけで自動スコープされる

## Reusable Patterns

```js
// 楽観的UI更新パターン
updateStars(container, rating);  // 先に更新
const res = await fetch(...);
if (!res.ok) updateStars(container, prev);  // 失敗時に戻す
```

---
## Walkthrough: 003 Astroデータアクセス層実装

## Key Specification

src/lib/types.ts（型定義）+ src/lib/data.ts（データ読み込み関数）を実装。

## What Was Done

- `src/lib/types.ts`: Paper / Rating / DailyData / RatingsData 型を定義
- `src/lib/data.ts`: getAvailableDates / getPapersForDate / getRatings / getRatingMap を実装
- `tsconfig.json` に `"types": ["node"]` を追加
- `@types/node` を devDependencies に追加

## How It Was Done

node:fs / node:path をimportしてファイル読み込み。エラーは全て catch して空配列/Mapを返す。
bun run build で型チェックとビルドを確認。

## Gotchas & Lessons Learned

- AstroのデフォルトtsonfigではNode.jsの型が含まれない → `@types/node` + `"types": ["node"]`が必要

## Reusable Patterns

```ts
// 全エラーをcatchして安全なデフォルト値を返すパターン
export function getAvailableDates(): string[] {
  try {
    return readdirSync(DATA_DIR)
      .filter((f) => /^\d{8}\.json$/.test(f))
      .map((f) => f.replace(".json", ""))
      .sort();
  } catch {
    return [];
  }
}
```

---
## Walkthrough: 002 parse.py TDD実装

## Key Specification

trend.mdのMarkdownテーブルからarXiv IDを抽出し、arXiv APIでabstractを取得、
sentence-transformersでスコアリングしてdata/YYYYMMDD.jsonを生成する。

## What Was Done

- `scripts/tests/test_parse.py`: 13テスト（TDD Red→Green）
- `scripts/parse.py`: parse_trend_section / compute_score / build_paper_dict / main を実装

## How It Was Done

1. テストを先に書いてModuleNotFoundError確認（Red）
2. parse.py実装後にarxivライブラリ未インストールで再度失敗
3. `pip install arxiv sentence-transformers numpy`でインストール
4. `MagicMock(name=...)` がMockの識別名であり属性ではないことを発見 → テスト修正

## Gotchas & Lessons Learned

- `MagicMock(name="Alice")` はデバッグ名。`.name = "Alice"` で明示的に設定する必要がある
- `model.encode()` はndarrayを返すがPyrightは`list[ndarray]`と認識しないため`list()`でラップ
- arXiv IDの正規表現: `^\d{4}\.\d{4,5}$`（4桁.4〜5桁）
- entry_id末尾の`v1`除去: `re.sub(r"v\d+$", "", raw_id)`

## Reusable Patterns

```python
# MagicMockの属性設定
author = MagicMock()
author.name = "Alice Smith"  # MagicMock(name=...) ではなくこちら

# arXiv IDの抽出（テーブル2列目）
cols = [c.strip() for c in line.split("|")]
if re.match(r"^\d{4}\.\d{4,5}$", cols[2]):
    ...

# cos類似度スコアリング
def compute_score(abstract_vec, profile_vecs):
    sims = [cosine_similarity(abstract_vec, pv) for pv in profile_vecs]
    return float(np.mean(sims))
```

---
## Walkthrough: 001 プロジェクト基盤セットアップ

## Key Specification

TASK.md: config.json・package.json・astro.config.mjs・tsconfig.json・data/ratings.json を作成し、
`bun install`が通る状態にする。

## What Was Done

- `config.json`: interest_profile・trend_dir・embedding_model等の設定を定義
- `package.json`: astro + @astrojs/node依存、`bun test`スクリプト追加
- `astro.config.mjs`: output='hybrid'、node adapterで設定
- `tsconfig.json`: `astro/tsconfigs/strict`を継承
- `data/ratings.json`: 空のratings配列で初期化
- `src/pages/index.astro`: 最小限のplaceholderページ
- `bun install`で`bun.lockb`生成（npm→bunに移行）

## How It Was Done

当初npmでインストールしていたが、ユーザー指示によりbunに変更。
`bun install`がpackage-lock.jsonからlockfileをマイグレートし、`bun.lockb`を生成。

## Gotchas & Lessons Learned

- bunはpackage-lock.jsonから自動マイグレートできる（`migrated lockfile from package-lock.json`）
- node_modulesはnpmとbunで共有できる（再インストール不要だった）
- package.jsonの`"test": "bun test"`でbunのテストランナーを使用

## Reusable Patterns

```json
// package.json - bunプロジェクトの基本構成
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "test": "bun test"
  }
}
```

```js
// astro.config.mjs - hybrid SSRの設定
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
export default defineConfig({
  output: 'hybrid',
  adapter: node({ mode: 'standalone' }),
});
```
-->

## Summary

## Implemented Features

## Key Specification

## Key Learnings

## Reusable Patterns

## Gotchas

## Source Walkthroughs

- .logosyncx/tasks/20260311-arxiv-phase-1/006-api/WALKTHROUGH.md
- .logosyncx/tasks/20260311-arxiv-phase-1/005-/WALKTHROUGH.md
- .logosyncx/tasks/20260311-arxiv-phase-1/004-papercard/WALKTHROUGH.md
- .logosyncx/tasks/20260311-arxiv-phase-1/003-astro/WALKTHROUGH.md
- .logosyncx/tasks/20260311-arxiv-phase-1/002-parsepy-tdd/WALKTHROUGH.md
- .logosyncx/tasks/20260311-arxiv-phase-1/001-/WALKTHROUGH.md
