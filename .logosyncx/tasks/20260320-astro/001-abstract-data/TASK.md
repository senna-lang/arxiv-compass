---
id: t-2de785
date: 2026-03-20T12:17:44.342675+09:00
title: abstract data属性の重複除去
seq: 1
status: open
priority: high
plan: 20260320-astro
tags: []
assignee: ""
---

## What

3コンポーネント（PaperCard, RecommendSection, SerendipitySection）の `.star-rating` div から `data-abstract` 属性を削除し、クリックハンドラでDOM走査に変更する。約26KB/ページの削減。

## Why

各論文の abstract が HTML 内に2回出現（`<details>` 内 + `data-abstract` 属性）しており、ページサイズの約15%が無駄な重複。

## Scope

- `src/components/PaperCard.astro` — `data-abstract` 削除 + script のクリックハンドラ修正
- `src/components/RecommendSection.astro` — `data-abstract` 削除
- `src/components/SerendipitySection.astro` — `data-abstract` 削除

## Acceptance Criteria

- [ ] ビルド出力HTMLに `data-abstract` が存在しない
- [ ] 星クリック時のPOSTボディに正しい abstract が含まれる
- [ ] `npx tsc --noEmit` パス
- [ ] `npm run build` 成功

## Checklist

- [ ] PaperCard.astro: `data-abstract={paper.abstract}` 削除
- [ ] PaperCard.astro: クリックハンドラで `container.dataset.abstract` → `card.querySelector("details p")?.textContent` に変更
- [ ] RecommendSection.astro: `data-abstract={rec.abstract}` 削除
- [ ] SerendipitySection.astro: `data-abstract={rec.abstract}` 削除
- [ ] ビルド出力で `data-abstract` が消えていることを確認

## Notes

- DOM走査のセレクタ: `container.closest("article")?.querySelector("details p")?.textContent ?? ""`
- 3コンポーネント全てで `article > details > p` 構造が統一されているため動作する
