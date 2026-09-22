import { test, expect } from "./fixtures";
import type { components } from "../src/api/openapi";

test("Project作成taskとresource grantを保存し、所属memberが許可資源を参照する", async ({ fullstack, page, seed }) => {
  await fullstack.login(seed.users.admin, "/projects", { adminMode: true });
  await test.step("管理者とmemberを含むProjectを画面から作成する", async () => {
    await page.getByTestId("project-create-open").click();
    const dialog = page.getByRole("dialog");
    await dialog.getByTestId("project-name").locator("input").fill("E2E Created Project");
    await dialog.getByTestId("project-members").locator("input").fill(seed.users.member.username);
    await page.getByRole("option", { name: seed.users.member.username, exact: true }).click();
    await page.keyboard.press("Escape");
    const submitted = page.waitForResponse(response => new URL(response.url()).pathname === "/api/tasks/projects" && response.request().method() === "POST");
    await dialog.getByTestId("project-create-submit").click();
    const tasks = await fullstack.tasks(await submitted);
    await expect(dialog).toBeHidden();
    for (const task of tasks) await fullstack.waitTask(task);
  });

  const projects = await fullstack.api<components["schemas"]["ProjectPage"]>("/api/projects?admin=true&nameLike=E2E%20Created%20Project&limit=0&page=0");
  expect(projects.status).toBe(200);
  expect(projects.data.count).toBe(1);
  const project = projects.data.data[0]!;
  await page.goto("/projects");
  await page.getByRole("link", { name: `${project.name} (#${project.id})`, exact: true }).click();
  await expect(page.locator("main")).toContainText(seed.users.member.username);

  await test.step("storage・network・flavorのgrantを画面から保存する", async () => {
    await page.getByRole("button", { name: "Edit grants", exact: true }).click();
    for (const [field, name] of [
      ["project-grant-storage-pools", seed.resources.storagePoolName],
      ["project-grant-network-pools", seed.resources.networkPoolName],
      ["project-grant-flavors", seed.resources.flavorName],
    ]) {
      await page.getByTestId(field).click();
      await page.getByRole("option", { name, exact: true }).click();
      await page.keyboard.press("Escape");
    }
    const updated = page.waitForResponse(response => new URL(response.url()).pathname.endsWith("/resource-grants") && response.request().method() === "PUT");
    await page.getByRole("button", { name: "Save grants", exact: true }).click();
    expect((await updated).status()).toBe(200);
    await page.reload();
    await expect(page.locator("main")).toContainText(`${seed.resources.storagePoolName} (#${seed.resources.storagePoolId})`);
    const persisted = await fullstack.api<components["schemas"]["ProjectDetail"]>(`/api/projects/${project.id}?admin=true`);
    expect(persisted.data.resourceGrants).toEqual({
      storagePoolIds: [seed.resources.storagePoolId],
      networkPoolIds: [seed.resources.networkPoolId],
      flavorIds: [seed.resources.flavorId],
    });
    expect(persisted.data.members.map(member => member.username).sort()).toEqual([seed.users.admin.username, seed.users.member.username].sort());
  });

  await fullstack.logout();
  await fullstack.enterCredentials(seed.users.member);
  await fullstack.expectPath(`/projects/${project.id}`);
  await expect(page.getByTestId("admin-mode-switch")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Edit grants", exact: true })).toHaveCount(0);
  await page.goto(`/storages?projectId=${project.id}`);
  await expect(page.locator("tbody")).toContainText(seed.resources.storageName);
});
