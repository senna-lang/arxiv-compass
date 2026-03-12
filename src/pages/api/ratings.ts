/**
 * 全評価データ取得APIエンドポイント
 *
 * GET /api/ratings
 *
 * 処理:
 * 1. Cloudflare KV から ratings を取得
 * 2. RatingsData JSON を返す
 *
 * 用途: recommend.py などのバッチスクリプトがローカルから参照する
 */
export const prerender = false;

import { env } from "cloudflare:workers";
import type { APIRoute } from "astro";
import type { RatingsData } from "../../lib/types";

export const GET: APIRoute = async () => {
  const kv = env.RATINGS_KV;
  const existing = await kv.get("ratings");
  const data: RatingsData = existing ? JSON.parse(existing) : { ratings: [] };

  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
};
