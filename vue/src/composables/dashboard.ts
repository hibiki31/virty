import { apiClient } from "@/api";
import type { components } from "@/api/openapi";
import {
  formatDateTime,
  formatNumber as formatLocaleNumber,
  translateDomainValue,
} from "@/composables/i18n";
import i18n from "@/plugins/i18n";

export type DashboardResponse = components["schemas"]["DashboardResponse"];

export class DashboardLoadError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`Dashboard request failed with status ${status}.`);
    this.name = "DashboardLoadError";
    this.status = status;
  }
}

export async function getDashboard(admin = false): Promise<DashboardResponse> {
  const response = await apiClient.GET("/api/dashboard", {
    params: { query: { admin } },
  });

  if (response.data) {
    return response.data;
  }

  throw new DashboardLoadError(response.response.status);
}

export function ratioPercent(value: number, total: number): number | null {
  if (!Number.isFinite(value) || !Number.isFinite(total) || total <= 0) {
    return null;
  }

  return Math.max(0, (value / total) * 100);
}

export function progressPercent(value: number | null): number {
  if (value === null || !Number.isFinite(value)) {
    return 0;
  }

  return Math.min(100, Math.max(0, value));
}

export function formatNumber(value: number): string {
  return formatLocaleNumber(value);
}

export function formatGib(value: number): string {
  return `${formatNumber(value)} GiB`;
}

export function formatPercentage(value: number | null): string {
  return value === null
    ? i18n.global.t("common.values.unavailable")
    : `${formatLocaleNumber(value)}%`;
}

export function formatTimestamp(value: string | null): string {
  return formatDateTime(value, "medium")
    || i18n.global.t("common.values.unavailable");
}

export function utilizationColor(value: number | null): string {
  if (value === null) {
    return "grey";
  }
  if (value > 80) {
    return "error";
  }
  if (value > 50) {
    return "warning";
  }
  return "primary";
}

export {
  taskMethodLabel,
  taskResourceLabel,
  taskStatusLabel,
} from "@/composables/task";

export const nodeRoleLabel = (value: string | null) =>
  translateDomainValue("nodeRole", value);
export const networkTypeLabel = (value: string | null) =>
  translateDomainValue("networkType", value);
