# arxiv-explorer

arXivの論文群をセマンティック地図化し、自分の興味に近い論文を発見するパーソナル新聞アプリ。

---

## システム概要

```
daily-news スキル
  └─ YYYYMMDD-trend.md を生成（別リポジトリ: life/）
          │
          ▼
    parse.py（毎朝）
      └─ trend.md の arXiv セクションをパース
      └─ arXiv API で abstract を取得
      └─ Embedding + interest_profile とのコサイン類似度でスコアリング
      └─ data/YYYYMMDD.json に保存
          │
          ▼
    Astro 新聞アプリ（ローカル dev）
      └─ 論文カード表示（score 降順）
      └─ 星をつける → data/ratings.json → git push
          │
          ▼ （Phase 2 以降）
    map.py（月次）
      └─ arXiv 論文 10,000 件を取得
      └─ BERTopic でクラスタリング → data/map.json（arXiv 地図）

    recommend.py（週次）
      └─ ratings.json × map.json → 近傍クラスタを特定
      └─ data/recommendations.json に保存
```

---

## Tech Stack

### Frontend
| | |
|---|---|
| **Astro** | SSR (hybrid mode) + 静的ページ生成 |
| **@astrojs/node** | ローカル dev サーバー用アダプター |
| **Vanilla JS** | 星 UI・API 呼び出し（rate.js） |

### Backend / Scripts
| | |
|---|---|
| **Python** | データパイプライン全般 |
| **sentence-transformers** | テキスト Embedding（all-MiniLM-L6-v2 → Phase2 で specter2） |
| **arxiv** | arXiv API クライアント |
| **BERTopic** *(Phase 2)* | UMAP + HDBSCAN + c-TF-IDF による論文クラスタリング |
| **numpy** | コサイン類似度計算 |

### Data
| ファイル | 内容 | 更新 |
|---|---|---|
| `data/YYYYMMDD.json` | 当日の論文 + スコア | 毎朝 |
| `data/ratings.json` | 星評価履歴（最重要資産） | 星クリック時 |
| `data/map.json` | arXiv 論文地図（クラスタ + UMAP 2D 座標） | 月次 |
| `data/recommendations.json` | 近傍クラスタからのおすすめ論文 | 週次 |

---

## Scoring

```
abstract → Embedding ──┐
                        ├─ cosine similarity × 7 → 平均 = score (0〜1)
interest_profile × 7 ──┘
```

`config.json` の `interest_profile` に興味領域を自然言語で記述するだけでスコアが自動計算される。

---

## Phase ロードマップ

```
Phase 1  ████████████████░░░░  毎日読んで星をつける習慣をつくる
Phase 2  ░░░░░░░░░░░░░░░░░░░░  ratings 20件〜  arXiv 地図生成 + おすすめ表示
Phase 3  ░░░░░░░░░░░░░░░░░░░░  ratings 50件〜  興味ペルソナの自動分離
```

### Phase 2 追加スコアリング

```
α = min(1.0, ratings件数 / 50)
final_score = α × instance_score + (1-α) × profile_score
```

ratings が少ない初期は `profile_score`（config.json ベース）が補完し、
蓄積されるにつれて `instance_score`（実際の評価データ）に移行する。
