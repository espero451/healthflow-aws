import { defineConfig } from "@playwright/test";

export default defineConfig({
  timeout: 60000,
  retries: 0,
  use: {
    baseURL: process.env.UI_BASE_URL || "http://localhost:5173"
  }
});
