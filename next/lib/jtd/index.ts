import Ajv from 'ajv/dist/jtd';
import { Schema } from 'jtd';

export const generateProperty = (propertyJtd: Schema, rootJtd: Schema = propertyJtd): any => {
  return 'properties' in propertyJtd
    ? generateProperties(propertyJtd.properties as Schema, rootJtd)
    : 'ref' in propertyJtd
    ? generateProperty((rootJtd.definitions as any)[propertyJtd.ref] as Schema, rootJtd)
    : 'discriminator' in propertyJtd
    ? generateDiscriminatorProperty(propertyJtd, rootJtd)
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
  const defaultDiscriminatorValue = defaultValue?.[discriminator];
  if (!defaultDiscriminatorValue || (typeof defaultValue === 'object' && Object.keys(defaultValue).length >= 2)) {
    return discriminatorJtd.metadata?.default;
  }
  return {
    [discriminator]: defaultDiscriminatorValue,
    ...generateProperty((discriminatorJtd as any).mapping[defaultDiscriminatorValue], rootJtd),
  };
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
