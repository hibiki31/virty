import { defineConfig, devices } from "@playwright/test";
import { playwrightBaseURL } from "./e2e/base-url";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  // 複数worktreeの並列検証でbrowser同士がCPUを奪い合わないようにする。
  workers: 2,
  forbidOnly: true,
  reporter: "line",
  retries: 0,
  timeout: 30_000,
  use: {
    baseURL: playwrightBaseURL,
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
