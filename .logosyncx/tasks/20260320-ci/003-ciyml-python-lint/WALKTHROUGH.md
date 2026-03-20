## Key Specification

ci.yml に `python-lint` ジョブを追加。`ruff check scripts/` と `py_compile` による構文チェックを実行。

## What Was Done

`python-lint` ジョブを ci.yml に実装（タスク1と同時に実装済み）。

## How It Was Done

- `pip install ruff`（requirements.txt は不要）
- `ruff check scripts/`
- `python -m py_compile scripts/*.py`（シェルグロブで全 .py を検査）

## Gotchas & Lessons Learned

ruff のみインストールすれば良いので pip キャッシュ効率が良い。

## Reusable Patterns

```yaml
- run: pip install ruff
- run: ruff check scripts/
- run: python -m py_compile scripts/*.py
```
