import { apiClient } from "@/api";
import type { paths } from "@/api/openapi";

import { format, parse, parseISO } from "date-fns";
import { ja } from "date-fns/locale/ja";

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
  query.page = (query.page || 1) - 1;
  const res = await apiClient.GET("/api/tasks", {
    params: {
      query: query,
    },
  });
  if (res.data) {
    return res.data;
  } else {
    return initTaskList;
  }
}

export const methodTransration = (method: string) => {
  switch (method) {
    case "add":
      return "POST";
    case "update":
      return "PUT";
    case "delete":
      return "DELETE";
    case "cahnge":
      return "PATH";
  }
};

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
  if (resource === "vm") return "mdi-cube-outline";
  else if (resource === "node") return "mdi-server";
  else if (resource === "storage") return "mdi-database";
  else if (resource === "network") return "mdi-wan";
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

export const toJST = (val: string | undefined | null) => {
  if (val) {
    return format(parseISO(val), "yyyy-MM-dd HH:mm", { locale: ja });
  } else {
    return "error";
  }
};

export const toFixedTow = (val: number) => {
  if (isFinite(val)) {
    return Number(val).toFixed(1);
  }
  return 0;
};
