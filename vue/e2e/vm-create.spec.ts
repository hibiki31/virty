import { expect, test } from "./fixtures";
import {
  expectNoHorizontalOverflow,
  installStoredLocale,
  localeCases,
} from "./locale";

for (const locale of localeCases) {
  test(`${locale.code}: VM作成dialogのcancel、error、successを確認する`, async ({
    api,
    authenticatedPage: page,
  }) => {
    await installStoredLocale(page, locale.code);
    await page.setViewportSize({ height: 844, width: 390 });
    await page.goto("/vms");

    await page.getByTestId("vm-create-open").click();
    let dialog = page.getByTestId("vm-create-dialog");
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText(locale.vmCreate, { exact: true })).toBeVisible();
    await expectNoHorizontalOverflow(page);
    await dialog.getByTestId("vm-create-cancel").click();
    await expect(dialog).toBeHidden();

    await page.setViewportSize({ height: 900, width: 1_440 });
    await page.getByTestId("vm-create-open").click();
    dialog = page.getByTestId("vm-create-dialog");
    await expect(dialog).toBeVisible();
    await expectNoHorizontalOverflow(page);
    await dialog.getByTestId("vm-name").getByRole("textbox").fill("vm-new");

    await dialog.getByTestId("vm-project").click();
    await page.getByRole("option", { name: "Project E2E (#a1b2c3)", exact: true }).click();

    await dialog.getByTestId("vm-node").click();
    await page.getByRole("option", { name: "node-e2e", exact: true }).click();
    await dialog.getByTestId("vm-destination-pool").click();
    await page.getByRole("option", { name: "pool-e2e", exact: true }).click();
    await dialog.getByTestId("vm-network").click();
    await page.getByRole("option", { name: "net-e2e", exact: true }).click();

    api.failNextVmCreate();
    await dialog.getByTestId("vm-create-submit").click();
    await expect(
      page.getByTestId("notification-body").filter({ hasText: locale.conflict }),
    ).toHaveText(locale.conflict);
    await expect(dialog).toBeVisible();

    await dialog.getByTestId("vm-create-submit").click();
    await expect(dialog).toBeHidden();
    expect(api.vmCreateBodies).toHaveLength(2);
    expect(api.vmCreateBodies[1]).toMatchObject({
      name: "vm-new",
      nodeName: "node-e2e",
      projectId: "a1b2c3",
    });
  });
}
