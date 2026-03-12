## Key Specification

src/lib/types.ts（型定義）+ src/lib/data.ts（データ読み込み関数）を実装。

## What Was Done

- `src/lib/types.ts`: Paper / Rating / DailyData / RatingsData 型を定義
- `src/lib/data.ts`: getAvailableDates / getPapersForDate / getRatings / getRatingMap を実装
- `tsconfig.json` に `"types": ["node"]` を追加
- `@types/node` を devDependencies に追加

## How It Was Done

node:fs / node:path をimportしてファイル読み込み。エラーは全て catch して空配列/Mapを返す。
bun run build で型チェックとビルドを確認。

## Gotchas & Lessons Learned

- AstroのデフォルトtsonfigではNode.jsの型が含まれない → `@types/node` + `"types": ["node"]`が必要

## Reusable Patterns

```ts
// 全エラーをcatchして安全なデフォルト値を返すパターン
export function getAvailableDates(): string[] {
  try {
    return readdirSync(DATA_DIR)
      .filter((f) => /^\d{8}\.json$/.test(f))
      .map((f) => f.replace(".json", ""))
      .sort();
  } catch {
    return [];
  }
}
```
