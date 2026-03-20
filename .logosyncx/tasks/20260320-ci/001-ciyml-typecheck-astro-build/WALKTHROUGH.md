## Key Specification

- `.github/workflows/ci.yml` 新規作成
- push to main / PR targeting main でトリガー
- concurrency: `ci-${{ github.ref }}` + cancel-in-progress
- typecheck・astro-build の2ジョブ（フロントエンド系）

## What Was Done

- `.github/workflows/ci.yml` を作成し、4ジョブ全て定義（python系もまとめて実装）
- `requirements.txt` に `pytest` を追加

## How It Was Done

- `oven-sh/setup-bun@v2` の `cache: true` で bun.lockb ベースのキャッシュを有効化
- `actions/setup-python@v5` の `cache: pip` で pip キャッシュを有効化
- python-lint は `pip install ruff` のみ（requirements.txt 不要）

## Gotchas & Lessons Learned

- `python -m py_compile scripts/*.py` はシェルグロブなのでそのまま使える
- `pytest --ignore=` のパスは `scripts/tests/test_parse.py` とフルパスで指定が必要

## Reusable Patterns

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```
