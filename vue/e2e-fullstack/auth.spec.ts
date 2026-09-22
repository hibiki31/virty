import { test, expect } from "./fixtures";

test.describe("空DBからの初期設定", () => {
  test.use({ initialized: false });

  test("初期管理者を作り、login・logout・再loginを実APIで確認する", async ({ fullstack, page, seed }) => {
    await page.goto("/vms");
    const setup = page.getByRole("dialog");
    await expect(page.getByTestId("setup-title")).toBeVisible();
    await setup.getByLabel("Admin username", { exact: true }).fill(seed.users.admin.username);
    try {
      await setup.getByTestId("new-password").locator("input").fill(seed.users.admin.password);
      await setup.getByTestId("confirm-password").locator("input").fill(seed.users.admin.password);
    } catch {
      throw new Error("初期管理者のpassword入力に失敗しました");
    }
    const submitted = page.waitForResponse(response => new URL(response.url()).pathname === "/api/auth/setup");
    await setup.getByRole("button", { name: "Setup", exact: true }).click();
    expect((await submitted).status()).toBe(201);
    await expect(setup).toBeHidden();
    await fullstack.enterCredentials(seed.users.admin);
    await fullstack.expectPath("/vms");
    await expect(page.getByTestId("admin-mode-switch").locator("input")).not.toBeChecked();
    await expect(page.getByTestId("vm-admin-create-open")).toHaveCount(0);
    await fullstack.enableAdminMode();
    await expect(page.getByTestId("vm-admin-create-open")).toBeVisible();
    const version = await fullstack.api<{ initialized: boolean }>("/api/version");
    expect(version.data.initialized).toBe(true);

    await fullstack.logout();
    expect((await page.context().cookies()).some(cookie => cookie.name === "accessToken")).toBe(false);
    await expect(page.getByTestId("admin-mode-switch")).toHaveCount(0);
    await fullstack.enterCredentials(seed.users.admin);
    await fullstack.expectPath("/vms");
    await expect(page.getByTestId("admin-mode-switch").locator("input")).not.toBeChecked();
    await expect(page.getByTestId("vm-admin-create-open")).toHaveCount(0);
    const current = await fullstack.api<{ username: string }>("/api/users/me");
    expect(current.status).toBe(200);
    expect(current.data.username).toBe(seed.users.admin.username);
  });
});

test("誤ったpasswordは401になり、再入力後は元のrouteへ戻る", async ({ fullstack, page, seed }) => {
  await page.goto("/projects");
  const refused = page.waitForResponse(response => new URL(response.url()).pathname === "/api/auth");
  await fullstack.enterCredentials({ ...seed.users.admin, password: "Invalid-password-456!" });
  expect((await refused).status()).toBe(401);
  await expect(page).toHaveURL(/\/login\?redirect=/);
  await expect(page.getByTestId("notification-body").filter({ hasText: "The username or password is incorrect." })).toBeVisible();
  await fullstack.enterCredentials(seed.users.admin);
  await fullstack.expectPath("/projects");
  await expect(page.getByTestId("admin-mode-switch").locator("input")).not.toBeChecked();
  await expect(page.getByRole("link", { name: "E2E Alpha (#aa0001)", exact: true })).toBeVisible();
});

test("期限切れの署名済みtokenを実APIが拒否し、cookie除去後に再認証できる", async ({ fullstack, page, seed, baseURL }) => {
  await fullstack.login(seed.users.admin);
  const expired = await fullstack.control<{ access_token: string }>("expired-token", { username: seed.users.admin.username });
  await page.context().addCookies([{ name: "accessToken", value: expired.access_token, url: baseURL! }]);
  const rejected = page.waitForResponse(response => new URL(response.url()).pathname === "/api/auth/validate");
  await page.reload();
  expect((await rejected).status()).toBe(401);
  await expect(page).toHaveURL(/\/login\?redirect=/);
  await expect(page.getByTestId("notification-body").filter({ hasText: "The authentication token has expired." })).toBeVisible();
  expect((await page.context().cookies()).some(cookie => cookie.name === "accessToken")).toBe(false);
  await fullstack.enterCredentials(seed.users.admin);
  await fullstack.expectPath("/vms");
  await expect(page.getByTestId("admin-mode-switch").locator("input")).not.toBeChecked();
});
