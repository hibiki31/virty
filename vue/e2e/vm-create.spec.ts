import { expect, test } from "./fixtures";
import {
  expectNoHorizontalOverflow,
  installStoredLocale,
  localeCases,
} from "./locale";

for (const locale of localeCases) {
  test(`${locale.code}: 管理者用VM作成はProjectなしで利用できる`, async ({
    api,
    authenticatedPage: page,
  }) => {
    await installStoredLocale(page, locale.code);
    await page.route("**/api/projects?*", route => route.fulfill({
      json: { count: 0, data: [] },
    }));
    const resourceRequests: URL[] = [];
    page.on("request", request => {
      const url = new URL(request.url());
      if (["/api/nodes", "/api/storages", "/api/networks", "/api/images"].includes(url.pathname)) {
        resourceRequests.push(url);
      }
    });
    await page.setViewportSize({ height: 844, width: 390 });
    await page.goto("/vms");
    const opener = page.getByTestId("vm-admin-create-open");
    await opener.click();
    const dialog = page.getByTestId("vm-create-dialog");
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText(locale.code === "ja" ? "管理者としてVMを作成" : "Create VM as admin", { exact: true })).toBeVisible();
    await expect(dialog.getByTestId("vm-project")).toHaveCount(0);
    await expectNoHorizontalOverflow(page);
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();

    await page.setViewportSize({ height: 900, width: 1440 });
    await opener.press("Enter");
    await expect(dialog).toBeVisible();
    await expectNoHorizontalOverflow(page);
    await dialog.getByTestId("vm-name").getByRole("textbox").fill("admin-vm-new");
    await dialog.getByTestId("vm-node").click();
    await page.getByRole("option", { name: "node-e2e", exact: true }).click();
    await dialog.getByTestId("vm-destination-pool").click();
    await page.getByRole("option", { name: "pool-e2e", exact: true }).click();
    await dialog.getByTestId("vm-network").click();
    await page.getByRole("option", { name: "net-e2e", exact: true }).click();

    api.failNextVmCreate();
    await dialog.getByTestId("vm-create-submit").click();
    await expect(page.getByTestId("notification-body").filter({ hasText: locale.conflict })).toBeVisible();
    await expect(dialog.getByTestId("vm-name").getByRole("textbox")).toHaveValue("admin-vm-new");
    const requestPromise = page.waitForRequest(request => request.url().endsWith("/api/tasks/vms/admin"));
    await dialog.getByTestId("vm-create-submit").click();
    await requestPromise;
    await expect(dialog).toBeHidden();
    expect(api.vmCreateBodies).toHaveLength(2);
    expect(api.vmCreateBodies[1]).toMatchObject({ name: "admin-vm-new", projectId: null });
    expect(new Set(resourceRequests.map(url => url.pathname)).size).toBe(4);
    expect(resourceRequests.every(url => url.searchParams.get("admin") === "true" && !url.searchParams.has("projectId"))).toBe(true);
  });

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
