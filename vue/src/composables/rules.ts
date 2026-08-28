import * as ipaddr from "ipaddr.js";
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import {
  resolveTranslation,
  translationRef,
  type TranslationRef,
} from "@/composables/i18n";

export type ValidationResult = true | TranslationRef;
type PureRule<Args extends unknown[]> = (...args: Args) => ValidationResult;

export function localizeRule<Args extends unknown[]>(
  rule: PureRule<Args>,
): (...args: Args) => true | string {
  return (...args) => {
    const result = rule(...args);
    return result === true ? true : resolveTranslation(result);
  };
}

export const required = (value: string): ValidationResult =>
  Boolean(value) || translationRef("validation.required");

export const limitLength64 = (value: string): ValidationResult =>
  value.length <= 64 || translationRef("validation.maxLength", { max: 64 });
export const limitLength32 = (value: string): ValidationResult =>
  value.length <= 32 || translationRef("validation.maxLength", { max: 32 });
export const limitLength16 = (value: string): ValidationResult =>
  value.length <= 16 || translationRef("validation.maxLength", { max: 16 });

export const characterRestrictions = (value: string): ValidationResult =>
  /^[A-Za-z0-9-]*$/.test(value)
  || translationRef("validation.characterRestrictions");

export const intValueRestrictions = (value: string): ValidationResult =>
  Number.isInteger(Number(value)) || translationRef("validation.integer");

export const portTCP = (value: unknown): ValidationResult => {
  const port = Number(value);
  return Number.isInteger(port) && port >= 0 && port < 65536
    ? true
    : translationRef("validation.tcpPort");
};

export const vlan = (value: unknown): ValidationResult => {
  const id = Number(value);
  return Number.isInteger(id) && id >= 1 && id <= 4094
    ? true
    : translationRef("validation.vlan");
};

export const firstCharacterRestrictions = (value: string): ValidationResult =>
  /^[A-Za-z].*/.test(value) || translationRef("validation.firstCharacter");

export const isValidIp = (value: string): ValidationResult =>
  ipaddr.isValid(value) || translationRef("validation.invalidIp");

export const requiredCheckbox = (value: boolean): ValidationResult =>
  value || translationRef("validation.requiredCheckbox");

export function isValidURL(value: string): ValidationResult {
  try {
    new URL(value);
    return true;
  } catch {
    return translationRef("validation.invalidUrl");
  }
}

const pureRules = {
  required,
  limitLength64,
  limitLength32,
  limitLength16,
  characterRestrictions,
  intValueRestrictions,
  portTCP,
  vlan,
  firstCharacterRestrictions,
  isValidIp,
  requiredCheckbox,
  isValidURL,
} as const;

type LocalizedRules = {
  [Key in keyof typeof pureRules]: (
    ...args: Parameters<(typeof pureRules)[Key]>
  ) => true | string;
};

function createLocalizedRules() {
  return {
    required: localizeRule(required),
    limitLength64: localizeRule(limitLength64),
    limitLength32: localizeRule(limitLength32),
    limitLength16: localizeRule(limitLength16),
    characterRestrictions: localizeRule(characterRestrictions),
    intValueRestrictions: localizeRule(intValueRestrictions),
    portTCP: localizeRule(portTCP),
    vlan: localizeRule(vlan),
    firstCharacterRestrictions: localizeRule(firstCharacterRestrictions),
    isValidIp: localizeRule(isValidIp),
    requiredCheckbox: localizeRule(requiredCheckbox),
    isValidURL: localizeRule(isValidURL),
  } satisfies LocalizedRules;
}

export function useLocalizedRules() {
  const { locale } = useI18n({ useScope: "global" });
  return computed(() => {
    void locale.value;
    return createLocalizedRules();
  });
}

export default createLocalizedRules();
