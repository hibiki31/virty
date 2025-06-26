import * as ipaddr from "ipaddr.js";

// 必須
export const required = (value: string) => !!value || "Required.";

// 文字数制限
export const limitLength64 = (value: string) =>
  value.length <= 64 || "64 characters maximum.";
export const limitLength32 = (value: string) =>
  value.length <= 32 || "64 characters maximum.";
export const limitLength16 = (value: string) =>
  value.length <= 16 || "64 characters maximum.";

const characterRestrictions = (value: string) => {
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

export const vlan = (value: any): true | string => {
  const port = Number(value);
  if (Number.isInteger(port) && port >= 1 && port < 4096) {
    return true;
  }
  return "Only vlan 1~4094";
};

// 先頭文字制限
export const firstCharacterRestrictions = (value: string) => {
  const regex = /^[A-Za-z].*/;
  return regex.test(value) || "Can use first character A-Z, a-z";
};

export const isValidIp = (value: string) =>
  ipaddr.isValid(value) || "Invalid IP format";

export const requiredCheckbox = (value: boolean) => value || "Required Ceckbox";

export function isValidURL(value: string) {
  try {
    new URL(value); // 例外が出なければほぼ仕様どおりの URL
    return true;
  } catch {
    return "not a valid URL.";
  }
}

const r = {
  required,
  limitLength64,
  limitLength32,
  limitLength16,
  /**
   * 名称として許可されている文字種[ A-Z, a-z, 0-9, -] に制限
   */
  characterRestrictions,
  intValueRestrictions,
  portTCP,
  vlan,
  firstCharacterRestrictions,
  isValidIp,
  requiredCheckbox,
  isValidURL,
} as const;

export default r;
