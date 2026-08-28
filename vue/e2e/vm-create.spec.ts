import { expect, test } from "./fixtures";

test("VM作成dialogのcancel、error、successを実ブラウザで確認する", async ({
  api,
  authenticatedPage: page,
}) => {
  await page.setViewportSize({ height: 844, width: 390 });
  await page.goto("/vms");

  await page.getByRole("button", { name: "CREATE" }).click();
  let dialog = page.getByTestId("vm-create-dialog");
  await expect(dialog).toBeVisible();
  await expect.poll(async () => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await dialog.getByTestId("vm-create-cancel").click();
  await expect(dialog).toBeHidden();

  await page.setViewportSize({ height: 900, width: 1_440 });
  await page.getByRole("button", { name: "CREATE" }).click();
  dialog = page.getByTestId("vm-create-dialog");
  await expect(dialog).toBeVisible();
  await dialog.getByTestId("vm-name").getByRole("textbox").fill("vm-new");

  await dialog.getByTestId("vm-project").click();
  await page.getByRole("option", { name: "Project E2E (#a1b2c3)" }).click();

  await dialog.getByTestId("vm-node").click();
  await page.getByRole("option", { name: "node-e2e" }).click();
  await dialog.getByTestId("vm-destination-pool").click();
  await page.getByRole("option", { name: "pool-e2e" }).click();
  await dialog.getByTestId("vm-network").click();
  await page.getByRole("option", { name: "net-e2e" }).click();

  api.failNextVmCreate();
  await dialog.getByTestId("vm-create-submit").click();
  await expect(page.getByText("VM already exists")).toBeVisible();
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
