import { expect, type Locator, type Page } from "@playwright/test";

export const LOCALE_STORAGE_KEY = "virty:locale";

export const localeCases = [
  {
    code: "en",
    conflict: "The request conflicts with the current resource state.",
    dashboardVm: "Virtual Machines",
    login: "Login",
    nextPage: "Next page",
    password: "Password",
    userId: "User ID",
    vmCreate: "Create VM",
  },
  {
    code: "ja",
    conflict: "現在のリソース状態と競合しています。",
    dashboardVm: "仮想マシン",
    login: "ログイン",
    nextPage: "次のページ",
    password: "パスワード",
    userId: "ユーザーID",
    vmCreate: "VMの作成",
  },
] as const;

export type LocaleCase = (typeof localeCases)[number];

export async function installBrowserLanguages(
  page: Page,
  languages: readonly string[],
): Promise<void> {
  await page.addInitScript(values => {
    Object.defineProperty(navigator, "languages", {
      configurable: true,
      get: () => values,
    });
    Object.defineProperty(navigator, "language", {
      configurable: true,
      get: () => values[0] ?? "",
    });
  }, [...languages]);
}

export async function installStoredLocale(
  page: Page,
  locale: LocaleCase["code"],
): Promise<void> {
  await page.addInitScript(
    ({ key, value }) => localStorage.setItem(key, value),
    { key: LOCALE_STORAGE_KEY, value: locale },
  );
}

export async function selectLocale(
  page: Page,
  locale: LocaleCase["code"],
  scope?: Locator,
): Promise<void> {
  const switcher = (scope ?? page).getByTestId("locale-switcher");
  await switcher.click();
  await page.getByTestId(`locale-switcher-option-${locale}`).click();
  await expect(page.locator("html")).toHaveAttribute("lang", locale);
}

export async function expectNoHorizontalOverflow(page: Page): Promise<void> {
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          Math.max(
            document.documentElement.scrollWidth,
            document.body?.scrollWidth ?? 0,
          ) <= window.innerWidth,
      ),
    )
    .toBe(true);
}
