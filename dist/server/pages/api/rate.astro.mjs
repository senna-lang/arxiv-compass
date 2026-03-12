import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
export { renderers } from '../../renderers.mjs';

const prerender = false;
const RATINGS_PATH = join(process.cwd(), "data", "ratings.json");
const POST = async ({ request }) => {
  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  const { paper_id, title, abstract, rating } = body;
  if (!paper_id || typeof rating !== "number" || rating < 1 || rating > 3) {
    return new Response(JSON.stringify({ error: "Invalid parameters" }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }
  let data = { ratings: [] };
  try {
    const raw = readFileSync(RATINGS_PATH, "utf-8");
    data = JSON.parse(raw);
  } catch {
  }
  const rated_at = (/* @__PURE__ */ new Date()).toISOString();
  const newEntry = { paper_id, title, abstract, rating, rated_at };
  const idx = data.ratings.findIndex((r) => r.paper_id === paper_id);
  if (idx >= 0) {
    data.ratings[idx] = newEntry;
  } else {
    data.ratings.push(newEntry);
  }
  writeFileSync(RATINGS_PATH, JSON.stringify(data, null, 2) + "\n", "utf-8");
  const dateStr = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10).replace(/-/g, "");
  try {
    execSync(
      `git add data/ratings.json && git commit -m "rate: ${dateStr}" && git push`,
      { cwd: process.cwd(), stdio: "pipe" }
    );
  } catch {
  }
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
};

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  POST,
  prerender
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
