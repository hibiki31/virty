import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";
import { toApiPageQuery } from "@/composables/pagination";

import {
  formatDateTime,
  formatNumber,
  translateDomainValue,
} from "@/composables/i18n";
import i18n from "@/plugins/i18n";

export type typeListTask =
  paths["/api/tasks"]["get"]["responses"]["200"]["content"]["application/json"];

export type typeListTaskQuery = NonNullable<
  paths["/api/tasks"]["get"]["parameters"]["query"]
>;

export const initTaskList: typeListTask = {
  count: 0,
  data: [],
};

export async function getTaskList(query: typeListTaskQuery) {
  const res = await apiClient.GET("/api/tasks", {
    params: {
      query: toApiPageQuery(query),
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initTaskList;
  }
}

export const methodTranslation = (method: string) => {
  switch (method) {
    case "add":
    case "post":
      return "POST";
    case "update":
    case "put":
      return "PUT";
    case "delete":
      return "DELETE";
    case "change":
    case "cahnge":
    case "patch":
      return "PATCH";
  }
};

// 既存の利用箇所との互換性を保つ。
export const methodTransration = methodTranslation;

export const copyClipBoardCurl = (item: typeListTask["data"][0]) => {
  const comand = `curl -X '${methodTransration(item.method)}' \\
'${location.protocol}//${location.host}/api/${item.resource}/${item.object}' \\
-H 'accept: application/json' \\
-H 'Authorization: Bearer ${""}' \\
-d '${JSON.stringify(item.request)}'`;
  console.log(comand);
};

export const getMethodColor = (statusCode: string) => {
  if (statusCode === "post") return "primary";
  else if (statusCode === "put") return "info";
  else if (statusCode === "delete") return "error";
  else return "yellow";
};

export const getResourceIcon = (resource: string | undefined | null) => {
  if (resource === "vm") return "mdi-desktop-tower";
  else if (resource === "node") return "mdi-server";
  else if (resource === "storage") return "mdi-database";
  else if (resource === "network") return "mdi-wan";
  else if (resource === "image") return "mdi-harddisk";
  else return "mdi-help-rhombus";
};

export const getStatusColor = (statusCode: string | undefined | null) => {
  switch (statusCode) {
    case "finish":
      return "primary";
    case "init":
      return "blue-grey";
    case "error":
      return "error";
    case "lost":
      return "grey";
    case "start":
      return "info";
  }
  return "yellow";
};

export const taskStatusLabel = (value: string | null | undefined) =>
  translateDomainValue("taskStatus", value);

export const taskResourceLabel = (value: string | null | undefined) =>
  translateDomainValue("taskResource", value);

export const taskMethodLabel = (value: string | null | undefined) =>
  translateDomainValue("taskMethod", value);

export const formatTaskRequest = (value: unknown): string => {
  if (typeof value === "string") return value;
  return JSON.stringify(value) ?? String(value ?? "");
};

export const taskRequestLabel = (value: unknown): string =>
  i18n.global.t("pages.tasks.requestParametersWithValue", {
    request: formatTaskRequest(value),
  });

export const formatTaskDateTime = (val: string | undefined | null) => {
  return formatDateTime(val, "short") || i18n.global.t("common.values.unavailable");
};

export const formatTaskDuration = (val: number) => {
  if (isFinite(val)) {
    return formatNumber(Number(val), "oneDecimal");
  }
  return formatNumber(0, "oneDecimal");
};
