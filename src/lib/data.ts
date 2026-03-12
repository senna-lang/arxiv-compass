/**
 * data/*.json を読み込むユーティリティ
 *
 * extractDates: import.meta.glob の結果から日付リストを返す（昇順）
 * getRecommendations: recommendations.json の内容を返す（ビルド時 node:fs 使用）
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { RecommendationsData } from "./types";

const DATA_DIR = join(process.cwd(), "data");

/**
 * import.meta.glob("/data/????????.json") の結果から日付文字列リストを返す。
 * glob呼び出し自体はViteの制約により各ページファイルで行う必要がある。
 */
export function extractDates(globResult: Record<string, unknown>): string[] {
	return Object.keys(globResult)
		.map((f) => f.replace("/data/", "").replace(".json", ""))
		.sort();
}

export function getRecommendations(): RecommendationsData | null {
	try {
		const raw = readFileSync(join(DATA_DIR, "recommendations.json"), "utf-8");
		return JSON.parse(raw) as RecommendationsData;
	} catch {
		return null;
	}
}
