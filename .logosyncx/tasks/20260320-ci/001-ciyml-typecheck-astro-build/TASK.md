---
id: t-e29048
date: 2026-03-20T12:49:18.581009+09:00
title: 'ci.yml 作成: typecheck + astro-build ジョブ'
seq: 1
status: done
priority: high
plan: 20260320-ci
tags: []
assignee: ""
completed_at: 2026-03-20T12:56:23.54468+09:00
---

## What

`.github/workflows/ci.yml` を新規作成し、フロントエンド系の2ジョブ（typecheck, astro-build）を定義する。ワークフロー全体のトリガー・concurrency 設定もこのタスクで行う。

## Why

PR・push 時に型エラーやビルド失敗を自動検出し、main ブランチの品質を保つため。

## Scope

- `.github/workflows/ci.yml`（新規作成）

OUT of scope: Python 系ジョブ（別タスク）

## Acceptance Criteria

- [ ] `push` to `main` と PR targeting `main` でトリガーされる
- [ ] `concurrency` で同一 ref の連続 push が cancel される
- [ ] `typecheck` ジョブ: checkout → setup-bun (cache:true) → bun install --frozen-lockfile → npx tsc --noEmit
- [ ] `astro-build` ジョブ: checkout → setup-bun (cache:true) → bun install --frozen-lockfile → bun run build

## Checklist

- [ ] ci.yml 作成（トリガー・concurrency・typecheck・astro-build）
- [ ] ローカルで YAML lint 確認

## Notes

- `oven-sh/setup-bun@v2` の `cache: true` で bun.lockb ベースのキャッシュが有効になる
