import '@astrojs/internal-helpers/path';
import 'cookie';
import 'kleur/colors';
import { N as NOOP_MIDDLEWARE_FN } from './chunks/astro-designed-error-pages_Cnkwhz-U.mjs';
import 'es-module-lexer';
import { l as decodeKey } from './chunks/astro/server_BYcyX5dH.mjs';
import 'clsx';

function sanitizeParams(params) {
  return Object.fromEntries(
    Object.entries(params).map(([key, value]) => {
      if (typeof value === "string") {
        return [key, value.normalize().replace(/#/g, "%23").replace(/\?/g, "%3F")];
      }
      return [key, value];
    })
  );
}
function getParameter(part, params) {
  if (part.spread) {
    return params[part.content.slice(3)] || "";
  }
  if (part.dynamic) {
    if (!params[part.content]) {
      throw new TypeError(`Missing parameter: ${part.content}`);
    }
    return params[part.content];
  }
  return part.content.normalize().replace(/\?/g, "%3F").replace(/#/g, "%23").replace(/%5B/g, "[").replace(/%5D/g, "]");
}
function getSegment(segment, params) {
  const segmentPath = segment.map((part) => getParameter(part, params)).join("");
  return segmentPath ? "/" + segmentPath : "";
}
function getRouteGenerator(segments, addTrailingSlash) {
  return (params) => {
    const sanitizedParams = sanitizeParams(params);
    let trailing = "";
    if (addTrailingSlash === "always" && segments.length) {
      trailing = "/";
    }
    const path = segments.map((segment) => getSegment(segment, sanitizedParams)).join("") + trailing;
    return path || "/";
  };
}

function deserializeRouteData(rawRouteData) {
  return {
    route: rawRouteData.route,
    type: rawRouteData.type,
    pattern: new RegExp(rawRouteData.pattern),
    params: rawRouteData.params,
    component: rawRouteData.component,
    generate: getRouteGenerator(rawRouteData.segments, rawRouteData._meta.trailingSlash),
    pathname: rawRouteData.pathname || void 0,
    segments: rawRouteData.segments,
    prerender: rawRouteData.prerender,
    redirect: rawRouteData.redirect,
    redirectRoute: rawRouteData.redirectRoute ? deserializeRouteData(rawRouteData.redirectRoute) : void 0,
    fallbackRoutes: rawRouteData.fallbackRoutes.map((fallback) => {
      return deserializeRouteData(fallback);
    }),
    isIndex: rawRouteData.isIndex
  };
}

function deserializeManifest(serializedManifest) {
  const routes = [];
  for (const serializedRoute of serializedManifest.routes) {
    routes.push({
      ...serializedRoute,
      routeData: deserializeRouteData(serializedRoute.routeData)
    });
    const route = serializedRoute;
    route.routeData = deserializeRouteData(serializedRoute.routeData);
  }
  const assets = new Set(serializedManifest.assets);
  const componentMetadata = new Map(serializedManifest.componentMetadata);
  const inlinedScripts = new Map(serializedManifest.inlinedScripts);
  const clientDirectives = new Map(serializedManifest.clientDirectives);
  const serverIslandNameMap = new Map(serializedManifest.serverIslandNameMap);
  const key = decodeKey(serializedManifest.key);
  return {
    // in case user middleware exists, this no-op middleware will be reassigned (see plugin-ssr.ts)
    middleware() {
      return { onRequest: NOOP_MIDDLEWARE_FN };
    },
    ...serializedManifest,
    assets,
    componentMetadata,
    inlinedScripts,
    clientDirectives,
    routes,
    serverIslandNameMap,
    key
  };
}

const manifest = deserializeManifest({"hrefRoot":"file:///Users/senna/Documents/Repos/arxiv-newspaper/","adapterName":"@astrojs/node","routes":[{"file":"index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/","isIndex":true,"type":"page","pattern":"^\\/$","segments":[],"params":[],"component":"src/pages/index.astro","pathname":"/","prerender":true,"fallbackRoutes":[],"_meta":{"trailingSlash":"ignore"}}},{"file":"","links":[],"scripts":[],"styles":[],"routeData":{"type":"endpoint","isIndex":false,"route":"/_image","pattern":"^\\/_image$","segments":[[{"content":"_image","dynamic":false,"spread":false}]],"params":[],"component":"node_modules/astro/dist/assets/endpoint/node.js","pathname":"/_image","prerender":false,"fallbackRoutes":[],"_meta":{"trailingSlash":"ignore"}}},{"file":"","links":[],"scripts":[],"styles":[],"routeData":{"route":"/api/rate","isIndex":false,"type":"endpoint","pattern":"^\\/api\\/rate\\/?$","segments":[[{"content":"api","dynamic":false,"spread":false}],[{"content":"rate","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/api/rate.ts","pathname":"/api/rate","prerender":false,"fallbackRoutes":[],"_meta":{"trailingSlash":"ignore"}}},{"file":"","links":[],"scripts":[],"styles":[{"type":"inline","content":".paper-card[data-astro-cid-saq65afh]{border:1px solid #e0e0e0;border-radius:8px;padding:1.25rem;margin-bottom:1rem;background:#fff}.paper-title[data-astro-cid-saq65afh]{font-size:1rem;font-weight:600;margin:0 0 .4rem;line-height:1.4}.paper-title[data-astro-cid-saq65afh] a[data-astro-cid-saq65afh]{color:#1a0dab;text-decoration:none}.paper-title[data-astro-cid-saq65afh] a[data-astro-cid-saq65afh]:hover{text-decoration:underline}.paper-meta[data-astro-cid-saq65afh]{font-size:.82rem;color:#555;display:flex;flex-wrap:wrap;gap:.25rem;margin-bottom:.75rem}.sep[data-astro-cid-saq65afh]{color:#aaa}.paper-actions[data-astro-cid-saq65afh]{display:flex;align-items:center;gap:1rem;margin-bottom:.75rem}.star-rating[data-astro-cid-saq65afh]{display:flex;gap:.15rem}.star[data-astro-cid-saq65afh]{background:none;border:none;cursor:pointer;font-size:1.4rem;color:#ccc;padding:0;line-height:1;transition:color .1s}.star[data-astro-cid-saq65afh].active,.star[data-astro-cid-saq65afh]:hover{color:#f5a623}.github-link[data-astro-cid-saq65afh]{font-size:.8rem;padding:.2rem .6rem;border:1px solid #ccc;border-radius:4px;color:#333;text-decoration:none}.github-link[data-astro-cid-saq65afh]:hover{background:#f5f5f5}.abstract-details[data-astro-cid-saq65afh] summary[data-astro-cid-saq65afh]{font-size:.82rem;color:#666;cursor:pointer;user-select:none}.abstract-text[data-astro-cid-saq65afh]{margin-top:.75rem;font-size:.88rem;line-height:1.6;color:#333;white-space:pre-wrap}[data-astro-cid-gvncnrsm]{box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;max-width:800px;margin:0 auto;padding:1rem;background:#f8f8f8;color:#222}header[data-astro-cid-gvncnrsm]{display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem;flex-wrap:wrap;gap:.5rem}h1[data-astro-cid-gvncnrsm]{font-size:1.4rem;margin:0}.nav[data-astro-cid-gvncnrsm]{display:flex;gap:.75rem}.nav[data-astro-cid-gvncnrsm] a[data-astro-cid-gvncnrsm]{font-size:.88rem;color:#1a0dab;text-decoration:none;padding:.2rem .5rem;border:1px solid #ccc;border-radius:4px}.nav[data-astro-cid-gvncnrsm] a[data-astro-cid-gvncnrsm]:hover{background:#e8e8e8}.nav[data-astro-cid-gvncnrsm] span[data-astro-cid-gvncnrsm]{font-size:.88rem;color:#aaa;padding:.2rem .5rem}.count[data-astro-cid-gvncnrsm]{font-size:.82rem;color:#666;margin-bottom:1rem}\n"}],"routeData":{"route":"/[date]","isIndex":false,"type":"page","pattern":"^\\/([^/]+?)\\/?$","segments":[[{"content":"date","dynamic":true,"spread":false}]],"params":["date"],"component":"src/pages/[date].astro","prerender":false,"fallbackRoutes":[],"_meta":{"trailingSlash":"ignore"}}}],"base":"/","trailingSlash":"ignore","compressHTML":true,"componentMetadata":[["/Users/senna/Documents/Repos/arxiv-newspaper/src/pages/[date].astro",{"propagation":"none","containsHead":true}],["/Users/senna/Documents/Repos/arxiv-newspaper/src/pages/index.astro",{"propagation":"none","containsHead":true}]],"renderers":[],"clientDirectives":[["idle","(()=>{var l=(o,t)=>{let i=async()=>{await(await o())()},e=typeof t.value==\"object\"?t.value:void 0,s={timeout:e==null?void 0:e.timeout};\"requestIdleCallback\"in window?window.requestIdleCallback(i,s):setTimeout(i,s.timeout||200)};(self.Astro||(self.Astro={})).idle=l;window.dispatchEvent(new Event(\"astro:idle\"));})();"],["load","(()=>{var e=async t=>{await(await t())()};(self.Astro||(self.Astro={})).load=e;window.dispatchEvent(new Event(\"astro:load\"));})();"],["media","(()=>{var s=(i,t)=>{let a=async()=>{await(await i())()};if(t.value){let e=matchMedia(t.value);e.matches?a():e.addEventListener(\"change\",a,{once:!0})}};(self.Astro||(self.Astro={})).media=s;window.dispatchEvent(new Event(\"astro:media\"));})();"],["only","(()=>{var e=async t=>{await(await t())()};(self.Astro||(self.Astro={})).only=e;window.dispatchEvent(new Event(\"astro:only\"));})();"],["visible","(()=>{var l=(s,i,o)=>{let r=async()=>{await(await s())()},t=typeof i.value==\"object\"?i.value:void 0,c={rootMargin:t==null?void 0:t.rootMargin},n=new IntersectionObserver(e=>{for(let a of e)if(a.isIntersecting){n.disconnect(),r();break}},c);for(let e of o.children)n.observe(e)};(self.Astro||(self.Astro={})).visible=l;window.dispatchEvent(new Event(\"astro:visible\"));})();"]],"entryModules":{"\u0000noop-middleware":"_noop-middleware.mjs","\u0000@astro-page:node_modules/astro/dist/assets/endpoint/node@_@js":"pages/_image.astro.mjs","\u0000@astro-page:src/pages/api/rate@_@ts":"pages/api/rate.astro.mjs","\u0000@astro-page:src/pages/[date]@_@astro":"pages/_date_.astro.mjs","\u0000@astro-page:src/pages/index@_@astro":"pages/index.astro.mjs","\u0000@astrojs-ssr-virtual-entry":"entry.mjs","\u0000@astro-renderers":"renderers.mjs","\u0000@astrojs-ssr-adapter":"_@astrojs-ssr-adapter.mjs","/Users/senna/Documents/Repos/arxiv-newspaper/node_modules/astro/dist/env/setup.js":"chunks/astro/env-setup_Cr6XTFvb.mjs","\u0000@astrojs-manifest":"manifest_CaXM1nup.mjs","astro:scripts/before-hydration.js":""},"inlinedScripts":[],"assets":["/rate.js","/index.html"],"buildFormat":"directory","checkOrigin":false,"serverIslandNameMap":[],"key":"kVCazywEL9H7aO1DyKakbxfgliTKZKdo5pcUbmpdrpE=","experimentalEnvGetSecretEnabled":false});

export { manifest };
