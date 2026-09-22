import { test, expect } from "./fixtures";

test("管理者は全Projectと管理画面を参照できる", async ({ fullstack, page, seed }) => {
  await fullstack.login(seed.users.admin, "/projects", { adminMode: true });
  await expect(page.getByTestId("project-create-open")).toBeVisible();
  for (const project of Object.values(seed.projects)) {
    await expect(page.getByRole("link", { name: `${project.name} (#${project.id})`, exact: true })).toBeVisible();
  }
  await page.goto("/users");
  await fullstack.expectPath("/users");
  await expect(page.locator("main").getByText(seed.users.member.username, { exact: true })).toBeVisible();
  const current = await fullstack.api<{ data: unknown[] }>("/api/users?limit=0&page=0");
  expect(current.status).toBe(200);
  expect(current.data.data).toHaveLength(3);
});

for (const role of ["member", "outsider"] as const) {
  test(`${role}は所属Projectだけを参照し、管理操作と他Projectを拒否される`, async ({ fullstack, page, seed }) => {
    const own = role === "member" ? "alpha" : "beta";
    const other = own === "alpha" ? "beta" : "alpha";
    await fullstack.login(seed.users[role], "/projects");
    await expect(page.getByTestId("admin-mode-switch")).toHaveCount(0);
    await expect(page.getByTestId("project-create-open")).toHaveCount(0);
    await expect(page.getByRole("link", { name: `${seed.projects[own].name} (#${seed.projects[own].id})`, exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: `${seed.projects[other].name} (#${seed.projects[other].id})`, exact: true })).toHaveCount(0);
    await page.goto("/users");
    await fullstack.expectPath("/");
    expect((await fullstack.api("/api/users?limit=0&page=0")).status).toBe(403);
    expect((await fullstack.api("/api/tasks/projects", "POST", {
      name: "Denied project", memberIds: [seed.users[role].username],
    })).status).toBe(403);
    expect((await fullstack.api(`/api/projects/${seed.projects[own].id}/resource-grants`, "PUT", {
      storagePoolIds: [], networkPoolIds: [], flavorIds: [],
    })).status).toBe(403);
    const refused = page.waitForResponse(response => new URL(response.url()).pathname === `/api/projects/${seed.projects[other].id}`);
    await page.goto(`/projects/${seed.projects[other].id}`);
    expect((await refused).status()).toBe(404);
    await expect(page.getByTestId("notification-body").filter({ hasText: "The project was not found." })).toBeVisible();
    await page.goto("/vms");
    await expect(page.getByTestId("vm-admin-create-open")).toHaveCount(0);
    await expect(page.locator("tbody")).toContainText(seed.vms[own].name);
    await expect(page.locator("tbody")).not.toContainText(seed.vms[other].name);
    expect((await fullstack.api(`/api/vms/${seed.vms[other].uuid}`)).status).toBe(404);
    expect((await fullstack.api("/api/vms?admin=true&limit=0&page=0")).status).toBe(403);
    await expect.poll(() => fullstack.diagnostics.filter(entry => entry.path === "/api/tasks/incomplete" && entry.status === 200).length).toBeGreaterThan(0);
    const polling = fullstack.diagnostics.filter(entry => entry.path === "/api/tasks/incomplete");
    expect(polling.some(entry => entry.status === 403)).toBe(false);
  });
}
