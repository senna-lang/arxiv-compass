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
