import { expect, test } from "./fixtures";
import {
  expectNoHorizontalOverflow,
  installStoredLocale,
  localeCases,
} from "./locale";

for (const locale of localeCases) {
  test(`${locale.code}: dashboardからVM一覧と詳細へ遷移する`, async ({
    authenticatedPage: page,
  }) => {
    await installStoredLocale(page, locale.code);
    await page.setViewportSize({ height: 900, width: 1_440 });
    await page.goto("/");

    const vmKpi = page.getByTestId("dashboard-kpi-vms");
    await expect(vmKpi).toBeVisible();
    await expect(vmKpi).toContainText(locale.dashboardVm);
    await expect(page.locator("html")).toHaveAttribute("lang", locale.code);
    await expectNoHorizontalOverflow(page);
    await vmKpi.click();
    await expect(page).toHaveURL(/\/vms$/);

    // Vuetify組込のpagination ARIAも、アプリと同じlocaleへ追従する。
    await expect(
      page.getByRole("button", { name: locale.nextPage, exact: true }),
    ).toBeVisible();
    await page.setViewportSize({ height: 844, width: 390 });
    await expectNoHorizontalOverflow(page);

    await page.getByRole("link", { name: "vm-e2e-uuid", exact: true }).click();
    await expect(page).toHaveURL(/\/vms\/vm-e2e-uuid$/);
    await expect(page).toHaveTitle("Virty - vm-e2e");
  });
}
