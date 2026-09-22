import { createI18n } from "vue-i18n";
import { en as vuetifyEn, ja as vuetifyJa } from "vuetify/locale";
import type { components } from "@/api/openapi";

import en from "@/locales/en.json";
import ja from "@/locales/ja.json";

export const supportedLocales = ["en", "ja"] as const;
export type SupportedLocale = (typeof supportedLocales)[number];
export type MessageSchema = typeof en;
type MessageKeyOf<T> = {
  [Key in keyof T & string]: T[Key] extends string
    ? Key
    : T[Key] extends Record<string, unknown>
      ? `${Key}.${MessageKeyOf<T[Key]>}`
      : never;
}[keyof T & string];
export type MessageKey = MessageKeyOf<MessageSchema>;

const appMessages: Record<SupportedLocale, MessageSchema> = { en, ja };
type I18nMessageSchema = MessageSchema & { $vuetify: typeof vuetifyEn };
const messages: Record<SupportedLocale, I18nMessageSchema> = {
  en: { ...appMessages.en, $vuetify: vuetifyEn },
  ja: { ...appMessages.ja, $vuetify: vuetifyJa as typeof vuetifyEn },
};

type GeneratedApiErrorCode = components["schemas"]["ApiErrorCode"];
type CatalogApiErrorCode = keyof MessageSchema["apiErrors"];
type ApiErrorCatalogIsComplete = Exclude<
  GeneratedApiErrorCode,
  CatalogApiErrorCode
> extends never
  ? Exclude<CatalogApiErrorCode, GeneratedApiErrorCode> extends never
    ? true
    : false
  : false;
const apiErrorCatalogIsComplete: ApiErrorCatalogIsComplete = true;
void apiErrorCatalogIsComplete;

type GeneratedFieldErrorCode = components["schemas"]["FieldErrorCode"];
type CatalogFieldErrorCode = keyof MessageSchema["fieldErrors"];
type FieldErrorCatalogIsComplete = Exclude<
  GeneratedFieldErrorCode,
  CatalogFieldErrorCode
> extends never
  ? Exclude<CatalogFieldErrorCode, GeneratedFieldErrorCode> extends never
    ? true
    : false
  : false;
const fieldErrorCatalogIsComplete: FieldErrorCatalogIsComplete = true;
void fieldErrorCatalogIsComplete;

export const API_ERROR_CODES = Object.freeze(
  Object.keys(en.apiErrors) as CatalogApiErrorCode[],
);
export const FIELD_ERROR_CODES = Object.freeze(
  Object.keys(en.fieldErrors) as CatalogFieldErrorCode[],
);

export const LOCALE_STORAGE_KEY = "virty:locale";

function toBrowserLocale(value: string | null | undefined): SupportedLocale | null {
  if (!value) return null;
  const language = value.toLowerCase().split("-")[0];
  return language === "en" || language === "ja" ? language : null;
}

export function resolveLocale(
  storedLocale: string | null,
  browserLanguages: readonly string[],
): SupportedLocale {
  if (storedLocale === "en" || storedLocale === "ja") return storedLocale;

  for (const language of browserLanguages) {
    const supported = toBrowserLocale(language);
    if (supported) return supported;
  }
  return "en";
}

function readStoredLocale(): string | null {
  try {
    return typeof localStorage === "undefined"
      ? null
      : localStorage.getItem(LOCALE_STORAGE_KEY);
  } catch {
    return null;
  }
}

function browserLanguages(): readonly string[] {
  if (typeof navigator === "undefined") return [];
  return navigator.languages.length > 0
    ? navigator.languages
    : navigator.language
      ? [navigator.language]
      : [];
}

export function resolveInitialLocale(): SupportedLocale {
  return resolveLocale(readStoredLocale(), browserLanguages());
}

export function createVirtyI18n(locale: SupportedLocale = "en") {
  return createI18n<[I18nMessageSchema], SupportedLocale, false>({
    legacy: false,
    globalInjection: true,
    locale,
    fallbackLocale: "en",
    messages,
    datetimeFormats: {
      en: {
        short: {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        },
        medium: { dateStyle: "medium", timeStyle: "medium" },
      },
      ja: {
        short: {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        },
        medium: { dateStyle: "medium", timeStyle: "medium" },
      },
    },
    numberFormats: {
      en: {
        decimal: { maximumFractionDigits: 1 },
        oneDecimal: { minimumFractionDigits: 1, maximumFractionDigits: 1 },
      },
      ja: {
        decimal: { maximumFractionDigits: 1 },
        oneDecimal: { minimumFractionDigits: 1, maximumFractionDigits: 1 },
      },
    },
  });
}

const i18n = createVirtyI18n(resolveInitialLocale());

export function setLocale(locale: SupportedLocale, persist = false): void {
  i18n.global.locale.value = locale;
  if (typeof document !== "undefined") {
    document.documentElement.lang = locale;
  }
  if (persist) {
    try {
      if (typeof localStorage !== "undefined") {
        localStorage.setItem(LOCALE_STORAGE_KEY, locale);
      }
    } catch {
      // ブラウザーの保護設定によってStorageを利用できない場合がある。
    }
  }
}

setLocale(i18n.global.locale.value);

export default i18n;
