import { watchEffect, toValue, type MaybeRefOrGetter } from "vue";
import { useI18n } from "vue-i18n";

import i18n, { type MessageKey, type MessageSchema } from "@/plugins/i18n";

export type TranslationScalar = string | number | boolean | null;
export type TranslationParam = TranslationScalar | TranslationRef;
export type TranslationRef = {
  kind: "translation";
  key: MessageKey;
  params?: Record<string, TranslationParam>;
};

export class TranslationError extends Error {
  readonly content: TranslationRef;

  constructor(content: TranslationRef) {
    super(content.key);
    this.name = "TranslationError";
    this.content = content;
  }
}

export function translationRef(
  key: MessageKey,
  params?: Record<string, TranslationParam>,
): TranslationRef {
  return params ? { kind: "translation", key, params } : { kind: "translation", key };
}

export function resolveTranslation(value: TranslationRef): string {
  const params = Object.fromEntries(
    Object.entries(value.params ?? {}).map(([key, param]) => [
      key,
      typeof param === "object" && param !== null && param.kind === "translation"
        ? resolveTranslation(param)
        : param,
    ]),
  );
  return i18n.global.t(value.key, params);
}

export function translateDomainValue(
  namespace: keyof MessageSchema["domain"],
  value: string | number | boolean | null | undefined,
): string {
  if (value === null || value === undefined || value === "") {
    return i18n.global.t("common.values.unknown");
  }

  const rawValue = String(value);
  const key = `domain.${namespace}.${rawValue}` as MessageKey;
  return i18n.global.te(key) ? i18n.global.t(key) : rawValue;
}

export const agentScopeKeys = {
  "*": "domain.agentScope.all",
  "identity.admin": "domain.agentScope.identity.admin",
  "system.*": "domain.agentScope.system.all",
  "system.version": "domain.agentScope.system.version",
  "metrics.*": "domain.agentScope.metrics.all",
  "metrics.get": "domain.agentScope.metrics.get",
  "task.*": "domain.agentScope.task.all",
  "task.list": "domain.agentScope.task.list",
  "task.incomplete": "domain.agentScope.task.incomplete",
  "task.get": "domain.agentScope.task.get",
  "task.delete-all": "domain.agentScope.task.deleteAll",
  "node.*": "domain.agentScope.node.all",
  "node.list": "domain.agentScope.node.list",
  "node.ssh-key.write": "domain.agentScope.node.sshKey.write",
  "node.ssh-public-key.get": "domain.agentScope.node.sshPublicKey.get",
  "node.get": "domain.agentScope.node.get",
  "node.facts": "domain.agentScope.node.facts",
  "node.info": "domain.agentScope.node.info",
  "node.create": "domain.agentScope.node.create",
  "node.delete": "domain.agentScope.node.delete",
  "node.role.update": "domain.agentScope.node.role.update",
  "vm.*": "domain.agentScope.vm.all",
  "vm.list": "domain.agentScope.vm.list",
  "vm.get": "domain.agentScope.vm.get",
  "vm.xml.get": "domain.agentScope.vm.xml.get",
  "vm.refresh": "domain.agentScope.vm.refresh",
  "vm.create": "domain.agentScope.vm.create",
  "vm.delete": "domain.agentScope.vm.delete",
  "vm.power.update": "domain.agentScope.vm.power.update",
  "vm.cdrom.update": "domain.agentScope.vm.cdrom.update",
  "vm.project.update": "domain.agentScope.vm.project.update",
  "vm.network.update": "domain.agentScope.vm.network.update",
  "storage.*": "domain.agentScope.storage.all",
  "storage.list": "domain.agentScope.storage.list",
  "storage.metadata.update": "domain.agentScope.storage.metadata.update",
  "storage.pool.list": "domain.agentScope.storage.pool.list",
  "storage.pool.create": "domain.agentScope.storage.pool.create",
  "storage.pool.update": "domain.agentScope.storage.pool.update",
  "storage.pool.delete": "domain.agentScope.storage.pool.delete",
  "storage.get": "domain.agentScope.storage.get",
  "storage.create": "domain.agentScope.storage.create",
  "storage.delete": "domain.agentScope.storage.delete",
  "image.*": "domain.agentScope.image.all",
  "image.list": "domain.agentScope.image.list",
  "image.flavor.update": "domain.agentScope.image.flavor.update",
  "image.refresh": "domain.agentScope.image.refresh",
  "image.download": "domain.agentScope.image.download",
  "image.delete": "domain.agentScope.image.delete",
  "network.*": "domain.agentScope.network.all",
  "network.list": "domain.agentScope.network.list",
  "network.pool.list": "domain.agentScope.network.pool.list",
  "network.pool.create": "domain.agentScope.network.pool.create",
  "network.pool.update": "domain.agentScope.network.pool.update",
  "network.pool.delete": "domain.agentScope.network.pool.delete",
  "network.get": "domain.agentScope.network.get",
  "network.xml.get": "domain.agentScope.network.xml.get",
  "network.refresh": "domain.agentScope.network.refresh",
  "network.create": "domain.agentScope.network.create",
  "network.ovs.create": "domain.agentScope.network.ovs.create",
  "network.provider.create": "domain.agentScope.network.provider.create",
  "network.ovs.delete": "domain.agentScope.network.ovs.delete",
  "network.delete": "domain.agentScope.network.delete",
  "project.*": "domain.agentScope.project.all",
  "project.list": "domain.agentScope.project.list",
  "project.get": "domain.agentScope.project.get",
  "project.member-candidates": "domain.agentScope.project.memberCandidates",
  "project.member.add": "domain.agentScope.project.member.add",
  "project.member.remove": "domain.agentScope.project.member.remove",
  "project.resource-grant-candidates.get": "domain.agentScope.project.resourceGrantCandidates.get",
  "project.resource-grants.update": "domain.agentScope.project.resourceGrants.update",
  "project.create": "domain.agentScope.project.create",
  "project.delete": "domain.agentScope.project.delete",
  "project.update": "domain.agentScope.project.update",
  "user.*": "domain.agentScope.user.all",
  "user.me": "domain.agentScope.user.me",
  "user.list": "domain.agentScope.user.list",
  "user.create": "domain.agentScope.user.create",
  "user.update": "domain.agentScope.user.update",
  "user.delete": "domain.agentScope.user.delete",
  "flavor.*": "domain.agentScope.flavor.all",
  "flavor.list": "domain.agentScope.flavor.list",
  "flavor.create": "domain.agentScope.flavor.create",
  "flavor.delete": "domain.agentScope.flavor.delete",
} as const satisfies Record<string, MessageKey>;

export function agentScopeLabel(scope: string): string {
  const key = agentScopeKeys[scope as keyof typeof agentScopeKeys];
  return key ? i18n.global.t(key) : scope;
}

export function agentScopeListLabel(scopes: readonly string[]): string {
  return scopes.map(agentScopeLabel).join(", ");
}

const userScopeKeys = {
  admin: "domain.userScope.admin",
  user: "domain.userScope.user",
  "inventory.read": "domain.userScope.inventory.read",
  "vm.read": "domain.userScope.vm.read",
  "vm.create": "domain.userScope.vm.create",
  "vm.power": "domain.userScope.vm.power",
  "vm.attach": "domain.userScope.vm.attach",
  "vm.delete": "domain.userScope.vm.delete",
  "vm.project": "domain.userScope.vm.project",
  "node.read": "domain.userScope.node.read",
  "node.manage": "domain.userScope.node.manage",
  "node.credentials": "domain.userScope.node.credentials",
  "storage.read": "domain.userScope.storage.read",
  "storage.manage": "domain.userScope.storage.manage",
  "image.read": "domain.userScope.image.read",
  "image.manage": "domain.userScope.image.manage",
  "network.read": "domain.userScope.network.read",
  "network.manage": "domain.userScope.network.manage",
  "project.read": "domain.userScope.project.read",
  "project.manage": "domain.userScope.project.manage",
  "flavor.read": "domain.userScope.flavor.read",
  "flavor.manage": "domain.userScope.flavor.manage",
  "task.read.self": "domain.userScope.task.read.self",
  "task.read.any": "domain.userScope.task.read.any",
  "task.manage": "domain.userScope.task.manage",
  "identity.manage": "domain.userScope.identity.manage",
  "metrics.read": "domain.userScope.metrics.read",
} as const satisfies Record<string, MessageKey>;

export function userScopeLabel(scope: string): string {
  const key = userScopeKeys[scope as keyof typeof userScopeKeys];
  return key ? i18n.global.t(key) : scope;
}

export function userScopeListLabel(scopes: readonly string[]): string {
  return scopes.map(userScopeLabel).join(", ");
}

const storageRoleKeys = {
  img: "domain.storageRole.img",
  iso: "domain.storageRole.iso",
  template: "domain.storageRole.template",
  "init-iso": "domain.storageRole.initIso",
} as const satisfies Record<string, MessageKey>;

export function storageRoleLabel(role: string | null | undefined): string {
  if (role === null || role === undefined || role === "") {
    return i18n.global.t("common.values.unknown");
  }
  const key = storageRoleKeys[role as keyof typeof storageRoleKeys];
  return key ? i18n.global.t(key) : role;
}

export function agentStatusLabel(status: string | null | undefined): string {
  return translateDomainValue("agentStatus", status);
}

export function booleanLabel(
  value: boolean | string | number | null | undefined,
): string {
  return translateDomainValue("boolean", value);
}

export function vmStatusLabel(status: number | null | undefined): string {
  return translateDomainValue("vmStatus", status);
}

export function nodeStatusLabel(
  status: string | number | null | undefined,
): string {
  return translateDomainValue("nodeStatus", status);
}

export function localizedDocumentTitle(page?: string): string {
  return page
    ? i18n.global.t("app.documentTitle", { page })
    : i18n.global.t("app.defaultTitle");
}

export function useLocalizedDocumentTitle(
  page: MaybeRefOrGetter<string | null | undefined>,
): void {
  const { locale } = useI18n({ useScope: "global" });
  watchEffect(() => {
    void locale.value;
    const value = toValue(page);
    document.title = localizedDocumentTitle(value || undefined);
  });
}

export function formatDateTime(
  value: string | null | undefined,
  format: "short" | "medium" = "short",
): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return i18n.global.d(date, format);
}

export function formatNumber(value: number, format: "decimal" | "oneDecimal" = "decimal"): string {
  return i18n.global.n(value, format);
}
