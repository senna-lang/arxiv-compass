import { f as createComponent, r as renderTemplate, h as addAttribute, m as maybeRenderHead, i as createAstro, j as renderHead, k as renderComponent } from '../chunks/astro/server_BYcyX5dH.mjs';
import 'kleur/colors';
import 'clsx';
/* empty css                                  */
import { g as getPapersForDate, a as getRatingMap, b as getAvailableDates } from '../chunks/data_DVu3MZN7.mjs';
export { renderers } from '../renderers.mjs';

var __freeze = Object.freeze;
var __defProp = Object.defineProperty;
var __template = (cooked, raw) => __freeze(__defProp(cooked, "raw", { value: __freeze(cooked.slice()) }));
var _a;
const $$Astro$1 = createAstro();
const $$PaperCard = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro$1, $$props, $$slots);
  Astro2.self = $$PaperCard;
  const { paper, initialRating } = Astro2.props;
  const scorePercent = Math.round(paper.score * 100);
  const firstCategory = paper.categories[0] ?? "";
  return renderTemplate(_a || (_a = __template(["", '<article class="paper-card"', ' data-astro-cid-saq65afh> <header class="paper-header" data-astro-cid-saq65afh> <h2 class="paper-title" data-astro-cid-saq65afh> <a', ' target="_blank" rel="noopener noreferrer" data-astro-cid-saq65afh> ', ' </a> </h2> <div class="paper-meta" data-astro-cid-saq65afh> <span class="authors" data-astro-cid-saq65afh>', "", '</span> <span class="sep" data-astro-cid-saq65afh>\xB7</span> <span class="category" data-astro-cid-saq65afh>', '</span> <span class="sep" data-astro-cid-saq65afh>\xB7</span> <span class="score" data-astro-cid-saq65afh>score ', '%</span> </div> </header> <div class="paper-actions" data-astro-cid-saq65afh> <div class="star-rating"', "", "", "", " data-astro-cid-saq65afh> ", " </div> ", ' </div> <details class="abstract-details" data-astro-cid-saq65afh> <summary data-astro-cid-saq65afh>abstract \u3092\u8AAD\u3080 \u25BC</summary> <p class="abstract-text" data-astro-cid-saq65afh>', '</p> </details> </article>  <script src="/rate.js"><\/script>'])), maybeRenderHead(), addAttribute(paper.id, "data-paper-id"), addAttribute(paper.url, "href"), paper.title, paper.authors.slice(0, 3).join(", "), paper.authors.length > 3 ? " et al." : "", firstCategory, scorePercent, addAttribute(paper.id, "data-paper-id"), addAttribute(paper.title, "data-title"), addAttribute(paper.abstract, "data-abstract"), addAttribute(initialRating, "data-rating"), [1, 2, 3].map((n) => renderTemplate`<button${addAttribute(`star ${n <= initialRating ? "active" : ""}`, "class")}${addAttribute(n, "data-value")}${addAttribute(`${n}\u661F`, "aria-label")} data-astro-cid-saq65afh>★</button>`), paper.github_url && renderTemplate`<a class="github-link"${addAttribute(paper.github_url, "href")} target="_blank" rel="noopener noreferrer" data-astro-cid-saq65afh>
GitHub
</a>`, paper.abstract);
}, "/Users/senna/Documents/Repos/arxiv-newspaper/src/components/PaperCard.astro", void 0);

const $$RecommendSection = createComponent(($$result, $$props, $$slots) => {
  return renderTemplate`<!-- Phase 2: RecommendSection -->`;
}, "/Users/senna/Documents/Repos/arxiv-newspaper/src/components/RecommendSection.astro", void 0);

const $$Astro = createAstro();
const prerender = false;
const $$date = createComponent(($$result, $$props, $$slots) => {
  const Astro2 = $$result.createAstro($$Astro, $$props, $$slots);
  Astro2.self = $$date;
  const { date } = Astro2.params;
  if (!date || !/^\d{8}$/.test(date)) {
    return Astro2.redirect("/");
  }
  const papers = getPapersForDate(date);
  if (papers.length === 0) {
    return new Response("Not Found", { status: 404 });
  }
  const ratingMap = getRatingMap();
  const dates = getAvailableDates();
  const idx = dates.indexOf(date);
  const prevDate = idx > 0 ? dates[idx - 1] : null;
  const nextDate = idx < dates.length - 1 ? dates[idx + 1] : null;
  const displayDate = `${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)}`;
  return renderTemplate`<html lang="ja" data-astro-cid-gvncnrsm> <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>arXiv新聞 ${displayDate}</title>${renderHead()}</head> <body data-astro-cid-gvncnrsm> <header data-astro-cid-gvncnrsm> <h1 data-astro-cid-gvncnrsm>📰 arXiv新聞 ${displayDate}</h1> <nav class="nav" data-astro-cid-gvncnrsm> ${prevDate ? renderTemplate`<a${addAttribute(`/${prevDate}`, "href")} data-astro-cid-gvncnrsm>← 前日</a>` : renderTemplate`<span data-astro-cid-gvncnrsm>← 前日</span>`} ${nextDate ? renderTemplate`<a${addAttribute(`/${nextDate}`, "href")} data-astro-cid-gvncnrsm>翌日 →</a>` : renderTemplate`<span data-astro-cid-gvncnrsm>翌日 →</span>`} </nav> </header> <p class="count" data-astro-cid-gvncnrsm>${papers.length} 件</p> ${papers.map((paper) => renderTemplate`${renderComponent($$result, "PaperCard", $$PaperCard, { "paper": paper, "initialRating": ratingMap.get(paper.id) ?? 0, "data-astro-cid-gvncnrsm": true })}`)} ${renderComponent($$result, "RecommendSection", $$RecommendSection, { "data-astro-cid-gvncnrsm": true })} </body></html>`;
}, "/Users/senna/Documents/Repos/arxiv-newspaper/src/pages/[date].astro", void 0);

const $$file = "/Users/senna/Documents/Repos/arxiv-newspaper/src/pages/[date].astro";
const $$url = "/[date]";

const _page = /*#__PURE__*/Object.freeze(/*#__PURE__*/Object.defineProperty({
  __proto__: null,
  default: $$date,
  file: $$file,
  prerender,
  url: $$url
}, Symbol.toStringTag, { value: 'Module' }));

const page = () => _page;

export { page };
