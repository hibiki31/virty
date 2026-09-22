import { expect, test } from "./fixtures";
import { installStoredLocale, localeCases, selectLocale } from "./locale";

for (const locale of localeCases) {
  test(`${locale.code}: Project一覧から共同管理情報を確認できる`, async ({
    authenticatedPage: page,
  }) => {
    await installStoredLocale(page, locale.code);
    await page.goto("/projects");

    await expect(page).toHaveTitle(`Virty - ${locale.projectsTitle}`);
    const projectLink = page.getByRole("link", { name: "Project E2E (#a1b2c3)" });
    await expect(projectLink).toBeVisible();
    await projectLink.click();

    await expect(page).toHaveURL(/\/projects\/a1b2c3$/);
    await expect(page.getByText(locale.projectLimits, { exact: true })).toBeVisible();
    await expect(page.getByText("operator", { exact: true })).toBeVisible();
    await expect(page.getByText("storage-e2e (#1)")).toBeVisible();
    await expect(page).toHaveTitle("Virty - Project E2E (#a1b2c3)");
  });

  test(`${locale.code}: Project作成ではsigned-in adminを明示memberに含める`, async ({
    api,
    authenticatedPage: page,
  }) => {
    await installStoredLocale(page, locale.code);
    await page.goto("/projects");
    await page.getByTestId("project-create-open").click();

    const dialog = page.getByRole("dialog");
    await expect(dialog.getByText(locale.projectCreate, { exact: true })).toBeVisible();
    await expect(dialog.getByText("operator", { exact: true })).toBeVisible();
    await dialog.getByTestId("project-name").locator("input").fill("Created E2E");
    await dialog.getByTestId("project-create-submit").click();

    await expect.poll(() => api.projectCreateBodies.length).toBe(1);
    expect(api.projectCreateBodies[0]).toEqual({
      name: "Created E2E",
      memberIds: ["operator"],
    });
  });
}

test("Project詳細をreloadなしで英語から日本語へ切り替える", async ({
  authenticatedPage: page,
}) => {
  await installStoredLocale(page, "en");
  await page.goto("/projects/a1b2c3");

  await expect(
    page.getByText("Limits (not enforced)", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText(
      "Shared ownership boundary for virtual machines and granted resources",
      { exact: true },
    ),
  ).toBeVisible();

  await selectLocale(page, "ja");
  await expect(page.getByText("上限（未適用）", { exact: true })).toBeVisible();
  await expect(
    page.getByText("VMと許可されたリソースを共同所有する境界", { exact: true }),
  ).toBeVisible();
  await expect(page).toHaveTitle("Virty - Project E2E (#a1b2c3)");
});
