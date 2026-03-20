---
id: t-a03272
date: 2026-03-20T12:18:08.059862+09:00
title: ratings APIページ単位フィルタ
seq: 2
status: open
priority: high
plan: 20260320-astro
tags: []
assignee: ""
---

## What

`GET /api/ratings` に `ids` クエリパラメータを追加し、ページ内の paper_id のみ返すようにする。クライアントJSもページ内の paper_id を収集して渡すように変更 + `requestIdleCallback` で遅延実行。

## Why

現状は全 ratings を毎回取得しており、レスポンスサイズとパース時間が無駄。ページ単位でフィルタすれば必要な分だけ返せる。

## Scope

- `src/pages/api/ratings.ts` — `ids` パラメータによるフィルタリング追加
- `src/components/PaperCard.astro` — script 内の fetch ロジック変更

OUT of scope: `POST /api/rate` の変更、localStorage キャッシュ

## Acceptance Criteria

- [ ] `GET /api/ratings?ids=id1,id2` がフィルタされた結果を返す
- [ ] `GET /api/ratings`（パラメータなし）が全件返す（後方互換）
- [ ] クライアントJSがページ内のpaper_idのみをクエリに渡す
- [ ] fetch が `requestIdleCallback` で遅延実行される
- [ ] `npx tsc --noEmit` パス

## Checklist

- [ ] `ratings.ts`: `url.searchParams.get("ids")` でフィルタロジック追加
- [ ] `PaperCard.astro` script: ページ内 `.star-rating[data-paper-id]` を収集
- [ ] `PaperCard.astro` script: fetch URL に `?ids=` パラメータ付与
- [ ] `PaperCard.astro` script: `DOMContentLoaded` → `requestIdleCallback` / `setTimeout` フォールバック
- [ ] ratings フィルタリングのユニットテスト作成

## Notes

- `ids` パラメータなしは recommend.py のバッチ取得で使用されるため、後方互換必須
