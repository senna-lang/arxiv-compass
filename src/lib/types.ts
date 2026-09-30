/**
 * arXiv新聞アプリの共通型定義
 *
 * Paper: data/YYYYMMDD.json の各論文エントリ
 * Rating: data/ratings.json の各評価エントリ
 * DailyData: data/YYYYMMDD.json のルート構造
 */

export type Paper = {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  url: string;
  categories: string[];
  submitted: string;
  score: number;
  github_url?: string;
  /** shadow mode の Jev 結果。meta.jev.status === "complete" の日だけ全論文に付く */
  jev?: JevRank;
};

/** SPECTER が選んだ同じ論文集合の中での Jev 順位。papers の並び（SPECTER順）は変えない */
export type JevRank = {
  specter_rank: number;
  rank: number;
  /** specter_rank - rank。正なら Jev では上位 */
  rank_delta: number;
  relevance_probability: number;
};

export type JevUnavailableReason = "timeout" | "inference_error" | "invalid_result";

export type JevModelIdentity = {
  base_id: string;
  base_revision: string;
  adapter_id: string;
  adapter_sha256: string;
  inference_version: string;
};

export type JevPredicateIdentity = {
  id: string;
  version: string;
  context_sha256: string;
};

/** 日次の Jev 実行結果。unavailable の日はどの論文にも jev が付かない */
export type JevRun =
  | { status: "complete"; model: JevModelIdentity; predicate: JevPredicateIdentity }
  | { status: "unavailable"; reason: JevUnavailableReason };

export type Rating = {
  paper_id: string;
  title: string;
  abstract: string;
  rating: 1 | 2 | 3;
  rated_at: string;
};

export type DailyData = {
  date: string;
  collected_at: string;
  papers: Paper[];
  meta: {
    total: number;
    model: string;
    /** parse.py 時代の日次JSONのみ */
    profile_version?: string;
    /** fetch_daily 以降の日次JSONのみ */
    source?: string;
    n_candidates?: number;
    n_ratings?: number;
    alpha?: number;
    /** shadow 導入前の日次JSONには存在しない */
    jev?: JevRun;
  };
};

export type RatingsData = {
  ratings: Rating[];
};

export type Cluster = {
  id: number;
  keywords: string[];
  label: string;
  centroid: number[];
  paper_ids: string[];
  size: number;
  umap_x: number;
  umap_y: number;
};

/** map.json 内の個別論文エントリ（座標 + クラスタID） */
export type MapPaper = {
  id: string;
  title?: string;
  abstract?: string;
  umap_x: number;
  umap_y: number;
  cluster_id: number | null;
};

export type MapData = {
  generated_at: string;
  total_papers: number;
  model: string;
  clusters: Cluster[];
  papers: MapPaper[];
};

/** ダッシュボードで表示する論文の統合型（map座標 + 日次データの詳細） */
export type DashboardPaper = MapPaper & {
  /** 日次JSONからマージされた詳細情報（存在する場合のみ） */
  abstract?: string;
  authors?: string[];
  url: string;
  categories?: string[];
  submitted?: string;
  score?: number;
  github_url?: string;
};

/** ダッシュボードのフィルタ状態 */
export type FilterState = {
  keyword: string;
  scoreRange: [number, number];
  selectedClusterIds: Set<number>;
};

export type Recommendation = {
  id: string;
  title: string;
  abstract: string;
  url: string;
  match_score: number;
  matched_cluster: string;
  submitted: string;
};

export type TopCluster = {
  label: string;
  score: number;
};

/** Recommendation と同じ構造だが意味的に区別するためのエイリアス */
export type SerendipityPaper = Recommendation;

export type RecommendationsData = {
  generated_at: string;
  top_clusters: TopCluster[];
  recommendations: Recommendation[];
  serendipity_clusters?: TopCluster[];
  serendipity?: SerendipityPaper[];
};
