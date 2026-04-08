import { defineConfig } from "astro/config";
import cloudflare from "@astrojs/cloudflare";
import react from "@astrojs/react";

export default defineConfig({
	output: "static",
	adapter: cloudflare(),
	integrations: [react()],
	image: {
		service: { entrypoint: "astro/assets/services/noop" },
	},
	vite: {
		ssr: {
			external: ["sharp"],
		},
	},
});
