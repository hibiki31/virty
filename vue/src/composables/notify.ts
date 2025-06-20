import { useNotification } from "@kyvg/vue3-notification";
const { notify: baseNotify } = useNotification();

declare type NotificationType = "warn" | "success" | "error" | "info";

function notify(type: NotificationType, title = "Success", text = "") {
  baseNotify({
    type: type,
    title: title,
    text: text,
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
