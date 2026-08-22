import { describe, expect, it } from "vitest";

import { resolvePlaywrightBaseURL } from "./base-url";

describe("Playwright base URL", () => {
  it("明示したHTTP接続先を受け入れる", () => {
    expect(resolvePlaywrightBaseURL("http://web-e2e-server")).toBe(
      "http://web-e2e-server",
    );
  });

  it("production TLS接続先との混同を拒否する", () => {
    expect(() => resolvePlaywrightBaseURL("https://virty.test")).toThrow(
      "Playwright E2Eの接続先はHTTP専用です: https:",
    );
  });
});
