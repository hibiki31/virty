import { expect, test } from "./fixtures";

test("dashboardからVM一覧と詳細へ遷移する", async ({ authenticatedPage: page }) => {
  await page.goto("/");

  await expect(page.getByText("Virtual Machines", { exact: true })).toBeVisible();
  await page.getByText("Virtual Machines", { exact: true }).click();
  await expect(page).toHaveURL(/\/vms$/);

  await page.getByRole("link", { name: "vm-e2e-uuid" }).click();
  await expect(page).toHaveURL(/\/vms\/vm-e2e-uuid$/);
  await expect(page).toHaveTitle("Virty - vm-e2e");
});
