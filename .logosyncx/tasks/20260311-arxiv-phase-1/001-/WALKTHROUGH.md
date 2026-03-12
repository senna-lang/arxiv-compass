## Key Specification

TASK.md: config.json・package.json・astro.config.mjs・tsconfig.json・data/ratings.json を作成し、
`bun install`が通る状態にする。

## What Was Done

- `config.json`: interest_profile・trend_dir・embedding_model等の設定を定義
- `package.json`: astro + @astrojs/node依存、`bun test`スクリプト追加
- `astro.config.mjs`: output='hybrid'、node adapterで設定
- `tsconfig.json`: `astro/tsconfigs/strict`を継承
- `data/ratings.json`: 空のratings配列で初期化
- `src/pages/index.astro`: 最小限のplaceholderページ
- `bun install`で`bun.lockb`生成（npm→bunに移行）

## How It Was Done

当初npmでインストールしていたが、ユーザー指示によりbunに変更。
`bun install`がpackage-lock.jsonからlockfileをマイグレートし、`bun.lockb`を生成。

## Gotchas & Lessons Learned

- bunはpackage-lock.jsonから自動マイグレートできる（`migrated lockfile from package-lock.json`）
- node_modulesはnpmとbunで共有できる（再インストール不要だった）
- package.jsonの`"test": "bun test"`でbunのテストランナーを使用

## Reusable Patterns

```json
// package.json - bunプロジェクトの基本構成
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "test": "bun test"
  }
}
```

```js
// astro.config.mjs - hybrid SSRの設定
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
export default defineConfig({
  output: 'hybrid',
  adapter: node({ mode: 'standalone' }),
});
```
