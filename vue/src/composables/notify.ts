import { useNotification } from "@kyvg/vue3-notification";
import type { paths, components } from "@/api/openapi";

const { notify: baseNotify } = useNotification();

type responsesValidationError = components["schemas"]["HTTPValidationError"];

declare type NotificationType = "warn" | "success" | "error" | "info";

function notify(
  type: NotificationType,
  title = "Success",
  text: responsesValidationError | string | undefined = "API request completed"
) {
  let message: string;

  if (typeof text === "string" || typeof text === "undefined") {
    message = text || "Unknown error";
  } else if (typeof text as responsesValidationError) {
    message = "";
  } else if (text && Array.isArray((text as responsesValidationError).detail)) {
    // Extract messages from the detail array
    message = (text as responsesValidationError)
      .detail!.map((e) => e.msg)
      .join("; ");
  } else {
    message = "Unknown error";
  }

  baseNotify({
    type,
    title,
    text: message,
  });
}

export function notifyTask(uuid: string) {
  baseNotify({
    type: "success",
    title: "Task has been queued",
    text: uuid,
  });
}

export default notify;
