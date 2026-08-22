const DEFAULT_PLAYWRIGHT_BASE_URL = "http://127.0.0.1:4173";

/** Playwrightの接続先をHTTP専用test runtimeへ制限する。 */
export function resolvePlaywrightBaseURL(value: string | undefined): string {
  const baseURL = value ?? DEFAULT_PLAYWRIGHT_BASE_URL;
  const parsed = new URL(baseURL);
  if (parsed.protocol !== "http:") {
    throw new Error(
      `Playwright E2Eの接続先はHTTP専用です: ${parsed.protocol}`,
    );
  }
  return baseURL;
}

export const playwrightBaseURL = resolvePlaywrightBaseURL(
  process.env.PLAYWRIGHT_BASE_URL,
);
