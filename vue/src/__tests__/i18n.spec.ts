import { mount } from "@vue/test-utils";
import { defineComponent, nextTick } from "vue";
import { describe, expect, it, vi } from "vitest";

import LocaleSwitcher from "@/components/LocaleSwitcher.vue";
import {
  agentScopeLabel,
  agentScopeListLabel,
  agentScopeKeys,
  agentStatusLabel,
  booleanLabel,
  formatDateTime,
  formatNumber,
  localizedDocumentTitle,
  nodeStatusLabel,
  storageRoleLabel,
  userScopeLabel,
  userScopeListLabel,
  vmStatusLabel,
} from "@/composables/i18n";
import en from "@/locales/en.json";
import ja from "@/locales/ja.json";
import i18n, {
  LOCALE_STORAGE_KEY,
  API_ERROR_CODES,
  FIELD_ERROR_CODES,
  resolveLocale,
  resolveInitialLocale,
  setLocale,
} from "@/plugins/i18n";
import { SelectStub } from "@/__tests__/support/components";

function leafKeys(value: object, prefix = ""): string[] {
  return Object.entries(value).flatMap(([key, child]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    return child !== null && typeof child === "object" && !Array.isArray(child)
      ? leafKeys(child, path)
      : [path];
  });
}

function leafEntries(value: object, prefix = ""): Array<[string, string]> {
  return Object.entries(value).flatMap(([key, child]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    return child !== null && typeof child === "object" && !Array.isArray(child)
      ? leafEntries(child, path)
      : [[path, String(child)]];
  });
}

function interpolationParams(message: string): string[] {
  return [...message.matchAll(/\{([A-Za-z][A-Za-z0-9_]*)\}/g)]
    .map(match => match[1])
    .filter((value, index, values) => values.indexOf(value) === index)
    .sort();
}

// api/agent/action_catalog.jsonの公開action scope。catalog変更時は同じ変更で更新する。
const actionCatalogScopes = [
  "flavor.create",
  "flavor.delete",
  "flavor.list",
  "image.delete",
  "image.download",
  "image.flavor.update",
  "image.list",
  "image.refresh",
  "metrics.get",
  "network.create",
  "network.delete",
  "network.get",
  "network.list",
  "network.ovs.create",
  "network.ovs.delete",
  "network.pool.create",
  "network.pool.delete",
  "network.pool.list",
  "network.pool.update",
  "network.refresh",
  "network.xml.get",
  "node.create",
  "node.delete",
  "node.facts",
  "node.get",
  "node.info",
  "node.list",
  "node.role.update",
  "node.ssh-key.write",
  "node.ssh-public-key.get",
  "project.create",
  "project.delete",
  "project.get",
  "project.list",
  "project.member-candidates",
  "project.member.add",
  "project.member.remove",
  "project.resource-grant-candidates.get",
  "project.resource-grants.update",
  "project.update",
  "storage.create",
  "storage.delete",
  "storage.get",
  "storage.list",
  "storage.metadata.update",
  "storage.pool.create",
  "storage.pool.delete",
  "storage.pool.list",
  "storage.pool.update",
  "system.version",
  "task.delete-all",
  "task.get",
  "task.incomplete",
  "task.list",
  "user.create",
  "user.delete",
  "user.list",
  "user.me",
  "user.update",
  "vm.cdrom.update",
  "vm.create",
  "vm.delete",
  "vm.get",
  "vm.list",
  "vm.network.update",
  "vm.power.update",
  "vm.project.update",
  "vm.refresh",
  "vm.xml.get",
] as const;

describe("locale resolution", () => {
  it("prefers a supported stored locale over browser preferences", () => {
    expect(resolveLocale("ja", ["en-US"])).toBe("ja");
    expect(resolveLocale("en", ["ja-JP"])).toBe("en");
  });

  it("uses the first supported browser language and otherwise falls back to English", () => {
    expect(resolveLocale("ja-JP", ["en-US"])).toBe("en");
    expect(resolveLocale("invalid", ["fr-FR", "ja-JP", "en-US"])).toBe("ja");
    expect(resolveLocale(null, ["fr-FR", "en-GB"])).toBe("en");
    expect(resolveLocale(null, ["fr-FR"])).toBe("en");
  });

  it("persists only an explicit locale selection and synchronizes html lang", () => {
    setLocale("ja");
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBeNull();
    expect(document.documentElement.lang).toBe("ja");

    setLocale("en", true);
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("en");
    expect(document.documentElement.lang).toBe("en");
  });

  it("continues startup when Storage.getItem throws", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("blocked");
    });
    vi.spyOn(window.navigator, "languages", "get").mockReturnValue(["ja-JP"]);

    expect(resolveInitialLocale()).toBe("ja");
  });

  it("continues an explicit selection when Storage.setItem throws", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("blocked");
    });

    expect(() => setLocale("ja", true)).not.toThrow();
    expect(i18n.global.locale.value).toBe("ja");
    expect(document.documentElement.lang).toBe("ja");
  });

  it("continues startup and explicit selection when the localStorage getter throws", () => {
    const descriptor = Object.getOwnPropertyDescriptor(window, "localStorage");
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      get() {
        throw new DOMException("blocked");
      },
    });

    try {
      vi.spyOn(window.navigator, "languages", "get").mockReturnValue(["ja-JP"]);
      expect(resolveInitialLocale()).toBe("ja");
      expect(() => setLocale("en", true)).not.toThrow();
      expect(document.documentElement.lang).toBe("en");
    } finally {
      if (descriptor) Object.defineProperty(window, "localStorage", descriptor);
    }
  });
});

describe("localized presentation", () => {
  it("switches messages, document titles, dates, numbers, and Vuetify messages", () => {
    const timestamp = "2025-01-02T03:04:05Z";

    setLocale("en");
    expect(localizedDocumentTitle("Home")).toBe("Virty - Home");
    expect(formatNumber(1234.5)).toBe(
      new Intl.NumberFormat("en", { maximumFractionDigits: 1 }).format(1234.5),
    );
    expect(formatDateTime(timestamp)).toBe(
      new Intl.DateTimeFormat("en", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      }).format(new Date(timestamp)),
    );

    setLocale("ja");
    expect(localizedDocumentTitle("ホーム")).toBe("Virty - ホーム");
    expect(formatNumber(1234.5)).toBe(
      new Intl.NumberFormat("ja", { maximumFractionDigits: 1 }).format(1234.5),
    );
    expect(i18n.global.t("$vuetify.dataFooter.itemsPerPageText")).not.toBe(
      "$vuetify.dataFooter.itemsPerPageText",
    );
  });

  it("keeps the hand-authored English and Japanese catalogs structurally identical", () => {
    expect(leafKeys(ja).sort()).toEqual(leafKeys(en).sort());
  });

  it("has no empty leaves and keeps interpolation parameters identical", () => {
    const english = new Map(leafEntries(en));
    const japanese = new Map(leafEntries(ja));

    for (const [key, message] of english) {
      expect(message.trim(), key).not.toBe("");
      expect(japanese.get(key)?.trim(), key).not.toBe("");
      expect(interpolationParams(japanese.get(key) ?? ""), key).toEqual(
        interpolationParams(message),
      );
    }
  });

  it("contains a non-empty translation for every generated API error code", () => {
    expect(API_ERROR_CODES).toHaveLength(237);
    for (const code of API_ERROR_CODES) {
      expect(en.apiErrors[code].trim(), code).not.toBe("");
      expect(ja.apiErrors[code].trim(), code).not.toBe("");
    }
  });

  it("contains a non-empty translation for every generated field error code", () => {
    expect(FIELD_ERROR_CODES).toHaveLength(14);
    for (const code of FIELD_ERROR_CODES) {
      expect(en.fieldErrors[code].trim(), code).not.toBe("");
      expect(ja.fieldErrors[code].trim(), code).not.toBe("");
    }
  });

  it("maps every Agent action catalog scope to non-empty English and Japanese labels", () => {
    expect(actionCatalogScopes).toHaveLength(69);
    expect(new Set(actionCatalogScopes).size).toBe(actionCatalogScopes.length);

    for (const scope of actionCatalogScopes) {
      expect(agentScopeKeys[scope], scope).toBeDefined();
    }

    for (const locale of ["en", "ja"] as const) {
      setLocale(locale);
      for (const scope of actionCatalogScopes) {
        const label = agentScopeLabel(scope);
        expect(label.trim(), `${locale}:${scope}`).not.toBe("");
        expect(label, `${locale}:${scope}`).not.toBe(scope);
      }
    }
  });

  it("chooses singular and plural variants from count", () => {
    setLocale("en");
    expect(i18n.global.t("appBar.taskCount", { count: 1 }, 1)).toBe("1 active task");
    expect(i18n.global.t("appBar.taskCount", { count: 2 }, 2)).toBe("2 active tasks");
    expect(i18n.global.t("dialogs.imageDelete.confirmation", { count: 1 }, 1)).toBe(
      "Yes, delete 1 image",
    );
    expect(i18n.global.t("dialogs.imageDelete.confirmation", { count: 2 }, 2)).toBe(
      "Yes, delete 2 images",
    );
    expect(i18n.global.t("dashboard.kpis.cpuCores", { count: 1 }, 1)).toBe("1 CPU core");
    expect(i18n.global.t("dashboard.kpis.cpuCores", { count: 4 }, 4)).toBe("4 CPU cores");
    expect(i18n.global.t("dashboard.kpis.portGroups", { count: 1 }, 1)).toBe("1 port group");
    expect(i18n.global.t("dashboard.kpis.portGroups", { count: 3 }, 3)).toBe("3 port groups");
    expect(i18n.global.t("pages.vms.coreCount", { count: 1 }, 1)).toBe("1 core");
    expect(i18n.global.t("pages.vms.coreCount", { count: 2 }, 2)).toBe("2 cores");

    setLocale("ja");
    expect(i18n.global.t("appBar.taskCount", { count: 1 }, 1)).toBe("実行中のタスク: 1件");
    expect(i18n.global.t("appBar.taskCount", { count: 2 }, 2)).toBe("実行中のタスク: 2件");
  });

  it("translates known domain values and preserves unknown API values", () => {
    setLocale("en");
    expect(vmStatusLabel(1)).toBe("Running");
    expect(vmStatusLabel(20)).toBe("Lost node");
    expect(nodeStatusLabel(10)).toBe("Ready");
    expect(agentStatusLabel("active")).toBe("Active");
    expect(booleanLabel(true)).toBe("Yes");
    expect(booleanLabel(false)).toBe("No");
    expect(booleanLabel(null)).toBe("Unknown");
    expect(booleanLabel("future_boolean")).toBe("future_boolean");
    expect(agentScopeLabel("vm.list")).toBe("List VMs (vm.list)");
    expect(agentScopeListLabel(["node.*", "future.scope"])).toBe(
      "All node actions (node.*), future.scope",
    );
    expect(userScopeLabel("identity.manage")).toBe(
      "Manage users and permissions (identity.manage)",
    );
    expect(userScopeListLabel(["vm.read", "future.user-scope"])).toBe(
      "Read VMs (vm.read), future.user-scope",
    );
    expect(storageRoleLabel("init-iso")).toBe("Cloud-init");

    expect(vmStatusLabel(999)).toBe("999");
    expect(nodeStatusLabel(2)).toBe("2");
    expect(agentStatusLabel("future_status")).toBe("future_status");
    expect(agentScopeLabel("future.scope")).toBe("future.scope");
    expect(userScopeLabel("future.user-scope")).toBe("future.user-scope");
    expect(storageRoleLabel("future-role")).toBe("future-role");

    setLocale("ja");
    expect(vmStatusLabel(1)).toBe("実行中");
    expect(nodeStatusLabel(10)).toBe("準備完了");
    expect(agentStatusLabel("active")).toBe("有効");
    expect(booleanLabel(true)).toBe("はい");
    expect(agentScopeLabel("vm.list")).toBe("VM一覧の参照 (vm.list)");
    expect(userScopeLabel("identity.manage")).toBe(
      "ユーザーと権限の管理 (identity.manage)",
    );
    expect(storageRoleLabel("img")).toBe("VMイメージ");
  });

  it("updates status, scope, boolean, and storage labels in a mounted component", async () => {
    const DomainLabelHarness = defineComponent({
      setup: () => ({
        agentScopeLabel,
        agentStatusLabel,
        booleanLabel,
        nodeStatusLabel,
        storageRoleLabel,
        userScopeLabel,
        vmStatusLabel,
      }),
      template: `
        <div>
          <span data-testid="vm-status">{{ vmStatusLabel(1) }}</span>
          <span data-testid="node-status">{{ nodeStatusLabel(10) }}</span>
          <span data-testid="agent-status">{{ agentStatusLabel('active') }}</span>
          <span data-testid="agent-scope">{{ agentScopeLabel('vm.list') }}</span>
          <span data-testid="user-scope">{{ userScopeLabel('vm.read') }}</span>
          <span data-testid="boolean">{{ booleanLabel(false) }}</span>
          <span data-testid="storage-role">{{ storageRoleLabel('img') }}</span>
          <span data-testid="unknown">{{ vmStatusLabel(999) }}</span>
        </div>
      `,
    });
    const wrapper = mount(DomainLabelHarness);

    expect(wrapper.get('[data-testid="vm-status"]').text()).toBe("Running");
    expect(wrapper.get('[data-testid="node-status"]').text()).toBe("Ready");
    expect(wrapper.get('[data-testid="agent-status"]').text()).toBe("Active");
    expect(wrapper.get('[data-testid="agent-scope"]').text()).toBe("List VMs (vm.list)");
    expect(wrapper.get('[data-testid="user-scope"]').text()).toBe("Read VMs (vm.read)");
    expect(wrapper.get('[data-testid="boolean"]').text()).toBe("No");
    expect(wrapper.get('[data-testid="storage-role"]').text()).toBe("VM image");
    expect(wrapper.get('[data-testid="unknown"]').text()).toBe("999");

    setLocale("ja");
    await nextTick();

    expect(wrapper.get('[data-testid="vm-status"]').text()).toBe("実行中");
    expect(wrapper.get('[data-testid="node-status"]').text()).toBe("準備完了");
    expect(wrapper.get('[data-testid="agent-status"]').text()).toBe("有効");
    expect(wrapper.get('[data-testid="agent-scope"]').text()).toBe("VM一覧の参照 (vm.list)");
    expect(wrapper.get('[data-testid="user-scope"]').text()).toBe("VMの参照 (vm.read)");
    expect(wrapper.get('[data-testid="boolean"]').text()).toBe("いいえ");
    expect(wrapper.get('[data-testid="storage-role"]').text()).toBe("VMイメージ");
    expect(wrapper.get('[data-testid="unknown"]').text()).toBe("999");
  });

  it("stores locale changes made through the switcher", async () => {
    const wrapper = mount(LocaleSwitcher, {
      global: {
        stubs: {
          VBtn: true,
          VList: true,
          VListItem: true,
          VMenu: true,
          VSelect: SelectStub,
        },
      },
    });

    wrapper.findComponent(SelectStub).vm.$emit("update:modelValue", "ja");
    await wrapper.vm.$nextTick();

    expect(i18n.global.locale.value).toBe("ja");
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe("ja");
    expect(document.documentElement.lang).toBe("ja");
  });
});
