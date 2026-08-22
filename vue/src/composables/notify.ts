import { useNotification } from "@kyvg/vue3-notification";
import type { components } from "@/api/openapi";

const { notify: baseNotify } = useNotification();

type responsesValidationError = components["schemas"]["HTTPValidationError"];

declare type NotificationType = "warn" | "success" | "error" | "info";

export function formatNotificationText(
  text: responsesValidationError | string | undefined,
): string {
  if (typeof text === "string") {
    return text || "Unknown error";
  }

  if (typeof text === "undefined") {
    return "Unknown error";
  }

  if (Array.isArray(text.detail)) {
    const messages = text.detail
      .map((entry) => entry.msg)
      .filter((message): message is string => Boolean(message));

    return messages.length > 0 ? messages.join("; ") : "Unknown error";
  }

  return "Unknown error";
}

function notify(
  type: NotificationType,
  title = "Success",
  text: responsesValidationError | string | undefined = "API request completed"
) {
  baseNotify({
    type,
    title,
    text: formatNotificationText(text),
  });
}

export function notifyTask(uuid: string | undefined | null) {
  baseNotify({
    type: "success",
    title: "Task has been queued",
    text: uuid || "",
  });
}

export default notify;
