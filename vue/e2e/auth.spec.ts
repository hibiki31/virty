import { expect, test } from "./fixtures";

test("protected deep linkからloginし元のrouteへ戻る", async ({ api: _api, page }) => {
  await page.goto("/vms/vm-e2e-uuid");

  await expect(page).toHaveURL(/\/login\?redirect=/);
  await page.getByLabel("ID").fill("operator");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: "Login" }).click();

  await expect(page).toHaveURL(/\/vms\/vm-e2e-uuid$/);
  await expect(page).toHaveTitle("Virty - vm-e2e");
});
