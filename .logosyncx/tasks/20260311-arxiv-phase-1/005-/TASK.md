---
id: t-43d8ef
date: 2026-03-11T23:35:49.758616+09:00
title: 日付別ページ実装
seq: 5
status: done
priority: medium
plan: 20260311-arxiv-phase-1
tags: []
assignee: ""
completed_at: 2026-03-12T09:55:15.174035+09:00
---

## What

`src/pages/[date].astro`と`src/pages/index.astro`を実装する。
日付パラメータでデータを読み込み、PaperCardを並べて表示する。
前日/翌日ナビゲーションとヘッダーを含む。

## Why

ユーザーが毎日論文を閲覧する主画面。

## Scope

- `src/pages/index.astro`
- `src/pages/[date].astro`

OUT: コンポーネント（タスク4）、データ層（タスク3）

## Acceptance Criteria

- [ ] `http://localhost:4321/`にアクセスすると最新日付のページにリダイレクトされる
- [ ] `http://localhost:4321/20260311`で論文一覧が表示される
- [ ] ヘッダーに日付が表示される（`📰 arXiv新聞 2026-03-11`）
- [ ] 前日/翌日ナビゲーションリンクが機能する（存在しない日付はdisabled）
- [ ] 論文がscoreの降順で表示される（parse.py側でソート済みのため確認のみ）
- [ ] 各論文に現在のrating（ratings.jsonから）が反映された星UIが表示される

## Checklist

- [ ] `src/pages/index.astro`
  - [ ] `getAvailableDates()`で最新日付を取得
  - [ ] `Astro.redirect(`/${latestDate}`)`でリダイレクト
- [ ] `src/pages/[date].astro`
  - [ ] `export const prerender = false`（SSRモード）
  - [ ] `Astro.params.date`でデータ読み込み
  - [ ] `getPapersForDate(date)` + `getRatingMap()`
  - [ ] ヘッダー（日付表示）
  - [ ] 前日/翌日リンク（`getAvailableDates()`で前後を判定）
  - [ ] `<PaperCard>`を論文数分レンダリング
  - [ ] `<RecommendSection />`（Phase 1: 空）

## Notes

- 日付フォーマット: URLパラメータは`YYYYMMDD`、表示は`YYYY-MM-DD`
- data/がない場合（初回）は404ページを表示
