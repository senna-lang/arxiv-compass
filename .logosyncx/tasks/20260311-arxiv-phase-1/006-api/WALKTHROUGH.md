## Key Specification

POST /api/rate でratings.jsonに星評価を保存し、git add/commit/pushする。

## What Was Done

- `src/pages/api/rate.ts`: 評価保存 + git push（best effort）

## How It Was Done

- readFileSync/writeFileSyncで同期的にratings.jsonを読み書き
- execSyncでgit操作（失敗してもAPIは200を返す）

## Gotchas & Lessons Learned

- execSyncはstdio: "pipe"を指定しないとgitの出力がサーバーのstdoutに出てしまう
- git pushはネットワーク状況で失敗するのでtry/catchでbest effort処理

## Reusable Patterns

```ts
// best effort git push
try {
  execSync(`git add data/ratings.json && git commit -m "rate: ${dateStr}" && git push`, {
    cwd: process.cwd(),
    stdio: "pipe",
  });
} catch {
  // 失敗してもAPIは成功を返す
}
```
