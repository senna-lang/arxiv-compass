---
id: t-045701
date: 2026-03-11T23:35:49.777604+09:00
title: 星評価APIと動作確認
seq: 6
status: done
priority: medium
plan: 20260311-arxiv-phase-1
tags: []
assignee: ""
completed_at: 2026-03-12T09:58:08.78599+09:00
---

## What

`src/pages/api/rate.ts`を実装し、星クリック → ratings.json保存 → git push の
一連のフローを動作確認する。全体統合テストも含む。

## Why

レーティングデータが蓄積されることがPhase 2（map/recommend）の前提条件。

## Scope

- `src/pages/api/rate.ts`
- E2E動作確認（npm run dev + ブラウザ）

OUT: コンポーネント、ページ（タスク4/5で実装済み）

## Acceptance Criteria

- [ ] `POST /api/rate`でratings.jsonが更新される
- [ ] 同一paper_idに再評価した場合は上書き（重複なし）
- [ ] git commit + pushが実行される（またはエラーが適切にハンドリングされる）
- [ ] ブラウザで星をクリックするとratings.jsonに記録される

## Checklist

- [ ] `src/pages/api/rate.ts`を作成
  - [ ] `export const prerender = false`
  - [ ] `POST`ハンドラ
  - [ ] リクエストボディ: `{ paper_id, title, abstract, rating }`
  - [ ] `data/ratings.json`を読み込み
  - [ ] 既存レーティングを検索して上書き or 新規追加
  - [ ] `rated_at`をISO文字列で記録
  - [ ] ファイル書き込み
  - [ ] `execSync('git add data/ratings.json && git commit -m "rate: YYYYMMDD" && git push')`
  - [ ] 200 OK or エラーレスポンス
- [ ] `npm run dev`で起動して動作確認
  - [ ] `http://localhost:4321/20260311`（またはparse.pyで生成した実際の日付）
  - [ ] 論文カードの星クリック → ratings.jsonが更新されることを確認
  - [ ] git logで自動コミットが記録されることを確認

## Notes

- git pushはネットワークエラーの可能性があるため、失敗してもAPIは200を返す（best effort）
- git commit messageのフォーマット: `rate: YYYYMMDD`（当日日付）
- `execSync`はNode.jsの`child_process`モジュールから
