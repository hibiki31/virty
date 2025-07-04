import { apiClient } from "@/api";
import type { paths, components } from "@/api/openapi";

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
  query.page = (query.page || 1) - 1;
  const res = await apiClient.GET("/api/vms", {
    params: {
      query: query,
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

export function openVNC(uuid: string) {
  window.open(
    `/novnc/vnc.html?resize=remote&autoconnect=true&path=novnc/websockify?token=${uuid}`
  );
}

export function getPowerColor(statusCode: number) {
  if (statusCode === 1) return "primary";
  else if (statusCode === 5) return "grey-lighten-2";
  else if (statusCode === 7) return "purple";
  else if (statusCode === 10) return "red";
  else if (statusCode === 20) return "purple";
  else return "yellow";
}
