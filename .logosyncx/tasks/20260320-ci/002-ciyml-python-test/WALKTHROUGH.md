## Key Specification

ci.yml に `python-test` ジョブを追加。`pytest scripts/tests/` を実行し `test_parse.py` は `--ignore` で除外。

## What Was Done

`python-test` ジョブを ci.yml に実装（タスク1と同時に実装済み）。

## How It Was Done

- `actions/setup-python@v5` + `cache: pip`
- `pip install -r requirements.txt`（pytest を requirements.txt に追加）
- `pytest scripts/tests/ --ignore=scripts/tests/test_parse.py`

## Gotchas & Lessons Learned

`--ignore` のパスは実行ディレクトリからの相対パスで指定。

## Reusable Patterns

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: pip
```
