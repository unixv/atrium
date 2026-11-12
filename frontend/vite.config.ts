import { defineConfig } from "vite";

export default defineConfig({
  server: {
    proxy: {
      "/ws": {
        target: "ws://server:8787",
        ws: true,
      },
    },
  },
});
