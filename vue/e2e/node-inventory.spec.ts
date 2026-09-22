import { expect, test } from "./fixtures";

test("管理者のnode一覧から詳細・診断まで管理用readを指定する", async ({
  authenticatedPage: page,
}) => {
  const inventoryResponse = page.waitForResponse(
    response => new URL(response.url()).pathname === "/api/nodes",
  );
  await page.goto("/nodes");
  expect(new URL((await inventoryResponse).url()).searchParams.get("admin")).toBe("true");

  const detailResponse = page.waitForResponse(
    response => new URL(response.url()).pathname === "/api/nodes/node-e2e",
  );
  const infoResponse = page.waitForResponse(
    response => new URL(response.url()).pathname === "/api/nodes/node-e2e/info",
  );
  await page.getByRole("link", { name: "node-e2e", exact: true }).click();
  for (const response of await Promise.all([detailResponse, infoResponse])) {
    expect(new URL(response.url()).searchParams.get("admin")).toBe("true");
  }
  await expect(page.getByText("E2E node", { exact: true })).toBeVisible();
});
