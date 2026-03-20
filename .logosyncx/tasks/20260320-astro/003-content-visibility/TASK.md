---
id: t-6257fa
date: 2026-03-20T12:18:29.518781+09:00
title: content-visibility レンダリング最適化
seq: 3
status: open
priority: medium
plan: 20260320-astro
tags: []
assignee: ""
---

## What

`.paper-card`, `.recommend-card`, `.serendipity-card` に `content-visibility: auto` と `contain-intrinsic-size` を追加し、ファーストビュー外のカードのレンダリングを遅延させる。

## Why

20枚のカードが全てレイアウト計算されるが、ファーストビューには3-4枚しか見えない。`content-visibility: auto` でブラウザが画面外のカードのレンダリングをスキップできる。

## Scope

- `src/components/PaperCard.astro` — CSS追加
- `src/components/RecommendSection.astro` — CSS追加
- `src/components/SerendipitySection.astro` — CSS追加

## Acceptance Criteria

- [ ] 各カードクラスに `content-visibility: auto` と `contain-intrinsic-size` が設定されている
- [ ] スクロールでカードが正しく表示される（レイアウトジャンプなし）
- [ ] `npm run build` 成功

## Checklist

- [ ] PaperCard.astro: `.paper-card` に `content-visibility: auto; contain-intrinsic-size: auto 200px;` 追加
- [ ] RecommendSection.astro: `.recommend-card` に同様のCSS追加
- [ ] SerendipitySection.astro: `.serendipity-card` に同様のCSS追加

## Notes

- Chrome 85+, Firefox 125+, Safari 18+ 対応。非対応ブラウザでは無視されるだけなのでリスクなし。
