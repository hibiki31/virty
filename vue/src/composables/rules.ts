// 必須
export const required = (value: string) => !!value || "Required.";

// 文字数制限
export const limitLength64 = (value: string) =>
  value.length <= 64 || "64 characters maximum.";
export const limitLength32 = (value: string) =>
  value.length <= 32 || "64 characters maximum.";

/**
 * 名称として許可されている文字種[ A-Z, a-z, 0-9, -] に制限
 */
export const characterRestrictions = (value: string) => {
  const regex = /^[A-Za-z0-9-]*$/;
  return regex.test(value) || "Can use character A-Z, a-z, 0-9, -";
};
export const intValueRestrictions = (value: string) =>
  Number.isInteger(Number(value)) || "Only Int value";

export const portTCP = (value: any): true | string => {
  const port = Number(value);
  if (Number.isInteger(port) && port >= 0 && port < 65536) {
    return true;
  }
  return "Only tcp port 0~65535";
};

// 先頭文字制限
export const firstCharacterRestrictions = (value: string) => {
  const regex = /^[A-Za-z].*/;
  return regex.test(value) || "Can use first character A-Z, a-z";
};
