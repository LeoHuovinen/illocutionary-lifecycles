import { defineConfig } from "vite";
export default defineConfig({
  build: { lib: { entry: "rive.js", formats: ["es"], fileName: () => "pipecat_rive.js" }, outDir: "../page", emptyOutDir: false, minify: true,
    rollupOptions: { output: { inlineDynamicImports: true } } },
});
