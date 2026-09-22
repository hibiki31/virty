import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://web-fullstack-server";
if (baseURL !== "http://web-fullstack-server") {
  throw new Error("全層E2Eはdevctlが作成する閉じたCompose networkで実行してください");
}

export default defineConfig({
  testDir: "./e2e-fullstack",
  outputDir: "./fullstack-results/test-results",
  fullyParallel: false,
  workers: 1,
  forbidOnly: true,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: "./e2e-fullstack/reporter.ts",
  use: {
    baseURL,
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    locale: "en-US",
    screenshot: "off",
    trace: "off",
    video: "off",
  },
  projects: [{ name: "fullstack-chromium", use: { ...devices["Desktop Chrome"] } }],
});
