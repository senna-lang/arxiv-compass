# arxiv-explorer

arXiv論文群をトピックモデリングで地図化し、自分の興味に近い論文を発見するパーソナル新聞アプリ。

---

## このシステムが解く問題

arXivには毎日数百件の論文が投稿される。全部読むのは不可能。
**「今日の投稿の中で、自分が興味を持ちそうな論文はどれか？」**
**「自分がまだ知らない、でも好きそうな研究領域はどこか？」**

この2つの問いに答えるために、**Embedding（意味的近さ）** と **トピックモデリング（論文地図）** を組み合わせている。

---

## 全体の流れ

```
[日次] 今日の論文をスコアリングして読む
                │
                ▼
        ┌───────────────────────────────────┐
        │  daily-news skill が               │
        │  YYYYMMDD-trend.md を生成         │
        │  （## 📄 arXiv 注目論文 セクション│
        │    に arXiv ID リストを含む）      │
        └───────────────────────────────────┘
                │
                ▼
        ┌───────────────────────────────────┐
        │  parse.py が trend.md をパース    │
        │  → arXiv API で abstract 取得     │
        │  → Embedding                      │
        │  → interest_profile との類似度    │
        │  → score 順に並べて表示           │
        └───────────────────────────────────┘
                │
                │  星をつけて評価を蓄積
                ▼
        Cloudflare KV（星評価ストア）
        ※ GET /api/ratings でバッチから参照
                │
                │
[月次]          ▼
        ┌───────────────────────────────────┐
        │  arXiv論文 10,000件を取得         │
        │  BERTopic でトピックモデリング    │
        │  → 論文地図（map.json）を生成     │
        └───────────────────────────────────┘
                │
                │
[週次]          ▼
        ┌───────────────────────────────────┐
        │  ratings.json × map.json          │
        │  → 自分の興味クラスタを特定       │
        │  → 近傍論文をおすすめ表示         │
        └───────────────────────────────────┘
```

---

## トピックモデリングの仕組み

このシステムの核心は **BERTopic** による論文地図の生成。

```
10,000件の論文 abstract
        │
        ▼
  Embedding（specter2）
  各 abstract を高次元ベクトルに変換
        │
        ▼
  UMAP で次元削減（高次元 → 2次元）
  意味的に近い論文が平面上でも近くなる
        │
        ▼
  HDBSCAN でクラスタリング
  自然に集まっているグループを検出
        │
        ▼
  c-TF-IDF でトピックラベル生成
  各クラスタを代表するキーワードを抽出
        │
        ▼
  map.json（arXiv論文地図）
  ┌─────────────────────────────────────┐
  │  cluster: "Diffusion Models"        │
  │  cluster: "Graph Neural Networks"   │
  │  cluster: "LLM Reasoning"           │
  │  cluster: "Protein Structure"       │
  │  ...（数十〜数百クラスタ）          │
  └─────────────────────────────────────┘
```

### 地図から「自分の興味領域」を発見する

```
Cloudflare KV
（星をつけた論文の abstract）
        │
        ▼
  評価済み論文が属するクラスタを特定
        │
        ▼
  高評価クラスタの centroid ベクトルを計算
        │
        ▼
  地図上の近傍クラスタを探索
  ┌──────────────────────────────────────────────────────┐
  │  "Diffusion Models" ← よく星をつけている            │
  │         ↓ 近い                                       │
  │  "Score-based Generative Models" ← まだ知らなかった │
  │  "Flow Matching" ← まだ知らなかった                 │
  └──────────────────────────────────────────────────────┘
        │
        ▼
  recommendations.json
  近傍クラスタから論文をおすすめ
```

---

## スコアリングの仕組み（日次）

daily-news skill が生成した `trend.md` に含まれる論文に対して、`config.json` に書いた **interest_profile** との意味的近さでスコアをつける。

```
abstract → Embedding ──┐
                        ├─ cosine similarity × 7 → 平均 = score（0〜1）
interest_profile × 7 ──┘
```

`config.json` の `interest_profile` に興味領域を自然言語で書くだけで自動計算される。
評価データが蓄積するにつれ、profile ベースから実績ベースへ段階的に移行する。

```
α = min(1.0, ratings件数 / 50)
final_score = α × instance_score + (1-α) × profile_score
```

ratings が少ない初期は `profile_score` が補完し、
蓄積されるにつれて実際の評価データ（`instance_score`）が主役になる。

## データの流れ

| ファイル | 内容 | 更新 |
|---|---|---|
| `data/YYYYMMDD.json` | 当日の論文 + スコア | 毎朝 |
| `data/ratings.json` | 星評価履歴の初期データ（Cloudflare KVへの移行元） | - |
| `data/map.json` | arXiv 論文地図（クラスタ + UMAP 2D 座標） | 月次 |
| `data/recommendations.json` | 近傍クラスタからのおすすめ論文 | 週次 |

星評価は **Cloudflare KV** に保存される（`POST /api/rate`）。
`recommend.py` は `config.json` の `ratings_url`（`GET /api/ratings`）からHTTPで取得する。
評価データを育てることがシステム全体の価値を高める。
