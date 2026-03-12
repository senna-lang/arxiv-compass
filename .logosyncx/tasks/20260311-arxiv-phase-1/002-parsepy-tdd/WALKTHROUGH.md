## Key Specification

trend.mdのMarkdownテーブルからarXiv IDを抽出し、arXiv APIでabstractを取得、
sentence-transformersでスコアリングしてdata/YYYYMMDD.jsonを生成する。

## What Was Done

- `scripts/tests/test_parse.py`: 13テスト（TDD Red→Green）
- `scripts/parse.py`: parse_trend_section / compute_score / build_paper_dict / main を実装

## How It Was Done

1. テストを先に書いてModuleNotFoundError確認（Red）
2. parse.py実装後にarxivライブラリ未インストールで再度失敗
3. `pip install arxiv sentence-transformers numpy`でインストール
4. `MagicMock(name=...)` がMockの識別名であり属性ではないことを発見 → テスト修正

## Gotchas & Lessons Learned

- `MagicMock(name="Alice")` はデバッグ名。`.name = "Alice"` で明示的に設定する必要がある
- `model.encode()` はndarrayを返すがPyrightは`list[ndarray]`と認識しないため`list()`でラップ
- arXiv IDの正規表現: `^\d{4}\.\d{4,5}$`（4桁.4〜5桁）
- entry_id末尾の`v1`除去: `re.sub(r"v\d+$", "", raw_id)`

## Reusable Patterns

```python
# MagicMockの属性設定
author = MagicMock()
author.name = "Alice Smith"  # MagicMock(name=...) ではなくこちら

# arXiv IDの抽出（テーブル2列目）
cols = [c.strip() for c in line.split("|")]
if re.match(r"^\d{4}\.\d{4,5}$", cols[2]):
    ...

# cos類似度スコアリング
def compute_score(abstract_vec, profile_vecs):
    sims = [cosine_similarity(abstract_vec, pv) for pv in profile_vecs]
    return float(np.mean(sims))
```
