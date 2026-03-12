---
id: t-4b9b9e
date: 2026-03-11T23:35:49.711962+09:00
title: parse.py TDD実装
seq: 2
status: done
priority: medium
plan: 20260311-arxiv-phase-1
tags: []
assignee: ""
completed_at: 2026-03-11T23:47:23.666668+09:00
---

## What

`scripts/parse.py`をTDDで実装する。trend.mdのarXivテーブルをパースし、
arXiv APIでabstractを取得、sentence-transformersでスコアリングして
`data/YYYYMMDD.json`を生成する。

## Why

毎朝のデータパイプラインの起点。これがないとAstroアプリに表示するデータがない。

## Scope

- `scripts/parse.py`
- `scripts/tests/__init__.py`
- `scripts/tests/test_parse.py`

OUT: Astroアプリ、config.json（タスク1で作成済み）

## Acceptance Criteria

- [ ] `python -m pytest scripts/tests/ -v` が全テストPASS
- [ ] `python scripts/parse.py --date 2026-03-11` を実行すると`data/20260311.json`が生成される
- [ ] 生成されたJSONがSPEC.mdのスキーマ（id/title/authors/abstract/url/categories/submitted/score）に準拠
- [ ] scoreが0〜1の範囲のfloat
- [ ] 論文がscoreの降順にソートされている

## Checklist

- [ ] `scripts/tests/test_parse.py`を先に書く（Red）
  - [ ] `test_parse_trend_section`: Markdownテーブル文字列からarXiv IDリスト抽出
  - [ ] `test_compute_score`: embedding vectorとprofile vectorのcos類似度計算
  - [ ] `test_build_paper_dict`: JSONスキーマ整合性（必須キーが揃っているか）
  - [ ] arXiv API呼び出しはMockで差し替え
  - [ ] sentence-transformersはMockで差し替え
- [ ] `scripts/parse.py`を実装してテストをGreen
  - [ ] `parse_trend_section(text: str) -> list[str]`: arXiv IDを抽出
  - [ ] `fetch_arxiv_papers(ids: list[str]) -> list[dict]`: arXiv APIで論文情報取得
  - [ ] `compute_score(abstract_vec, profile_vecs) -> float`: cos類似度平均
  - [ ] `build_paper_dict(paper, score) -> dict`: JSONスキーマ準拠のdict生成
  - [ ] `main(date: str)`: フロー全体を統合
  - [ ] `--date`オプション（デフォルト: 今日）
- [ ] `python -m pytest scripts/tests/ -v`でPASS確認
- [ ] 実際のtrend.mdで動作確認

## Notes

- trend.mdのarXivセクション先頭行: `## 📄 arXiv 注目論文`
- テーブルの各行: `| [日本語タイトル](URL) | arXiv_ID | 日付 | 著者 | ★★★ | タグ | メモ |`
- arXiv IDは2列目から抽出（URLからも抽出可能）
- arXiv APIライブラリ: `arxiv>=2.1.0`
- ファイル冒頭にdocstringで仕様を記述すること（CLAUDE.mdルール）
- Result型でエラーハンドリング、throwは使わない
