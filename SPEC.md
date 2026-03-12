# arXiv新聞アプリ 仕様書

## 解決したい課題

arXivには毎日数百件の論文が投稿される。カテゴリ（cs.CL, cs.LG等）でフィルタしても
まだ多すぎて、自分の興味に近い論文を見つけるのが難しい。

**キーワード検索では「知らない隣接領域」は発見できない。**
自分が知らないキーワードで書かれた論文は検索に引っかからないため、
興味の外側にある重要な論文を見逃し続ける。

### 解決アプローチ

arXiv論文群をテキストクラスタリングで「地図化」する。
地図上に自分の興味の位置を投影することで、
キーワードを知らなくても意味的に近い論文を発見できる。

```
arXiv論文群（大量）をクラスタリング → 「地図」を作る
　　　　×
自分のレーティング履歴 → 「地図上の自分の位置」を特定
　　　　↓
自分の位置に近いクラスタの論文を抽出 → おすすめとして表示
```

---

## システム構成

```
daily-newsスキル（既存・変更なし）
  └─ ideas/daily/YYYYMMDD-trend.md を生成

parse.py（毎朝・trend.md生成後に実行）
  └─ YYYYMMDD-trend.md のarXivセクションをパース
       └─ abstractをEmbeddingしてscoreを付与
            └─ data/YYYYMMDD.json に保存

Astro新聞アプリ
  └─ data/*.json を読んで表示
       └─ 自分で星をつける → ratings.json → Git push

map.py（月次）
  └─ arXiv論文群（過去N件）を大量取得
       └─ HDBSCANでクラスタリング → 「地図」生成
            └─ map.json に保存

recommend.py（週次）
  └─ ratings.json から自分の興味ベクトルを算出
       └─ map.json の地図上に投影 → 近傍クラスタを特定
            └─ 近傍クラスタ内の論文をスコアリング
                 └─ recommendations.json に保存
```

---

## ディレクトリ構成

```
arxiv-newspaper/
├── data/
│   ├── 20250311.json          # 当日の論文（collect.pyが生成）
│   ├── 20250310.json
│   ├── ratings.json           # 星履歴（資産・最重要）
│   ├── map.json               # arXiv地図（map.pyが月次生成）
│   └── recommendations.json   # おすすめ論文（recommend.pyが週次生成）
├── scripts/
│   ├── parse.py               # trend.mdをパース+Embedding→JSON変換（毎朝）
│   ├── map.py                 # arXiv地図生成（月次）
│   └── recommend.py           # おすすめ生成（週次）
├── src/                       # Astroソース
│   ├── pages/
│   │   ├── index.astro        # 今日の論文
│   │   └── map.astro          # 地図の可視化（UMAP 2D）
│   └── components/
│       ├── PaperCard.astro    # 論文カード（星UI付き）
│       └── RecommendSection.astro
├── public/
│   └── rate.js                # 星をつけてGit pushするJS
├── config.json
└── package.json
```

---

## データ仕様

### `data/YYYYMMDD.json`

parse.pyが毎朝生成。daily-newsスキルが出力した`YYYYMMDD-trend.md`のarXivセクションを変換したもの。

```json
{
  "date": "2025-03-11",
  "collected_at": "2025-03-11T09:00:00+09:00",
  "papers": [
    {
      "id": "2503.12345",
      "title": "Efficient Attention via Sparse Patterns",
      "authors": ["Alice Smith (MIT)", "Bob Jones (CMU)"],
      "abstract": "We propose...",
      "url": "https://arxiv.org/abs/2503.12345",
      "categories": ["cs.CL", "cs.LG"],
      "submitted": "2025-03-10",
      "score": 0.82,
      "github_url": "https://github.com/xxx/yyy"
    }
  ],
  "meta": {
    "total": 187,
    "model": "all-MiniLM-L6-v2",
    "profile_version": "1"
  }
}
```

### `data/ratings.json`

ユーザーが星をつけるたびに追記。全システムの起点となる資産。

```json
{
  "ratings": [
    {
      "paper_id": "2503.12345",
      "title": "Efficient Attention via Sparse Patterns",
      "abstract": "We propose...",
      "rating": 3,
      "rated_at": "2025-03-11T10:30:00+09:00"
    }
  ]
}
```

### `data/map.json`

map.pyが月次で生成。BERTopicによるトピックモデリング結果＝「地図」。

```json
{
  "generated_at": "2025-03-01T00:00:00+09:00",
  "total_papers": 10000,
  "model": "all-MiniLM-L6-v2",
  "clusters": [
    {
      "id": 0,
      "keywords": ["inference", "latency", "throughput", "serving", "quantization"],
      "label": "inference optimization",
      "centroid": [...],
      "paper_ids": ["2503.12345", "2502.98765"],
      "size": 312,
      "umap_x": 2.34,
      "umap_y": -1.12
    },
    {
      "id": 1,
      "keywords": ["prompt", "injection", "jailbreak", "attack", "defense"],
      "label": "prompt injection & LLM security",
      "centroid": [...],
      "paper_ids": ["2503.11111"],
      "size": 198,
      "umap_x": -3.21,
      "umap_y": 0.87
    }
  ]
}
```

`keywords`はBERTopicのc-TF-IDFが自動生成するトピックキーワード。
`label`はkeywordsの先頭をベースに人間が読みやすい形で付与する（自動または手動）。

### `data/recommendations.json`

recommend.pyが週次で生成。

```json
{
  "generated_at": "2025-03-11T00:00:00+09:00",
  "top_clusters": [
    {"label": "inference optimization", "score": 0.92},
    {"label": "prompt injection & LLM security", "score": 0.87}
  ],
  "recommendations": [
    {
      "id": "2501.11111",
      "title": "...",
      "abstract": "...",
      "url": "https://arxiv.org/abs/2501.11111",
      "match_score": 0.92,
      "matched_cluster": "inference optimization",
      "submitted": "2025-01-15"
    }
  ]
}
```

---

## スクリプト仕様

### `scripts/parse.py`（毎朝）

daily-newsスキルが生成した`YYYYMMDD-trend.md`のarXivセクションをパースし、
Embeddingとスコアリングを付与してJSONに変換する。

**処理フロー**
1. `config.json`の`trend_dir`から`YYYYMMDD-trend.md`を読み込む（別リポジトリの`life/ideas/daily/`を参照）
2. 論文ごとにタイトル・著者・arXiv ID・概要を抽出
3. abstractをsentence-transformersでベクトル化
4. `config.json`の興味プロファイルとのcos類似度をscoreとして付与
5. scoreの降順でソートして`data/YYYYMMDD.json`に保存

**実行**
```bash
python scripts/parse.py
python scripts/parse.py --date 2025-03-10
```

**依存**
```
sentence-transformers>=2.7.0
numpy>=1.26.0
```

---

### `scripts/map.py`（月次）

arXiv論文群を大量取得し、BERTopicでトピックモデリング＋クラスタリングを行って地図を生成する。

**BERTopicを採用する理由**

BERTopicはEmbedding → UMAP次元削減 → HDBSCANクラスタリング → トピックラベル生成を
一貫したパイプラインとして提供する。個別にHDBSCAN・UMAPを呼ぶ必要がなくなり、
クラスタのラベル付けもTF-IDFより意味的に精度が高い。

```
allenai/specter2（Embedding）
        ↓
BERTopic
  ├─ UMAP（random_state=42）→ 次元削減 → 2D座標（地図の座標軸）
  ├─ HDBSCAN（内包）         → クラスタリング
  └─ c-TF-IDF（内包）        → トピックキーワード自動生成 → クラスタラベル
        ↓
map.json に保存
```

**処理フロー**
1. arXiv APIで対象カテゴリの過去N件（デフォルト10000件）を取得
2. abstractを`allenai/specter2`でベクトル化（学術論文の引用関係で訓練済み）
3. BERTopicにEmbeddingを渡してトピック抽出
   - UMAPは`random_state=42`で固定（同一入力なら結果が再現可能）
   - 各論文にtopic_idが割り当てられる
   - 各トピックにキーワードリストが自動生成される（クラスタラベルとして使用）
   - UMAP 2D座標が生成される（地図の座標軸として使用）
4. 各トピック（クラスタ）のcentroidを計算
5. `map.json`に保存

**実行**
```bash
python scripts/map.py
python scripts/map.py --max-papers 20000
```

**依存**
```
arxiv>=2.1.0
sentence-transformers>=2.7.0
bertopic>=0.16.0
numpy>=1.26.0
# specter2はsentence-transformersから直接ロード可能（別途インストール不要）
# AutoModel.from_pretrained("allenai/specter2")
```

**備考**
- BERTopicがUMAP・HDBSCANを内包するため個別インストール不要
- 初回は時間がかかる（10000件のEmbeddingは数十分）
- 地図自体は月1回の更新で十分（arXivの構造は急変しない）
- トピックの粒度はBERTopicのmin_cluster_sizeで調整可能
- **クラスタIDの非安定性**: 月次再生成時に入力論文が変わるとtopic_idは変わりうる。`recommend.py`や`recommendations.json`ではIDではなく`label`（キーワードベースの文字列）を安定識別子として使うこと。IDはmap.json内部の参照にのみ使用する

---

### `scripts/recommend.py`（週次）

ratings.jsonから各クラスタのスコアを算出し、おすすめ論文を生成。

**処理フロー**
1. `ratings.json`から★2以上の論文を抽出
2. 抽出した論文のabstractをその場でEmbedding（再計算）
   - ratings.jsonにembeddingは保存しない（高評価論文は多くて数百件のため再計算コストは無視できる）
   - `config.json`の`embedding_model`を使用（map.pyと同じモデルで空間を統一すること）
3. `map.json`の各クラスタをinstance-based scoringで評価：
   ```
   score(cluster_c) = mean( cos_sim(centroid_c, v_i) for v_i in rated_embeddings )
   ```
   ※ 単純平均ではなく各論文が独立に投票する方式。多峰性の興味を正しく扱える。
3. ratings件数に応じてinterest_profileのスコアと加重合成：
   ```
   α = min(1.0, ratings件数 / 50)
   final_score = α * instance_score + (1-α) * cos_sim(centroid, profile_vec)
   ```
   ratings 0件: profile_vecのみ。ratings 50件以上: instance_scoreのみ。
4. 上位N件のクラスタを「自分の近傍クラスタ」として特定
5. 近傍クラスタ内の論文をスコアリングして上位を抽出
6. `recommendations.json`に保存

**実行**
```bash
python scripts/recommend.py
python scripts/recommend.py --top-clusters 3 --top-n 20
```

**備考**
- ratings.jsonが少ない初期はinterest_profileが補完するため初日から動作する
- 複数方向の興味（inference optimizationとLLMセキュリティ等）はinstance-based scoringで自然に扱える（各論文が自分に近いクラスタに票を投じるため平均による情報損失がない）
- ratings 50件以上でPhase 3へ: `ratings.json`の高評価論文をHDBSCAN(min_cluster_size=5)でクラスタリングし、興味ペルソナを自動分離してペルソナ別に近傍探索する

---

## Astroアプリ仕様

### 画面構成

```
┌─────────────────────────────────────┐
│  📰 arXiv新聞  2025-03-11           │
│  [← 前日]                [翌日 →]   │
├─────────────────────────────────────┤
│  論文A                              │
│  Efficient Attention via...         │
│  Alice Smith (MIT) · cs.CL · 0.82  │
│  ★★☆  [abstract を読む ▼]          │
│  [GitHub]                           │
├─────────────────────────────────────┤
│  論文B ...                          │
├─────────────────────────────────────┤
│  🔍 過去記事からのおすすめ           │
│  ※ あなたの近傍クラスタ:            │
│     inference optimization (92%)    │
│  論文X  マッチ度 92%                │
│  論文Y  マッチ度 87%                │
└─────────────────────────────────────┘
```

### map.astro（地図ページ）

UMAPの2次元座標を使ってarXivの地図をインタラクティブに表示。
自分の近傍クラスタをハイライト表示する。

```
各クラスタ = 散布図上の点（sizeに比例した大きさ）
自分の位置 = ★マークでオーバーレイ
ホバー     = クラスタラベル・代表論文を表示
```

### 星UI・レーティング保存フロー

1. ユーザーが星をクリック
2. `rate.js`がローカルの`ratings.json`を更新
3. `git add data/ratings.json && git commit -m "rate: YYYYMMDD" && git push`
4. GitHub Actions（またはCloudflare Pages）が自動でサイトをリビルド

### ホスティング

- **GitHub Pages** または **Cloudflare Pages**
- `data/*.json`はリポジトリに含める（Gitが履歴管理）

---

## `config.json`

```json
{
  "categories": ["cs.CL", "cs.LG", "cs.AI", "cs.CR"],
  "max_results_daily": 200,
  "max_results_map": 10000,
  "interest_profile": [
    "LLM inference optimization and serving efficiency",
    "attention mechanism variants and efficient transformers",
    "large language model internals and interpretability",
    "tokenization and embedding representations",
    "MLOps and LLM deployment infrastructure",
    "prompt injection and LLM security attacks",
    "AI agent tool use and reasoning"
  ],
  "embedding_model": "allenai/specter2",
  "trend_dir": "/Users/senna/Documents/Repos/life/ideas/daily",
  "output_dir": "data",
  "recommendation": {
    "min_rating": 2,
    "top_clusters": 3,
    "top_n": 20,
    "min_match_score": 0.75
  }
}
```

---

## 実行スケジュール

```
毎朝 09:00   daily-newsスキル実行 → YYYYMMDD-trend.md 生成
毎朝 09:30   parse.py             → YYYYMMDD.json 生成
毎週日曜     recommend.py         → recommendations.json 更新
毎月1日      map.py               → map.json（地図）更新
```

---

## 既存daily-newsスキルとの関係

| | daily-newsスキル（既存） | 本システム |
|---|---|---|
| arXiv取得 | /recent（直近2日、head -400） | trend.mdをparse.pyが変換 |
| スコアリング | Claudeが主観で判断 | sentence-transformersで定量化 |
| 出力 | trend.md（人間が読む） | YYYYMMDD.json（アプリが読む） |
| 過去論文 | 対応不可 | 地図＋おすすめで発見可能 |

daily-newsスキルは変更不要。parse.pyがtrend.mdを読んでJSON化するだけ。

### リポジトリ分割方針

本システムは`life`リポジトリとは**別リポジトリ**（`arxiv-newspaper`）として管理する。

```
life/                          （既存・変更なし）
  ideas/daily/YYYYMMDD-trend.md  ← daily-newsスキルが生成
  .claude/skills/daily-news/

arxiv-newspaper/               （本システム・新規）
  config.json                    trend_dir で life リポジトリを参照
  scripts/
  data/
  src/
```

**分割する理由:**
- ratings.json へのコミットが `life` の git log を汚さない
- GitHub Pages / Cloudflare Pages がリポジトリルートから素直にデプロイできる
- 関心の分離（情報収集 vs 論文推薦アプリ）

**クロスリポジトリ依存は `config.json` の `trend_dir` 1行のみ。**

---

## フェーズ別ロードマップ

### Phase 1（～1ヶ月）
- collect.py + Astro新聞アプリの基本動作
- 毎日論文を読んで星をつける習慣をつくる

### Phase 2（ratings 20件以上）
- map.py で地図を初回生成
- recommend.py でおすすめを表示（instance-based scoring + profile 加重合成）
- map.astro で地図を可視化

### Phase 3（ratings 50件以上）
- ratings自体をHDBSCANでクラスタリング → 興味ペルソナを自動分離
- ペルソナ別に独立して近傍クラスタを探索してマージ（多峰性の完全対応）
- interest_profileをレーティング結果で自動更新

---

## 将来拡張メモ

- Hacker NewsやZennの記事も同様にレーティング対象に追加
- 「3ヶ月前と今で自分の興味の重心がどう移動したか」の時系列可視化
- LLMキャリアのGate別（Gate1/2/3）に興味クラスタをタグ付け
