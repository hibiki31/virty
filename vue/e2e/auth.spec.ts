import { expect, test } from "./fixtures";
import { installStoredLocale, localeCases } from "./locale";

for (const locale of localeCases) {
  test(`${locale.code}: protected deep linkからloginし元のrouteへ戻る`, async ({
    api: _api,
    page,
  }) => {
    await installStoredLocale(page, locale.code);
    await page.goto("/vms/vm-e2e-uuid");

    await expect(page).toHaveURL(/\/login\?redirect=/);
    await expect(page.locator("html")).toHaveAttribute("lang", locale.code);
    await expect(page.getByTestId("locale-switcher")).toBeVisible();
    await expect(page.getByLabel(locale.userId, { exact: true })).toBeVisible();
    await expect(page.getByLabel(locale.password, { exact: true })).toBeVisible();
    await page.getByTestId("login-username").getByRole("textbox").fill("operator");
    await page.getByTestId("login-password").getByRole("textbox").fill("password");
    await page.getByTestId("login-submit").click();

    await expect(page).toHaveURL(/\/vms\/vm-e2e-uuid$/);
    await expect(page).toHaveTitle("Virty - vm-e2e");
  });
}
