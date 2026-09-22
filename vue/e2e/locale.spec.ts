import {
  expect,
  rawNodeInfo,
  rawTask,
  rawVmXml,
  test,
} from "./fixtures";
import {
  expectNoHorizontalOverflow,
  installBrowserLanguages,
  installStoredLocale,
  LOCALE_STORAGE_KEY,
  selectLocale,
} from "./locale";

test("初期Setup dialogでlocaleを切り替え、reload後も保持する", async ({
  api,
  page,
}) => {
  api.setInitialized(false);
  await installBrowserLanguages(page, ["en-GB"]);
  await page.setViewportSize({ height: 844, width: 390 });
  const initialVersion = page.waitForResponse(
    response => new URL(response.url()).pathname === "/api/version",
  );
  await page.goto("/login");
  await initialVersion;

  let setupHeading = page.getByTestId("setup-title");
  await expect(setupHeading).toHaveText("Set up Virty");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  expect(
    await page.evaluate(key => localStorage.getItem(key), LOCALE_STORAGE_KEY),
  ).toBeNull();
  await expectNoHorizontalOverflow(page);

  // persistent dialogはsetupが完了するまでEscapeでも閉じない。
  await page.keyboard.press("Escape");
  await expect(setupHeading).toBeVisible();

  await page.getByTestId("setup-locale-switcher").click();
  await expect(page.getByTestId("locale-switcher-option-en")).toContainText(
    "English",
  );
  await expect(page.getByTestId("locale-switcher-option-ja")).toContainText(
    "日本語",
  );
  await page.getByTestId("locale-switcher-option-ja").click();

  await expect(page.locator("html")).toHaveAttribute("lang", "ja");
  await expect(setupHeading).toHaveText("Virtyのセットアップ");
  await expect(page).toHaveTitle("Virty - ログイン");
  expect(
    await page.evaluate(key => localStorage.getItem(key), LOCALE_STORAGE_KEY),
  ).toBe("ja");

  const reloadedVersion = page.waitForResponse(
    response => new URL(response.url()).pathname === "/api/version",
  );
  await page.reload();
  await reloadedVersion;
  setupHeading = page.getByTestId("setup-title");
  await expect(setupHeading).toHaveText("Virtyのセットアップ");
  await expect(page.locator("html")).toHaveAttribute("lang", "ja");
  await page.setViewportSize({ height: 900, width: 1_440 });
  await expectNoHorizontalOverflow(page);
});

test("locale切替でtaskのmessage、log、request、UUIDを改変しない", async ({
  authenticatedPage: page,
}) => {
  await installStoredLocale(page, "en");
  await page.setViewportSize({ height: 900, width: 1_440 });
  await page.goto("/tasks");

  await expect(page.getByText(rawTask.uuid, { exact: true })).toBeVisible();
  await expect(page.getByTestId("task-view-details")).toHaveAttribute("aria-label", "View details");
  await page.getByTestId("task-view-details").click();

  let dialog = page.getByRole("dialog");
  await expect(dialog.locator("pre").filter({ hasText: rawTask.message })).toBeVisible();
  await expect(dialog.locator("pre").filter({ hasText: rawTask.log })).toBeVisible();
  await expect(
    dialog.locator("pre").filter({ hasText: rawTask.request.opaqueToken }),
  ).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await selectLocale(page, "ja");
  await expect(page).toHaveTitle("Virty - タスク");
  await expect(page.getByText(rawTask.uuid, { exact: true })).toBeVisible();

  await expect(page.getByTestId("task-view-details")).toHaveAttribute("aria-label", "詳細を表示");
  await page.getByTestId("task-view-details").click();
  dialog = page.getByRole("dialog");
  await expect(dialog.locator("pre").filter({ hasText: rawTask.message })).toBeVisible();
  await expect(dialog.locator("pre").filter({ hasText: rawTask.log })).toBeVisible();
  await expect(
    dialog.locator("pre").filter({ hasText: rawTask.request.opaqueToken }),
  ).toBeVisible();
});

test("locale切替でVM XMLを改変しない", async ({ authenticatedPage: page }) => {
  await installStoredLocale(page, "en");
  await page.setViewportSize({ height: 900, width: 1_440 });
  const xmlResponse = page.waitForResponse(
    response => new URL(response.url()).pathname === "/api/vms/vm-e2e-uuid/xml",
  );
  await page.goto("/vms/vm-e2e-uuid");
  await xmlResponse;

  // VM詳細で唯一のexpansion controlを、表示言語に依存しないARIA属性で操作する。
  const xmlToggle = page.locator(
    'button.v-expansion-panel-title[aria-expanded="false"]',
  );
  await expect(xmlToggle).toHaveCount(1);
  await xmlToggle.click();
  const xmlOutput = page.locator("pre").filter({ hasText: "XML-UNCHANGED-42" });
  await expect(xmlOutput).toHaveText(rawVmXml);

  await selectLocale(page, "ja");
  await expect(xmlOutput).toHaveText(rawVmXml);
});

test("locale切替でSSH・Ansible由来のnode情報を改変しない", async ({
  authenticatedPage: page,
}) => {
  await installStoredLocale(page, "en");
  await page.setViewportSize({ height: 900, width: 1_440 });
  const infoResponse = page.waitForResponse(
    response => new URL(response.url()).pathname === "/api/nodes/node-e2e/info",
  );
  await page.goto("/nodes/node-e2e");
  await infoResponse;

  const sshOutput = page.locator("pre").filter({ hasText: rawNodeInfo.ssh });
  const ansibleOutput = page
    .locator("pre")
    .filter({ hasText: rawNodeInfo.ansible });
  await expect(sshOutput).toHaveText(rawNodeInfo.ssh);
  await expect(ansibleOutput).toHaveText(rawNodeInfo.ansible);

  await selectLocale(page, "ja");
  await expect(sshOutput).toHaveText(rawNodeInfo.ssh);
  await expect(ansibleOutput).toHaveText(rawNodeInfo.ansible);
});

test("Agent管理のchromeをreloadなしで英語から日本語へ切り替える", async ({
  authenticatedPage: page,
}) => {
  await installStoredLocale(page, "en");
  await page.setViewportSize({ height: 900, width: 1_440 });
  await page.goto("/agent");

  await expect(page.getByRole("heading", { name: "Agent control" })).toBeVisible();
  await expect(page.getByText("WebAuthn credential", { exact: true })).toBeVisible();
  await expect(page.getByText("Global mutation control", { exact: true })).toBeVisible();
  await expect(page.getByText("R1", { exact: true })).toBeVisible();

  await selectLocale(page, "ja");
  await expect(page.getByRole("heading", { name: "Agent管理" })).toBeVisible();
  await expect(page.getByText("WebAuthnクレデンシャル", { exact: true })).toBeVisible();
  await expect(page.getByText("変更操作の全体制御", { exact: true })).toBeVisible();
  await expect(page.getByText("R1", { exact: true })).toBeVisible();
  await expect(page).toHaveTitle("Virty - Agent管理");
});

test("Vuetify組込文言をreloadなしで英語から日本語へ切り替える", async ({
  authenticatedPage: page,
}) => {
  await installStoredLocale(page, "en");
  await page.goto("/vms");

  await expect(
    page.getByRole("button", { name: "Next page", exact: true }),
  ).toBeVisible();

  await selectLocale(page, "ja");
  await expect(
    page.getByRole("button", { name: "次のページ", exact: true }),
  ).toBeVisible();
  await expect(page).toHaveTitle("Virty - VM");
});
