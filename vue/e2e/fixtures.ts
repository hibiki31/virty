import { test as base, type Page, type Route } from "@playwright/test";

const encoded = (value: object): string =>
  Buffer.from(JSON.stringify(value)).toString("base64url");

export const accessToken = `${encoded({ alg: "none", typ: "JWT" })}.${encoded({
  exp: 4_102_444_800,
  projects: [],
  scopes: ["user", "admin"],
  sub: "operator",
})}.signature`;

const dashboard = {
  generatedAt: "2026-08-22T12:34:56Z",
  visibility: "all",
  nodes: { count: 1, core: 8, memoryGib: 16, roles: [{ name: "libvirt", count: 1 }] },
  vms: {
    count: 1,
    core: 2,
    memoryGib: 8,
    statuses: {
      running: 1,
      stopped: 0,
      maintenance: 0,
      deleted: 0,
      lostNode: 0,
      unknown: 0,
    },
  },
  storages: {
    count: 1,
    capacityGib: 100,
    usedGib: 20,
    availableGib: 80,
    highUsageCount: 0,
    highestUsage: [],
  },
  networks: { count: 1, portGroupCount: 0, types: [{ name: "bridge", count: 1 }] },
  images: { count: 1 },
  tasks: { incompleteCount: 0, failedLast24Hours: 0, recent: [] },
};

const node = {
  core: 8,
  cpuGen: "test-cpu",
  description: "E2E node",
  domain: "192.0.2.10",
  libvirtVersion: "10.0",
  memory: 16_384,
  name: "node-e2e",
  osLike: "linux",
  osName: "Test Linux",
  osVersion: "1",
  port: 22,
  qemuVersion: "9.0",
  roles: [],
  status: 10,
  userName: "operator",
};

const vm = {
  core: 2,
  description: "E2E VM",
  drives: [],
  interfaces: [],
  memory: 8_192,
  name: "vm-e2e",
  node,
  nodeName: node.name,
  ownerProjectId: null,
  ownerUserId: "operator",
  status: 1,
  uuid: "vm-e2e-uuid",
  vncPort: -1,
};

type ApiState = {
  failNextVmCreate: () => void;
  vmCreateBodies: unknown[];
};

type Fixtures = {
  api: ApiState;
  authenticatedPage: Page;
};

async function fulfillJson(route: Route, json: unknown, status = 200): Promise<void> {
  await route.fulfill({
    body: JSON.stringify(json),
    contentType: "application/json",
    status,
  });
}

export const test = base.extend<Fixtures>({
  api: async ({ page }, use) => {
    const state = {
      failVmCreate: false,
      vmCreateBodies: [] as unknown[],
    };

    await page.route("**/api/**", async (route) => {
      const request = route.request();
      const path = new URL(request.url()).pathname;

      if (path === "/api/auth" && request.method() === "POST") {
        await fulfillJson(route, { access_token: accessToken, token_type: "bearer" });
        return;
      }
      if (path === "/api/auth/validate") {
        await fulfillJson(route, { id: "operator", role: [], scopes: ["user", "admin"] });
        return;
      }
      if (path === "/api/version") {
        await fulfillJson(route, { initialized: true, version: "5.1.2" });
        return;
      }
      if (path === "/api/dashboard") {
        await fulfillJson(route, dashboard);
        return;
      }
      if (path === "/api/tasks/incomplete") {
        await fulfillJson(route, { count: 0, hash: "empty", uuids: [] });
        return;
      }
      if (path === "/api/vms/vm-e2e-uuid/xml") {
        await fulfillJson(route, { xml: "<domain />" });
        return;
      }
      if (path === "/api/vms/vm-e2e-uuid") {
        await fulfillJson(route, vm);
        return;
      }
      if (path === "/api/vms" && request.method() === "GET") {
        await fulfillJson(route, { count: 1, data: [vm] });
        return;
      }
      if (path === "/api/nodes") {
        await fulfillJson(route, { count: 1, data: [node] });
        return;
      }
      if (path === "/api/networks") {
        await fulfillJson(route, {
          count: 1,
          data: [{ name: "net-e2e", nodeName: node.name, portgroups: [], type: "bridge", uuid: "net-e2e" }],
        });
        return;
      }
      if (path === "/api/storages") {
        await fulfillJson(route, {
          count: 1,
          data: [{ name: "pool-e2e", nodeName: node.name, uuid: "pool-e2e" }],
        });
        return;
      }
      if (path === "/api/images") {
        await fulfillJson(route, { count: 0, data: [] });
        return;
      }
      if (path === "/api/users") {
        await fulfillJson(route, { count: 0, data: [] });
        return;
      }
      if (path === "/api/tasks/vms" && request.method() === "POST") {
        state.vmCreateBodies.push(request.postDataJSON());
        if (state.failVmCreate) {
          state.failVmCreate = false;
          await fulfillJson(
            route,
            { detail: [{ loc: ["body", "name"], msg: "VM already exists", type: "conflict" }] },
            422,
          );
        } else {
          await fulfillJson(route, [{ uuid: "vm-create-task" }]);
        }
        return;
      }

      await fulfillJson(route, {});
    });

    await use({
      failNextVmCreate: () => {
        state.failVmCreate = true;
      },
      vmCreateBodies: state.vmCreateBodies,
    });
  },

  authenticatedPage: async ({ api: _api, context, page }, use) => {
    const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:4173";
    await context.addCookies([{ name: "accessToken", url: baseURL, value: accessToken }]);
    await use(page);
  },
});

export { expect } from "@playwright/test";
