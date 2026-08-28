import App from "@/App.vue";
import notify, {
  apiErrorRef,
  formatNotificationBody,
  formatNotificationTitle,
  formatNotificationText,
  notificationContentFromError,
  notifyTask,
  rawTextRef,
  type NotificationPayload,
} from "@/composables/notify";
import { TranslationError, translationRef } from "@/composables/i18n";
import { setLocale } from "@/plugins/i18n";
import { mount } from "@vue/test-utils";
import { defineComponent, h, nextTick } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  baseNotify: vi.fn(),
}));

vi.mock("@kyvg/vue3-notification", () => ({
  useNotification: () => ({ notify: mocks.baseNotify }),
}));

describe("API notification", () => {
  beforeEach(() => {
    mocks.baseNotify.mockReset();
  });

  it("translation、raw値、API envelopeを表示境界で解決する", () => {
    expect(formatNotificationText(translationRef("common.notifications.success"))).toBe("Success");
    expect(formatNotificationText(rawTextRef("task-1"))).toBe("task-1");
    expect(formatNotificationText(apiErrorRef({
      detail: { code: "resource_not_found", message: "Raw fallback" },
    }))).toBe("The requested resource was not found.");
  });

  it("Project業務errorも共通envelopeのcodeから翻訳する", () => {
    const content = apiErrorRef({
      detail: {
        code: "vm_project_resource_conflict",
        message: "Raw fallback that must not be displayed.",
      },
    });

    expect(formatNotificationText(content)).toBe(
      "The VM uses resources that are not granted to the destination project.",
    );
    setLocale("ja");
    expect(formatNotificationText(content)).toBe(
      "VMが移動先プロジェクトに許可されていないリソースを使用しています。",
    );
  });

  it("typed client errorをtranslation contentとして保持する", () => {
    const content = notificationContentFromError(
      new TranslationError(translationRef("webauthn.credentialFailed")),
    );

    expect(content).toEqual(translationRef("webauthn.credentialFailed"));
    expect(formatNotificationText(content)).toBe(
      "The WebAuthn credential could not be created.",
    );
    setLocale("ja");
    expect(formatNotificationText(content)).toBe(
      "WebAuthn credentialを作成できませんでした。",
    );

    const apiError = new Error("network unavailable");
    expect(notificationContentFromError(apiError)).toEqual(apiErrorRef(apiError));
  });

  it("default notificationもtranslation refのまま保持する", () => {
    notify("success");

    expect(mocks.baseNotify).toHaveBeenCalledWith({
      type: "success",
      data: {
        title: translationRef("common.notifications.success"),
        content: translationRef("common.notifications.apiCompleted"),
      },
    });
  });

  it("translation refとAPI envelopeを保持し、表示中のlocale変更へ追従する", () => {
    notify(
      "error",
      translationRef("common.errors.apiRequestFailed"),
      apiErrorRef({ detail: { code: "permission_denied", message: "Raw fallback" } }),
    );

    expect(mocks.baseNotify).toHaveBeenCalledWith({
      type: "error",
      data: {
        title: translationRef("common.errors.apiRequestFailed"),
        content: apiErrorRef({
          detail: { code: "permission_denied", message: "Raw fallback" },
        }),
      },
    });

    const payload = mocks.baseNotify.mock.calls[0][0].data as NotificationPayload;
    expect(formatNotificationTitle(payload)).toBe("The API request failed.");
    expect(formatNotificationBody(payload)).toBe(
      "You do not have permission to perform this operation.",
    );

    setLocale("ja");
    expect(formatNotificationTitle(payload)).toBe("APIリクエストに失敗しました。");
    expect(formatNotificationBody(payload)).toBe("この操作を実行する権限がありません。");
  });

  it("Appの表示中toastをlocale変更時に再解決する", async () => {
    const payload: NotificationPayload = {
      title: translationRef("common.errors.apiRequestFailed"),
      content: apiErrorRef({
        detail: { code: "permission_denied", message: "Raw fallback" },
      }),
    };
    const ContainerStub = defineComponent({
      template: "<div><slot /></div>",
    });
    const NotificationsStub = defineComponent({
      setup(_, { slots }) {
        return () => h("section", slots.body?.({ item: { type: "error", data: payload } }));
      },
    });
    const wrapper = mount(App, {
      global: {
        stubs: {
          Notifications: NotificationsStub,
          RouterView: true,
          VAlert: ContainerStub,
          VAlertTitle: ContainerStub,
          VApp: ContainerStub,
        },
      },
    });

    expect(wrapper.text()).toContain("The API request failed.");
    expect(wrapper.text()).toContain("You do not have permission");

    setLocale("ja");
    await nextTick();
    expect(wrapper.text()).toContain("APIリクエストに失敗しました。");
    expect(wrapper.text()).toContain("この操作を実行する権限がありません。");
  });

  it("task UUIDをqueue通知へ含め、欠落時は空文字にする", () => {
    notifyTask("task-1");
    notifyTask(undefined);

    expect(mocks.baseNotify).toHaveBeenNthCalledWith(1, {
      type: "success",
      data: {
        title: translationRef("common.notifications.queued"),
        content: rawTextRef("task-1"),
      },
    });
    expect(mocks.baseNotify).toHaveBeenNthCalledWith(2, {
      type: "success",
      data: {
        title: translationRef("common.notifications.queued"),
        content: rawTextRef(undefined),
      },
    });
  });
});
