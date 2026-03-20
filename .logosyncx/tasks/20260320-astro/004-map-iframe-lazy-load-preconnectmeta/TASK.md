---
id: t-b64060
date: 2026-03-20T12:18:52.512914+09:00
title: map iframe lazy load + preconnect/meta
seq: 4
status: open
priority: low
plan: 20260320-astro
tags: []
assignee: ""
---

## What

map.astro の iframe に `loading="lazy"` を追加。MainLayout.astro に preconnect ヒントと meta description を追加。

## Why

map.html は 375KB あり、iframe の遅延読み込みでメインドキュメントのパース優先度を上げる。preconnect で arxiv.org へのリンクナビゲーションを高速化。meta description で SEO 改善。

## Scope

- `src/pages/map.astro` — iframe に `loading="lazy"` 追加
- `src/layouts/MainLayout.astro` — `<link rel="preconnect">`, `<link rel="dns-prefetch">`, `<meta name="description">` 追加

## Acceptance Criteria

- [ ] map.astro の iframe に `loading="lazy"` が設定されている
- [ ] MainLayout.astro に preconnect と dns-prefetch が設定されている
- [ ] MainLayout.astro に meta description が設定されている
- [ ] `npm run build` 成功

## Checklist

- [ ] map.astro: iframe に `loading="lazy"` 追加
- [ ] MainLayout.astro: `<link rel="preconnect" href="https://arxiv.org" />` 追加
- [ ] MainLayout.astro: `<link rel="dns-prefetch" href="https://arxiv.org" />` 追加
- [ ] MainLayout.astro: `<meta name="description" content="arXiv論文の日次トレンドニュースペーパー" />` 追加

## Notes

- iframe は 80vh で画面の大部分を占めるため、`loading="lazy"` の効果は限定的だが害もない
