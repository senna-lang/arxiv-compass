---
id: t-3dd7d7
date: 2026-03-11T23:35:49.702456+09:00
title: プロジェクト基盤セットアップ
seq: 1
status: done
priority: medium
plan: 20260311-arxiv-phase-1
tags: []
assignee: ""
completed_at: 2026-03-11T23:42:08.920762+09:00
---

## What

Astro + Pythonプロジェクトの骨格となる設定ファイル群を作成する。
`config.json`・`package.json`・`astro.config.mjs`・`data/ratings.json`を用意し、
`npm install`と`npm run dev`が通る状態にする。

## Why

後続タスク（parse.py・Astroページ）の前提となる環境。依存関係を先に確定させることで並列作業が可能になる。

## Scope

- `config.json`
- `package.json`
- `astro.config.mjs`
- `tsconfig.json`
- `data/ratings.json`（空ファイル）
- `data/.gitkeep`

OUT: src/ 以下のAstroコード、scripts/以下のPythonコード

## Acceptance Criteria

- [ ] `npm install` が成功する
- [ ] `npm run dev` でAstroが起動する（404ページでもOK）
- [ ] `config.json`にinterest_profile・trend_dir・embedding_model等が定義されている
- [ ] `data/ratings.json`が`{ "ratings": [] }`の状態で存在する

## Checklist

- [ ] `config.json`を作成（SPEC.md記載の内容）
- [ ] `package.json`を作成（astro, @astrojs/node依存）
- [ ] `astro.config.mjs`を作成（output: 'hybrid', node adapter）
- [ ] `tsconfig.json`を作成（Astroのデフォルト設定）
- [ ] `data/ratings.json`を作成（空ratings配列）
- [ ] `npm install`を実行して確認

## Notes

- embedding_modelはPhase 1では`all-MiniLM-L6-v2`（Phase 2でspecter2に変更）
- trend_dirは`/Users/senna/Documents/Repos/life/ideas/daily`
