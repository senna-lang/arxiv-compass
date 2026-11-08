/** GET/POST/DELETE /api/topics. KV key "topics". */
export const prerender = false;

import type { APIRoute } from "astro";
import type { TopicsData } from "../../lib/types";

const MAX_TOPICS = 20;
const MAX_LEN = 200;

async function readTopics(kv: KVNamespace): Promise<TopicsData> {
	const raw = await kv.get("topics");
	return raw ? JSON.parse(raw) : { topics: [] };
}

function kvOf(locals: App.Locals): KVNamespace {
	return (locals.runtime?.env as Cloudflare.Env).RATINGS_KV;
}

export const GET: APIRoute = async ({ url, locals }) => {
	const next = url.searchParams.get("next");
	if (next) return Response.redirect(next, 302);
	const data = await readTopics(kvOf(locals));
	return Response.json(data);
};

export const POST: APIRoute = async ({ request, locals }) => {
	let body: { text?: string };
	try { body = await request.json(); } catch { return Response.json({ error: "Invalid JSON" }, { status: 400 }); }
	const text = String(body.text ?? "").trim();
	const kv = kvOf(locals);
	const data = await readTopics(kv);
	const dup = data.topics.some((t) => t.text.toLowerCase() === text.toLowerCase());
	if (!text || text.length > MAX_LEN || dup || data.topics.length >= MAX_TOPICS) {
		return Response.json({ error: "Invalid topic" }, { status: 400 });
	}
	data.topics.push({ text, added_at: new Date().toISOString() });
	await kv.put("topics", JSON.stringify(data));
	return Response.json({ ok: true, topics: data.topics });
};

export const DELETE: APIRoute = async ({ request, locals }) => {
	let body: { text?: string };
	try { body = await request.json(); } catch { return Response.json({ error: "Invalid JSON" }, { status: 400 }); }
	const text = String(body.text ?? "").trim().toLowerCase();
	const kv = kvOf(locals);
	const data = await readTopics(kv);
	data.topics = data.topics.filter((t) => t.text.toLowerCase() !== text);
	await kv.put("topics", JSON.stringify(data));
	return Response.json({ ok: true, topics: data.topics });
};
