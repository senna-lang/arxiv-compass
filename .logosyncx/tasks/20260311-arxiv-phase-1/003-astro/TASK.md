---
id: t-0bcf6a
date: 2026-03-11T23:35:49.723292+09:00
title: Astroデータアクセス層実装
seq: 3
status: done
priority: medium
plan: 20260311-arxiv-phase-1
tags: []
assignee: ""
completed_at: 2026-03-11T23:49:03.216761+09:00
---

## What

`src/lib/data.ts`にデータ読み込みユーティリティを実装する。
`data/*.json`ファイルを読み込む関数群をエクスポートし、
Astroページから型安全に利用できるようにする。

## Why

AstroページとJSONデータの橋渡し。型定義を集約することでページ実装が楽になる。

## Scope

- `src/lib/data.ts`（型定義 + データ読み込み関数）
- `src/lib/types.ts`（共通型定義）

OUT: Astroページ、コンポーネント

## Acceptance Criteria

- [ ] `getAvailableDates()`が`data/`以下のJSONファイルから日付リストを返す
- [ ] `getPapersForDate(date)`が指定日付の論文配列を返す
- [ ] `getRatings()`がratings配列を返す
- [ ] 型定義が`Paper`・`Rating`・`DailyData`として定義されている
- [ ] LSP診断エラーがない

## Checklist

- [ ] `src/lib/types.ts`を作成
  - [ ] `Paper`型（id/title/authors/abstract/url/categories/submitted/score/github_url?）
  - [ ] `Rating`型（paper_id/title/abstract/rating/rated_at）
  - [ ] `DailyData`型（date/collected_at/papers/meta）
- [ ] `src/lib/data.ts`を作成
  - [ ] `getAvailableDates(): string[]`
  - [ ] `getPapersForDate(date: string): Paper[]`
  - [ ] `getRatings(): Rating[]`
  - [ ] `getRatingMap(): Map<string, number>`（paper_id → rating）

## Notes

- `import.meta.env.ROOT`または`process.cwd()`でルートパスを解決
- Node.js fsでファイル読み込み（Astroのサーバーサイド）
- ブランデッド型は今回は不要（シンプルさ優先）
