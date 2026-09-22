import { test, expect, type Seed } from "./fixtures";

const resources = {
  vms: (seed: Seed) => seed.vms.alpha.name,
  nodes: (seed: Seed) => seed.resources.nodeName,
  storages: (seed: Seed) => seed.resources.storageName,
  images: (seed: Seed) => seed.resources.imageName,
  networks: (seed: Seed) => seed.resources.networkName,
};

for (const [resource, resourceName] of Object.entries(resources)) {
  test(`${resource}: 実DBの一覧をProject選択・再読込・解除で絞り込む`, async ({ fullstack, page, seed }) => {
    await fullstack.login(seed.users.admin, `/${resource}`, { adminMode: true });
    await expect(page.locator("tbody")).toContainText(resourceName(seed));

    await fullstack.selectProject(seed.projects.alpha);
    await expect(page.locator("tbody")).toContainText(resourceName(seed));
    if (resource === "vms") await expect(page.locator("tbody")).not.toContainText(seed.vms.beta.name);
    await page.reload();
    await expect(page.locator("header")).toContainText(seed.projects.alpha.name);
    await expect(page.locator("tbody")).toContainText(resourceName(seed));

    const filtered = page.waitForResponse(response => {
      const url = new URL(response.url());
      return url.pathname === `/api/${resource}` && url.searchParams.get("projectId") === seed.projects.beta.id;
    });
    await fullstack.selectProject(seed.projects.beta);
    const response = await filtered;
    expect(response.status()).toBe(200);
    const result = await response.json() as { count: number; data: { name: string }[] };
    expect(result.count).toBe(resource === "vms" ? 1 : 0);
    await expect(page.locator("tbody")).not.toContainText(resourceName(seed));
    if (resource === "vms") await expect(page.locator("tbody")).toContainText(seed.vms.beta.name);

    const cleared = page.waitForResponse(response => {
      const url = new URL(response.url());
      return url.pathname === `/api/${resource}` && !url.searchParams.has("projectId");
    });
    await page.locator("header").getByRole("button", { name: "Clear Project", exact: true }).click();
    expect((await cleared).status()).toBe(200);
    await expect(page).toHaveURL(new RegExp(`/${resource}$`));
    await expect(page.locator("tbody")).toContainText(resourceName(seed));
  });
}
