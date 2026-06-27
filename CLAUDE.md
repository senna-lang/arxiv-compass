# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# フロントエンド
npm run dev          # 開発サーバー起動
npm run build        # 本番ビルド
npm run preview      # ビルド結果をプレビュー

# Pythonパイプライン
npm run parse        # 今日の trend.md をパースして YYYYMMDD.json を生成
npm run parse:all    # data/ にない日付の trend.md を一括処理
npm run map          # 論文地図を生成（max 1000件）
npm run map:full     # 論文地図を生成（max 10000件）
npm run recommend    # おすすめ論文を生成

# KVへのデータ移行
npx wrangler kv key put "ratings" --namespace-id=797a1d2d28ef40cd86bb25c2bce60fe9 --path=data/ratings.json --remote

# 型チェック
npx tsc --noEmit
```

## アーキテクチャ

### データフロー

```
daily-news skill → YYYYMMDD-trend.md（config.trend_dir に保存）
    ↓
parse.py → data/YYYYMMDD.json（arXiv論文 + スコア）
    ↓
Astro static build → Cloudflare Pages にデプロイ

ユーザーが星をつける
    ↓
POST /api/rate → Cloudflare KV（RATINGS_KV）
GET /api/ratings → recommend.py が ratings_url 経由で取得
    ↓
recommend.py → data/recommendations.json
```

### フロントエンド（Astro + Cloudflare）

- `output: 'static'` で静的ビルド。`/api/*` エンドポイントだけ `prerender = false` でWorkerとして動作
- ページは `import.meta.glob("/data/????????.json", { eager: true })` でビルド時にJSONを読み込む（`node:fs` は使わない）
- KVバインディングは `import { env } from "cloudflare:workers"` でアクセス。型は `src/env.d.ts` の `Cloudflare.Env` で定義
- 共通レイアウトは `src/layouts/MainLayout.astro`。ページ固有のスタイルは `<style slot="head">` で注入

### Pythonパイプライン

- `config.json` が全スクリプトの設定起点（`embedding_model`, `trend_dir`, `output_dir`, `ratings_url` など）
- 全スクリプトが同じモデル `allenai/specter2_base` を使用
- `recommend.py` は `config.ratings_url`（本番: `GET /api/ratings`）から評価データを取得。未設定時は `data/ratings.json` にフォールバック

### スコアリングロジック

- 日次: `abstract` vs `interest_profile`（7項目）の cosine similarity 平均 = score
- 週次レコメンド: `α = min(1.0, ratings件数/50)` で profile ベースから実績ベースへ段階的移行

## 重要な制約

- `import.meta.glob()` は Vite の制約でユーティリティ関数内に書けない。各ページファイルで直接呼ぶ必要がある。日付リストへの変換は `extractDates()` (`src/lib/data.ts`) で共通化
- 評価データの本番ソースは Cloudflare KV（`/api/ratings`）。`data/ratings.json` はビルド時のフォールバックとして残しており、`src/pages/map.astro` と `[date].astro` が読み込む。バッチスクリプトも `ratings_url` 未設定時はこのファイルにフォールバックする

## Code Intelligence

Prefer LSP over Grep/Read for code navigation — it's faster, precise, and avoids reading entire files:
- `workspaceSymbol` to find where something is defined
- `findReferences` to see all usages across the codebase
- `goToDefinition` / `goToImplementation` to jump to source
- `hover` for type info without reading the file

Use Grep only when LSP isn't available or for text/pattern searches (comments, strings, config).

After writing or editing code, check LSP diagnostics and fix errors before proceeding.

---

<!-- BEGIN CODEATRIUM -->
## Past Memory Search (codeatrium)

IMPORTANT: Command usage is injected automatically at session start via `loci prime` (SessionStart hook).
If not in context, run `loci prime`.

### Rules

1. **Search before implementing** — always check if something was discussed or built before starting work.
2. **Check symbols when you lack context** — run `loci context --symbol` before changing a function you don't have enough background on.
3. **Use technical terms** — queries with exact symbol names, error messages, or parameter names yield better results.
4. **Follow up with `loci show`** — when `exchange_core` is ambiguous, fetch the full verbatim conversation.
<!-- END CODEATRIUM -->

---
