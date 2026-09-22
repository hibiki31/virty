import { test, expect, type Fullstack, type Seed, type Task } from "./fixtures";
import type { components } from "../src/api/openapi";

async function createVm(fullstack: Fullstack, seed: Seed, name: string, copy: boolean): Promise<Task[]> {
  const page = fullstack.page;
  await page.getByTestId("vm-create-open").click();
  const dialog = page.getByTestId("vm-create-dialog");
  await expect(dialog).toBeVisible();
  await dialog.getByTestId("vm-name").locator("input").fill(name);
  await dialog.getByTestId("vm-project").click();
  await page.getByRole("option", { name: `${seed.projects.alpha.name} (#${seed.projects.alpha.id})`, exact: true }).click();
  await dialog.getByTestId("vm-node").click();
  await page.getByRole("option", { name: seed.resources.nodeName, exact: true }).click();
  await dialog.getByTestId("vm-destination-pool").click();
  await page.getByRole("option", { name: seed.resources.storageName, exact: true }).click();
  if (copy) {
    await dialog.getByTestId("vm-disk-mode").click();
    await page.getByRole("option", { name: "Copy", exact: true }).click();
    await dialog.getByTestId("vm-source-pool").click();
    await page.getByRole("option", { name: seed.resources.storageName, exact: true }).click();
    await dialog.getByTestId("vm-source-image").click();
    await page.getByRole("option", { name: seed.resources.imageName, exact: true }).click();
  }
  await dialog.getByTestId("vm-network").click();
  await page.getByRole("option", { name: seed.resources.networkName, exact: true }).click();
  const submitted = page.waitForResponse(response => new URL(response.url()).pathname === "/api/tasks/vms" && response.request().method() === "POST");
  await dialog.getByTestId("vm-create-submit").click();
  const tasks = await fullstack.tasks(await submitted);
  await expect(dialog).toBeHidden();
  return tasks;
}

test("memberがtemplateからVMを作成し、worker完了とDBの所有Project・資源を画面で確認する", async ({ fullstack, page, seed }) => {
  await fullstack.login(seed.users.member);
  const tasks = await test.step("templateと許可されたnode・storage・networkを選んで作成する", () => createVm(fullstack, seed, "e2e-created-vm", true));
  for (const task of tasks) await fullstack.waitTask(task);
  await page.goto("/tasks");
  for (const task of tasks) {
    const row = page.getByRole("row").filter({ hasText: task.uuid });
    await expect(row).toContainText("Finished");
  }
  await page.goto("/vms");
  const row = page.getByRole("row").filter({ hasText: "e2e-created-vm" });
  await expect(row).toContainText(seed.resources.nodeName);
  await expect(row).toContainText(seed.projects.alpha.name);
  const vms = await fullstack.api<components["schemas"]["DomainPage"]>("/api/vms?nameLike=e2e-created-vm&limit=0&page=0");
  expect(vms.status).toBe(200);
  expect(vms.data.count).toBe(1);
  const vm = vms.data.data[0]!;
  expect(vm.ownerProject?.id).toBe(seed.projects.alpha.id);
  expect(vm.nodeName).toBe(seed.resources.nodeName);
  expect(vm.core).toBe(2);
  expect(vm.memory).toBe(8192);
  const detail = await fullstack.api<components["schemas"]["DomainDetail"]>(`/api/vms/${vm.uuid}`);
  expect(detail.status).toBe(200);
  expect(detail.data.drives?.filter(drive => drive.device === "disk").map(drive => drive.capacityGb)).toEqual([32]);
  expect(detail.data.interfaces?.map(network => network.networkUuid)).toEqual([seed.resources.networkUuid]);
  const project = await fullstack.api<components["schemas"]["ProjectDetail"]>(`/api/projects/${seed.projects.alpha.id}`);
  expect(project.status).toBe(200);
  expect(project.data.usedCore).toBe(3);
  expect(project.data.usedMemoryG).toBe(9);
  expect(project.data.usedStorageG).toBe(32);
  await row.getByRole("link", { name: vm.uuid, exact: true }).click();
  await expect(page).toHaveTitle("Virty - e2e-created-vm");
  await page.goto(`/projects/${seed.projects.alpha.id}`);
  await expect(page.locator("main")).toContainText("32 GiB used");
});

test("workerのdomain_define失敗をtask画面で確認し、新規VMがDBへ登録されない", async ({ fullstack, page, seed }) => {
  await fullstack.login(seed.users.member);
  await fullstack.control("failure", { operation: "domain_define" });
  const tasks = await test.step("失敗を注入したbackendへVM作成を送る", () => createVm(fullstack, seed, "e2e-failed-vm", false));
  const failed = tasks.find(task => task.resource === "vm" && task.method === "post");
  expect(failed).toBeDefined();
  await fullstack.waitTask(failed!, "error");
  for (const task of tasks.filter(task => task.uuid !== failed!.uuid)) {
    const dependent = await fullstack.waitTask(task, "error");
    expect(dependent.errorCode).toBe("DEPENDENCY_FAILED");
  }
  await page.goto("/tasks");
  const row = page.getByRole("row").filter({ hasText: failed!.uuid });
  await expect(row).toContainText("Error");
  await row.getByTestId("task-view-details").click();
  await expect(page.getByRole("dialog")).toContainText("E2Eで指定したdomain_defineの失敗");
  const vms = await fullstack.api<components["schemas"]["DomainPage"]>("/api/vms?nameLike=e2e-failed-vm&limit=0&page=0");
  expect(vms.status).toBe(200);
  expect(vms.data.count).toBe(0);
});
