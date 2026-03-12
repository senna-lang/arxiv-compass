/**
 * 星評価保存APIエンドポイント
 *
 * POST /api/rate
 * Body: { paper_id: string, title: string, abstract: string, rating: number }
 *
 * 処理:
 * 1. data/ratings.json を読み込む
 * 2. 同一paper_idがあれば上書き、なければ追記
 * 3. data/ratings.json を書き込む
 * 4. git add + commit + push（best effort）
 * 5. 200 OK を返す
 */
export const prerender = false;

import type { APIRoute } from "astro";
import { execSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import type { Rating, RatingsData } from "../../lib/types";

const RATINGS_PATH = join(process.cwd(), "data", "ratings.json");

export const POST: APIRoute = async ({ request }) => {
  let body: { paper_id: string; title: string; abstract: string; rating: number };

  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const { paper_id, title, abstract, rating } = body;
  if (!paper_id || typeof rating !== "number" || rating < 1 || rating > 3) {
    return new Response(JSON.stringify({ error: "Invalid parameters" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  // ratings.json 読み込み
  let data: RatingsData = { ratings: [] };
  try {
    const raw = readFileSync(RATINGS_PATH, "utf-8");
    data = JSON.parse(raw);
  } catch {
    // ファイルがなければ空で始める
  }

  const rated_at = new Date().toISOString();
  const newEntry: Rating = { paper_id, title, abstract, rating, rated_at };

  const idx = data.ratings.findIndex((r) => r.paper_id === paper_id);
  if (idx >= 0) {
    data.ratings[idx] = newEntry;
  } else {
    data.ratings.push(newEntry);
  }

  writeFileSync(RATINGS_PATH, JSON.stringify(data, null, 2) + "\n", "utf-8");

  // git add + commit + push（best effort）
  const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  try {
    execSync(
      `git add data/ratings.json && git commit -m "rate: ${dateStr}" && git push`,
      { cwd: process.cwd(), stdio: "pipe" }
    );
  } catch {
    // pushに失敗してもAPIは成功を返す
  }

  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
};
