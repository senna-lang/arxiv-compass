/**
 * data/*.json を読み込むユーティリティ
 *
 * getAvailableDates: data/ 以下のYYYYMMDD.jsonから日付リストを返す（昇順）
 * getPapersForDate: 指定日付の論文配列を返す
 * getRatings: ratings.json の評価配列を返す
 * getRatingMap: paper_id → rating のMapを返す
 */

import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import type { DailyData, Paper, Rating, RatingsData } from "./types";

const DATA_DIR = join(process.cwd(), "data");

export function getAvailableDates(): string[] {
  try {
    const files = readdirSync(DATA_DIR);
    return files
      .filter((f) => /^\d{8}\.json$/.test(f))
      .map((f) => f.replace(".json", ""))
      .sort();
  } catch {
    return [];
  }
}

export function getPapersForDate(date: string): Paper[] {
  try {
    const raw = readFileSync(join(DATA_DIR, `${date}.json`), "utf-8");
    const data: DailyData = JSON.parse(raw);
    return data.papers;
  } catch {
    return [];
  }
}

export function getRatings(): Rating[] {
  try {
    const raw = readFileSync(join(DATA_DIR, "ratings.json"), "utf-8");
    const data: RatingsData = JSON.parse(raw);
    return data.ratings;
  } catch {
    return [];
  }
}

export function getRatingMap(): Map<string, number> {
  const ratings = getRatings();
  return new Map(ratings.map((r) => [r.paper_id, r.rating]));
}
