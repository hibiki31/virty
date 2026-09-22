import { test as base, type Page, type Route } from "@playwright/test";
import { playwrightBaseURL } from "./base-url";

const encoded = (value: object): string =>
  Buffer.from(JSON.stringify(value)).toString("base64url");

export const accessToken = `${encoded({ alg: "none", typ: "JWT" })}.${encoded({
  exp: 4_102_444_800,
  projects: ["a1b2c3"],
  scopes: ["user", "admin", "project.read", "project.manage"],
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

export const rawVmXml =
  '<domain data-opaque="XML-UNCHANGED-42"><name>vm-e2e</name></domain>';

export const rawNodeInfo = {
  ansible: "ANSIBLE-OUTPUT-UNCHANGED-42",
  ssh: "SSH-OUTPUT-UNCHANGED-42",
} as const;

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

const nodeInfo = {
  dfH: "Filesystem output",
  free: "Memory output",
  ipAddress: "IP address output",
  ipNeigh: "IP neighbor output",
  ipRoute: "IP route output",
  iptables: "Netfilter output",
  iptablesNat: "NAT output",
  lsblk: "Block device output",
  netplanGet: rawNodeInfo.ansible,
  top: rawNodeInfo.ssh,
  uptime: "Uptime output",
};

export const vm = {
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

export const rawTask = {
  log: "virsh output: vm-e2e-uuid",
  message: "libvirt: DOMAIN_RUNNING",
  object: "vm-e2e-uuid",
  postTime: "2026-08-22T12:34:56Z",
  request: { opaqueToken: "REQ-UNCHANGED-42" },
  resource: "vm",
  runTime: 1.25,
  status: "finish",
  method: "post",
  userId: "operator",
  uuid: "task-raw-7f3a",
};

const project = {
  id: "a1b2c3",
  name: "Project E2E",
  memberCount: 1,
  usedCore: 2,
  usedMemoryG: 8,
  usedStorageG: 0,
};

const projectDetail = {
  ...project,
  limits: { core: 16, memoryG: 64, storageCapacityG: 500, enforced: false },
  members: [{ username: "operator" }],
  resourceGrants: {
    storagePoolIds: [1],
    networkPoolIds: [1],
    flavorIds: [],
  },
  storagePools: [{ id: 1, name: "storage-e2e" }],
  networkPools: [{ id: 1, name: "network-e2e" }],
  flavors: [],
};

type ApiState = {
  failNextVmCreate: () => void;
  setInitialized: (initialized: boolean) => void;
  projectCreateBodies: unknown[];
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

async function handleAgentRequest(route: Route, path: string): Promise<boolean> {
  if (path === "/api/agent/v1/pairing-requests") {
    await fulfillJson(route, []);
    return true;
  }
  if (path === "/api/agent/v1/lease-requests") {
    await fulfillJson(route, []);
    return true;
  }
  if (path === "/api/agent/v1/devices") {
    await fulfillJson(route, []);
    return true;
  }
  if (path === "/api/agent/v1/capability-leases") {
    await fulfillJson(route, []);
    return true;
  }
  if (path === "/api/agent/v1/control") {
    await fulfillJson(route, {
      allowDeleteWithoutRecovery: false,
      allowNetworkChangeWithoutOob: false,
      enabledRiskLevels: ["R1"],
      mutationsEnabled: false,
      reason: "E2E baseline",
      shadowMode: true,
      updatedAt: "2026-08-22T12:34:56Z",
      updatedBy: "operator",
    });
    return true;
  }
  if (path === "/api/agent/v1/operation-reconciliations") {
    await fulfillJson(route, []);
    return true;
  }
  return false;
}

export const test = base.extend<Fixtures>({
  api: async ({ page }, use) => {
    const state = {
      failVmCreate: false,
      initialized: true,
      projectCreateBodies: [] as unknown[],
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
        await fulfillJson(route, { initialized: state.initialized, version: "5.1.2" });
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
      if (path === "/api/tasks" && request.method() === "GET") {
        await fulfillJson(route, { count: 1, data: [rawTask] });
        return;
      }
      if (await handleAgentRequest(route, path)) {
        return;
      }
      if (path === "/api/vms/vm-e2e-uuid/xml") {
        await fulfillJson(route, { xml: rawVmXml });
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
      if (path === "/api/projects/a1b2c3/member-candidates") {
        await fulfillJson(route, { count: 0, data: [] });
        return;
      }
      if (path === "/api/projects/a1b2c3") {
        await fulfillJson(route, projectDetail);
        return;
      }
      if (path === "/api/projects" && request.method() === "GET") {
        await fulfillJson(route, { count: 1, data: [project] });
        return;
      }
      if (path === "/api/tasks/projects" && request.method() === "POST") {
        state.projectCreateBodies.push(request.postDataJSON());
        await fulfillJson(route, [{ uuid: "project-create-task" }]);
        return;
      }
      if (path === "/api/nodes") {
        await fulfillJson(route, { count: 1, data: [node] });
        return;
      }
      if (path === "/api/nodes/node-e2e/info") {
        await fulfillJson(route, nodeInfo);
        return;
      }
      if (path === "/api/nodes/node-e2e") {
        await fulfillJson(route, node);
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
        await fulfillJson(route, {
          count: 1,
          data: [{ username: "operator", scopes: [], projects: [{ id: project.id, name: project.name }], publickeys: [] }],
        });
        return;
      }
      if (["/api/tasks/vms", "/api/tasks/vms/admin"].includes(path) && request.method() === "POST") {
        state.vmCreateBodies.push(request.postDataJSON());
        if (state.failVmCreate) {
          state.failVmCreate = false;
          await fulfillJson(
            route,
            {
              detail: {
                code: "conflict",
                message: "The VM already exists.",
              },
            },
            409,
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
      setInitialized: initialized => {
        state.initialized = initialized;
      },
      projectCreateBodies: state.projectCreateBodies,
      vmCreateBodies: state.vmCreateBodies,
    });
  },

  authenticatedPage: async ({ api: _api, context, page }, use) => {
    await context.addCookies([
      { name: "accessToken", url: playwrightBaseURL, value: accessToken },
    ]);
    await use(page);
  },
});

export { expect } from "@playwright/test";
