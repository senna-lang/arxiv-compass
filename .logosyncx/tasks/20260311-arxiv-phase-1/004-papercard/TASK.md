---
id: t-b7c0ad
date: 2026-03-11T23:35:49.732844+09:00
title: PaperCardコンポーネント実装
seq: 4
status: done
priority: medium
plan: 20260311-arxiv-phase-1
tags: []
assignee: ""
completed_at: 2026-03-12T09:50:46.333692+09:00
---

## What

論文カードコンポーネント`PaperCard.astro`を実装する。
タイトル・著者・スコア・星UI・abstractアコーディオンを含む。
クライアントサイドの星クリックイベントも実装する。

## Why

ユーザーが論文を評価するメインのUIパーツ。

## Scope

- `src/components/PaperCard.astro`
- `src/components/RecommendSection.astro`（空stubのみ）
- `public/rate.js`（星クリック→API呼び出し）

OUT: API route、ページ

## Acceptance Criteria

- [ ] タイトル（arXivリンク付き）・著者・カテゴリ・スコアが表示される
- [ ] 星1〜3をクリックすると視覚的にフィードバックがある
- [ ] abstractが`<details>`で展開/折りたたみできる
- [ ] github_urlがある場合のみ[GitHub]ボタンが表示される
- [ ] 星クリックで`POST /api/rate`にfetchが飛ぶ

## Checklist

- [ ] `src/components/PaperCard.astro`を作成
  - [ ] Props: `paper: Paper`, `initialRating: number`
  - [ ] タイトル（`<a href={paper.url}`）
  - [ ] 著者・カテゴリ・スコア表示
  - [ ] 星UI（`★★☆`スタイル、クリック可能）
  - [ ] `<details><summary>abstract を読む ▼</summary>` でabstract
  - [ ] github_urlがあれば`<a href={github_url}>[GitHub]</a>`
- [ ] `public/rate.js`を作成
  - [ ] 星クリックで`fetch('/api/rate', { method: 'POST', body: JSON.stringify({...}) })`
  - [ ] レスポンス成功でUIを更新
- [ ] `src/components/RecommendSection.astro`を空stubで作成（Phase 2用）

## Notes

- スタイルはAstroのscoped CSSで記述（外部CSSフレームワーク不使用）
- 星UIはJavaScript不使用でも基本表示できるよう初期値をHTMLに埋め込む
