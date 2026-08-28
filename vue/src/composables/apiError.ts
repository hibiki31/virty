import i18n from "@/plugins/i18n";

export type ApiErrorParam = string | number | boolean | null;
export type ApiErrorParams = Record<string, ApiErrorParam>;

type ApiFieldError = {
  field: string;
  code: string;
  params?: ApiErrorParams | null;
};

type ApiErrorDetail = {
  code: string;
  message: string;
  params?: ApiErrorParams | null;
  errors?: ApiFieldError[] | null;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function normalizeParams(value: unknown): ApiErrorParams {
  if (!isRecord(value)) return {};
  return Object.fromEntries(
    Object.entries(value).filter((entry): entry is [string, ApiErrorParam] => {
      const param = entry[1];
      return param === null || ["string", "number", "boolean"].includes(typeof param);
    }),
  );
}

function translatedError(code: string, params: ApiErrorParams): string | null {
  const key = `apiErrors.${code}`;
  return i18n.global.te(key) ? i18n.global.t(key, params) : null;
}

function translatedFieldError(code: string, params: ApiErrorParams): string | null {
  const key = `fieldErrors.${code}`;
  return i18n.global.te(key) ? i18n.global.t(key, params) : null;
}

function fieldLabel(field: string): string {
  const parts = field.split(".").filter(part => part && !/^\d+$/.test(part));
  const name = parts[parts.length - 1];
  if (!name || name === "*") return field;

  for (const key of [`apiFields.${name}`, `common.fields.${name}`]) {
    if (i18n.global.te(key)) return i18n.global.t(key);
  }
  return field;
}

function isApiErrorDetail(value: unknown): value is ApiErrorDetail {
  return isRecord(value)
    && typeof value.code === "string"
    && typeof value.message === "string";
}

function formatEnvelope(detail: ApiErrorDetail): string {
  const errors = Array.isArray(detail.errors) ? detail.errors : [];
  const fieldMessages = errors.flatMap(error => {
    if (!isRecord(error) || typeof error.field !== "string" || typeof error.code !== "string") {
      return [];
    }
    const message = translatedFieldError(error.code, normalizeParams(error.params));
    return message ? [`${fieldLabel(error.field)}: ${message}`] : [];
  });
  if (fieldMessages.length > 0) return fieldMessages.join("; ");

  return translatedError(detail.code, normalizeParams(detail.params)) || detail.message;
}

export function formatApiError(error: unknown): string {
  if (!isRecord(error)) return i18n.global.t("common.errors.apiRequestFailed");

  const detail = error.detail;
  if (isApiErrorDetail(detail)) return formatEnvelope(detail);
  return i18n.global.t("common.errors.apiRequestFailed");
}
