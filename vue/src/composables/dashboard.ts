import { apiClient } from "@/api";
import type { components } from "@/api/openapi";

export type DashboardResponse = components["schemas"]["DashboardResponse"];

export class DashboardLoadError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`Dashboard request failed with status ${status}.`);
    this.name = "DashboardLoadError";
    this.status = status;
  }
}

export async function getDashboard(): Promise<DashboardResponse> {
  const response = await apiClient.GET("/api/dashboard");

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

const numberFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 1,
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 1,
});

const timestampFormatter = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeStyle: "medium",
});

export function formatNumber(value: number): string {
  return numberFormatter.format(value);
}

export function formatGib(value: number): string {
  return `${formatNumber(value)} GiB`;
}

export function formatPercentage(value: number | null): string {
  return value === null ? "Unavailable" : `${percentFormatter.format(value)}%`;
}

export function formatTimestamp(value: string | null): string {
  if (!value) {
    return "Time unavailable";
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Time unavailable"
    : timestampFormatter.format(date);
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

export function titleCase(value: string | null): string {
  if (!value) {
    return "Unknown";
  }

  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function pluralize(
  count: number,
  singular: string,
  plural = `${singular}s`,
): string {
  return count === 1 ? singular : plural;
}
