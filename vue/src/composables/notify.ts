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

export default notify;
