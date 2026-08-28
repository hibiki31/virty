import { useNotification } from "@kyvg/vue3-notification";
import { formatApiError } from "@/composables/apiError";
import {
  resolveTranslation,
  translationRef,
  TranslationError,
  type TranslationRef,
} from "@/composables/i18n";

const { notify: baseNotify } = useNotification();

declare type NotificationType = "warn" | "success" | "error" | "info";

export type ApiErrorRef = { kind: "api-error"; error: unknown };
export type RawTextRef = { kind: "raw-text"; text: string };
export type NotificationContent = TranslationRef | ApiErrorRef | RawTextRef;
export type NotificationPayload = {
  title: TranslationRef;
  content: NotificationContent;
};

export function apiErrorRef(error: unknown): ApiErrorRef {
  return { kind: "api-error", error };
}

export function rawTextRef(text: string | null | undefined): RawTextRef {
  return { kind: "raw-text", text: text ?? "" };
}

export function formatNotificationText(content: NotificationContent): string {
  if (content.kind === "translation") return resolveTranslation(content);
  if (content.kind === "raw-text") return content.text;
  return formatApiError(content.error);
}

export function notificationContentFromError(error: unknown): NotificationContent {
  return error instanceof TranslationError ? error.content : apiErrorRef(error);
}

export function formatNotificationTitle(payload: NotificationPayload): string {
  return resolveTranslation(payload.title);
}

export function formatNotificationBody(payload: NotificationPayload): string {
  return formatNotificationText(payload.content);
}

function notify(
  type: NotificationType,
  title: TranslationRef = translationRef("common.notifications.success"),
  text: NotificationContent = translationRef("common.notifications.apiCompleted"),
) {
  baseNotify({
    type,
    data: { title, content: text } satisfies NotificationPayload,
  });
}

export function notifyTask(uuid: string | undefined | null) {
  baseNotify({
    type: "success",
    data: {
      title: translationRef("common.notifications.queued"),
      content: rawTextRef(uuid),
    } satisfies NotificationPayload,
  });
}

export default notify;
