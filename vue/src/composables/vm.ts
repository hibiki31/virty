import { apiClient } from "@/api";
import type { paths, components } from "@/api/openapi";
import { toApiPageQuery } from "@/composables/pagination";
import { formatNumber, translationRef } from "@/composables/i18n";
import notify, { apiErrorRef } from "@/composables/notify";

export type bodyPostVM = components["schemas"]["DomainForCreate"];
export type typeListVM =
  paths["/api/vms"]["get"]["responses"]["200"]["content"]["application/json"];
export type typeListVMQuery = NonNullable<
  paths["/api/vms"]["get"]["parameters"]["query"]
>;

export const initVMList: typeListVM = {
  count: 0,
  data: [],
};

export const itemsMemory = [
  { title: "512MB", value: 512 },
  { title: "1GB", value: 1024 },
  { title: "2GB", value: 2048 },
  { title: "4GB", value: 4096 },
  { title: "8GB", value: 8192 },
  { title: "16GB", value: 16384 },
  { title: "24GB", value: 24576 },
  { title: "32GB", value: 32768 },
  { title: "64GB", value: 65536 },
  { title: "128GB", value: 131072 },
  { title: "256GB", value: 262144 },
  { title: "512GB", value: 524288 },
  { title: "1TB", value: 1048576 },
];

export const itemsCPU = [
  { title: "1 Core", value: 1 },
  { title: "2 Core", value: 2 },
  { title: "4 Core", value: 4 },
  { title: "8 Core", value: 8 },
  { title: "12 Core", value: 12 },
  { title: "16 Core", value: 16 },
  { title: "24 Core", value: 24 },
];

export async function getVMList(query: typeListVMQuery) {
  const res = await apiClient.GET("/api/vms", {
    params: {
      query: toApiPageQuery(query),
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initVMList;
  }
}

export function vmPowerOff(uuid: string) {
  apiClient.PATCH("/api/tasks/vms/{uuid}/power", {
    params: { path: { uuid: uuid } },
    body: { status: "off" },
  });
}

export function vmPowerOn(uuid: string) {
  apiClient.PATCH("/api/tasks/vms/{uuid}/power", {
    params: { path: { uuid: uuid } },
    body: { status: "on" },
  });
}

export async function openVNC(uuid: string) {
  const consoleWindow = window.open("about:blank", "_blank");
  if (consoleWindow) consoleWindow.opener = null;

  try {
    const response = await apiClient.POST("/api/vms/{uuid}/console-ticket", {
      params: { path: { uuid } },
    });
    if (!response.data) {
      consoleWindow?.close();
      notify(
        "error",
        translationRef("pages.vmDetail.notifications.consoleFailed"),
        apiErrorRef(response.error),
      );
      return;
    }

    const token = encodeURIComponent(response.data.token);
    const consoleUrl =
      `/novnc/vnc.html?resize=remote&autoconnect=true` +
      `&path=novnc/websockify?token=${token}`;
    if (consoleWindow) {
      consoleWindow.location.href = consoleUrl;
    } else {
      window.open(consoleUrl, "_blank", "noopener,noreferrer");
    }
  } catch {
    consoleWindow?.close();
    notify(
      "error",
      translationRef("pages.vmDetail.notifications.consoleFailed"),
      translationRef("pages.vmDetail.notifications.consoleUnreachable"),
    );
  }
}

export function getPowerColor(statusCode: number) {
  if (statusCode === 1) return "primary";
  else if (statusCode === 5) return "grey-lighten-2";
  else if (statusCode === 7) return "purple";
  else if (statusCode === 10) return "red";
  else if (statusCode === 20) return "purple";
  else return "yellow";
}

export function getStorageFileName(source: string) {
  const normalizedSource = source.replace(/\/+$/, "");
  return normalizedSource.split("/").pop() || source;
}

export function formatStorageCapacity(capacityGb: number | null | undefined) {
  return capacityGb == null ? "-" : `${formatNumber(capacityGb)} GB`;
}
