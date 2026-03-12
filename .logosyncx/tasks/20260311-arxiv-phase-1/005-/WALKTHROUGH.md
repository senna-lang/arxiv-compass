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
