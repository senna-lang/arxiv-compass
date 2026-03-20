---
id: t-603077
date: 2026-03-20T12:49:51.383507+09:00
title: 'ci.yml: python-lint ジョブ追加'
seq: 3
status: done
priority: medium
plan: 20260320-ci
tags: []
assignee: ""
completed_at: 2026-03-20T12:57:08.021089+09:00
---

## What

ci.yml に `python-lint` ジョブを追加する。`ruff check scripts/` と `py_compile` による構文チェックを実行する。

## Why

Python コードのスタイル違反や構文エラーを CI で自動検出するため。ML 依存を入れず高速に回す。

## Scope

- `.github/workflows/ci.yml`（python-lint ジョブ追加）

OUT of scope: ruff.toml の作成（初回は既定ルールで実行）

## Acceptance Criteria

- [ ] `python-lint` ジョブ: checkout → setup-python 3.11 → pip install ruff → ruff check scripts/ → python -m py_compile で全 .py をチェック
- [ ] ML 依存なしで ~20秒で完了する

## Checklist

- [ ] ci.yml に python-lint ジョブ追加
- [ ] ruff check と py_compile の両ステップを含む

## Notes

- ruff のみインストールすれば良い（requirements.txt の ML 依存は不要）
- py_compile は標準ライブラリなので追加インストール不要
