import Ajv from 'ajv/dist/jtd';
import { Schema } from 'jtd';
import { FieldValues, UseFormGetValues } from 'react-hook-form';
import { useFormExtraData } from '~/store/formState';

export const generateProperty = (propertyJtd: Schema, rootJtd: Schema = propertyJtd): any => {
  return 'properties' in propertyJtd
    ? generateProperties(propertyJtd.properties as Schema, rootJtd)
    : 'ref' in propertyJtd
    ? generateProperty((rootJtd.definitions as any)[propertyJtd.ref] as Schema, rootJtd)
    : 'discriminator' in propertyJtd
    ? generateDiscriminatorProperty(propertyJtd, rootJtd)
    : typeof propertyJtd.metadata?.default === 'function'
    ? ''
    : propertyJtd.metadata?.default;
};

export const generateProperties = (propertiesJtd: Schema, rootJtd: Schema) => {
  const properties: { [key: string]: any } = {};
  Object.entries(propertiesJtd).forEach(([key, propertyJtd]: [string, Schema]) => {
    properties[key] = generateProperty(propertyJtd, rootJtd);
  });
  return properties;
};

export const generateDiscriminatorProperty = (discriminatorJtd: Schema, rootJtd: Schema) => {
  const discriminator = (discriminatorJtd as any).discriminator;
  const defaultValue = discriminatorJtd.metadata?.default as any;
  if (typeof defaultValue !== 'object') {
    return {};
  }
  const defaultDiscriminatorValue = defaultValue?.[discriminator];
  if (!defaultDiscriminatorValue || Object.keys(defaultValue).length >= 2) {
    return defaultValue;
  }
  return {
    [discriminator]: defaultDiscriminatorValue,
    ...generateProperty((discriminatorJtd as any).mapping[defaultDiscriminatorValue], rootJtd),
  };
};

export const getRelatedValue =
  (getValues: UseFormGetValues<FieldValues>, currentName: string) =>
  (popCount: number, addName: string, isExtraData?: boolean) => {
    const path = currentName.split('.');
    const prefixName = path.slice(0, path.length - popCount).join('.');
    const propertyName = prefixName + '.' + addName;
    const { extraData } = useFormExtraData(propertyName);

    if (isExtraData) {
      return extraData || {};
    }

    return getValues(propertyName);
  };

/**
 * Custom Ajv instance
 */
export const ajv = new Ajv({
  strict: false,
  allErrors: true,
} as any);

ajv.addKeyword({
  keyword: 'required',
  schemaType: 'boolean',
  validate: (schema: boolean, _data, _parentSchema, dataCxt) => {
    if (!schema) {
      return true;
    }
    if (!dataCxt) {
      return false;
    }
    const value = dataCxt.parentData?.[dataCxt.parentDataProperty];
    if (Array.isArray(value)) {
      return value.length > 0;
    }
    return !!dataCxt.parentData?.[dataCxt.parentDataProperty];
  },
});
