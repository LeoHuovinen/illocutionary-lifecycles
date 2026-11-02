// Builds livekit_bars.jsx into ../page/livekit_bars.js, one module a plain page imports.
//   npx vite build --config vite.livekit_bars.config.mjs
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  define: { "process.env.NODE_ENV": '"production"' },
  build: {
    lib: { entry: "livekit_bars.jsx", formats: ["es"], fileName: () => "livekit_bars.js" },
    outDir: "../page", emptyOutDir: false, minify: true,
    rollupOptions: { output: { inlineDynamicImports: true } },
  },
});
