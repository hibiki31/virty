/**
 * MetaData of JTD property.
 */
export interface MetaData {
  name: string;
  description?: string;
  default?: any;
  discriminatorName?: string;
  hiddenDiscriminator?: boolean;
  /**
   * If true, the property is spread into the parent object.
   * (Only for parent property)
   * @default false
   */
  spread?: boolean;
  /**
   * If true, the property label will be hidden.
   * (Only for parent property)
   * @default false
   */
  hiddenLabel?: boolean;
  /**
   * If true, the property is not displayed in the dialog.
   * @default false
   */
  hidden?: boolean;
  /**
   * If true, the property is required.
   * (Do not use optionalProperties because it is not possible to define the order of the forms.)
   * @default true
   */
  required?: boolean;
  /**
   * If true, the property is read-only.
   * @default false
   */
  readonly?: boolean;
  /**
   * Define types not supported by the JTD
   * @default undefined
   */
  customType?: 'mappingBoolean' | 'password';
  /**
   * Set the choices in the select form.
   * If the value is a table name, the list is fetched; if it is an array, it is used as is.
   * @default undefined
   * @example
   * choices: 'users'
   * choices: [{ label: 'Label A', value: 'a' }, { label: 'Label 1', value: 1 }]
   */
  choices?: Choice[] | string;
  /**
   * If true, properties can be added to or removed from the array.
   * @default true
   */
  editableArray?: boolean;
  /**
   * Relative path to label string.
   * @default undefined
   * @example
   * labelPath: ['label']
   * labelPath: ['options', 'label']
   */
  labelPath?: string[];
}

export interface Choice {
  label: string;
  value: string | number;
}
