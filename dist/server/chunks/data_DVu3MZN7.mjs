import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const DATA_DIR = join(process.cwd(), "data");
function getAvailableDates() {
  try {
    const files = readdirSync(DATA_DIR);
    return files.filter((f) => /^\d{8}\.json$/.test(f)).map((f) => f.replace(".json", "")).sort();
  } catch {
    return [];
  }
}
function getPapersForDate(date) {
  try {
    const raw = readFileSync(join(DATA_DIR, `${date}.json`), "utf-8");
    const data = JSON.parse(raw);
    return data.papers;
  } catch {
    return [];
  }
}
function getRatings() {
  try {
    const raw = readFileSync(join(DATA_DIR, "ratings.json"), "utf-8");
    const data = JSON.parse(raw);
    return data.ratings;
  } catch {
    return [];
  }
}
function getRatingMap() {
  const ratings = getRatings();
  return new Map(ratings.map((r) => [r.paper_id, r.rating]));
}

export { getRatingMap as a, getAvailableDates as b, getPapersForDate as g };
