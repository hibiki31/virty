import { expect, test } from "./fixtures";

test("Project一覧から共同管理情報を確認できる", async ({ authenticatedPage: page }) => {
  await page.goto("/projects");

  const projectLink = page.getByRole("link", { name: "Project E2E (#a1b2c3)" });
  await expect(projectLink).toBeVisible();
  await projectLink.click();

  await expect(page).toHaveURL(/\/projects\/a1b2c3$/);
  await expect(page.getByText("Limits (not enforced)")).toBeVisible();
  await expect(page.getByText("operator", { exact: true })).toBeVisible();
  await expect(page.getByText("storage-e2e (#1)")).toBeVisible();
});

test("Project作成ではsigned-in adminを明示memberに含める", async ({
  api,
  authenticatedPage: page,
}) => {
  await page.goto("/projects");
  await page.getByRole("button", { name: "CREATE" }).click();

  const dialog = page.getByRole("dialog");
  await expect(dialog.getByText("operator", { exact: true })).toBeVisible();
  await dialog.getByTestId("project-name").locator("input").fill("Created E2E");
  await dialog.getByRole("button", { name: "Create", exact: true }).click();

  await expect.poll(() => api.projectCreateBodies.length).toBe(1);
  expect(api.projectCreateBodies[0]).toEqual({
    name: "Created E2E",
    memberIds: ["operator"],
  });
});
