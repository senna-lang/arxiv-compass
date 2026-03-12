import { defineConfig } from "astro/config";
import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
	output: "static",
	adapter: cloudflare(),
	image: {
		service: { entrypoint: "astro/assets/services/noop" },
	},
	vite: {
		ssr: {
			external: ["sharp"],
		},
	},
});
