import { expect, test, vm } from "./fixtures";

const routes = [
  ["/", "/api/dashboard"],
  ["/vms", "/api/vms"],
  ["/storages", "/api/storages"],
  ["/images", "/api/images"],
  ["/networks", "/api/networks"],
  ["/projects", "/api/projects"],
  ["/vms/vm-e2e-uuid", "/api/vms/vm-e2e-uuid"],
  ["/projects/a1b2c3", "/api/projects/a1b2c3"],
  ["/storages/pool-e2e", "/api/storages/pool-e2e"],
  ["/networks/net-e2e", "/api/networks/net-e2e"],
];

for (const [pagePath, apiPath] of routes) {
  test(`${pagePath}: 管理者のresource参照を指定する`, async ({ authenticatedPage: page }) => {
    await page.route("**/api/storages/pool-e2e?*", route => route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ name: "pool-e2e", uuid: "pool-e2e", nodeName: "node-e2e", path: "/images", available: 50 }),
    }));
    await page.route("**/api/networks/net-e2e?*", route => route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ name: "net-e2e", uuid: "net-e2e", nodeName: "node-e2e", type: "bridge", portgroups: [] }),
    }));
    await page.route("**/api/networks/net-e2e/xml?*", route => route.fulfill({
      contentType: "application/json", body: JSON.stringify({ xml: "<network/>" }),
    }));
    const xmlPath = pagePath === "/vms/vm-e2e-uuid" || pagePath === "/networks/net-e2e"
      ? `${apiPath}/xml` : undefined;
    const xmlResponse = xmlPath
      ? page.waitForResponse(value => new URL(value.url()).pathname === xmlPath)
      : undefined;
    const response = page.waitForResponse(value => new URL(value.url()).pathname === apiPath);
    await page.goto(pagePath);
    const result = await response;
    expect(result.status()).toBe(200);
    expect(new URL(result.url()).searchParams.get("admin"), result.url()).toBe("true");
    if (xmlResponse) {
      expect(new URL((await xmlResponse).url()).searchParams.get("admin")).toBe("true");
    }
  });
}

test("管理者は他人のVMのコンソールを開ける", async ({ authenticatedPage: page }) => {
  await page.route("**/api/vms/vm-e2e-uuid?*", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({ ...vm, ownerUserId: "another-user", vncPort: 5901 }),
  }));
  let adminParam: string | null = null;
  await page.route("**/api/vms/vm-e2e-uuid/console-ticket?*", route => {
    adminParam = new URL(route.request().url()).searchParams.get("admin");
    return route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ token: "ticket-e2e", expiresIn: 60 }),
    });
  });

  await page.goto("/vms/vm-e2e-uuid");

  const consoleButton = page.getByRole("button", { name: "Console" });
  await expect(consoleButton).toBeEnabled();
  const popupPromise = page.waitForEvent("popup");
  await consoleButton.click();
  const popup = await popupPromise;
  await expect.poll(() => popup.url()).toContain("/novnc/vnc.html");
  expect(adminParam).toBe("true");
});

test("所有するVMではコンソールを開ける", async ({ authenticatedPage: page }) => {
  await page.route("**/api/vms/vm-e2e-uuid?*", route => route.fulfill({
    contentType: "application/json",
    body: JSON.stringify({ ...vm, vncPort: 5901 }),
  }));

  await page.goto("/vms/vm-e2e-uuid");

  await expect(page.getByRole("button", { name: "Console" })).toBeEnabled();
});
