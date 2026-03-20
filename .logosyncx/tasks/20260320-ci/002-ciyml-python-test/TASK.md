---
id: t-b5c025
date: 2026-03-20T12:49:37.779048+09:00
title: 'ci.yml: python-test ジョブ追加'
seq: 2
status: done
priority: high
plan: 20260320-ci
tags: []
assignee: ""
completed_at: 2026-03-20T12:57:08.000098+09:00
---

## What

ci.yml に `python-test` ジョブを追加する。`pytest scripts/tests/` を実行し、`test_parse.py` は `--ignore` で除外する。

## Why

Python パイプラインのロジック（スコアリング、レコメンド等）の回帰を CI で検出するため。

## Scope

- `.github/workflows/ci.yml`（python-test ジョブ追加）
- `requirements.txt`（pytest 追加）

OUT of scope: test_parse.py の修正（別 issue）

## Acceptance Criteria

- [ ] `python-test` ジョブ: checkout → setup-python 3.11 (cache:pip) → pip install -r requirements.txt pytest → pytest scripts/tests/ --ignore=scripts/tests/test_parse.py
- [ ] `requirements.txt` に `pytest` が追加されている
- [ ] `test_parse.py` が除外されてテストが pass する

## Checklist

- [ ] requirements.txt に pytest 追加
- [ ] ci.yml に python-test ジョブ追加

## Notes

- `test_parse.py` は存在しない `parse.py` を import するため除外が必要
- `pytest` は requirements.txt に含まれていなかったので明示的に追加
