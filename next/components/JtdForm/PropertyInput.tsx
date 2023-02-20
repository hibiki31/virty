import {
  Autocomplete,
  Box,
  Checkbox,
  Chip,
  Divider,
  FormControl,
  FormControlLabel,
  FormHelperText,
  Grid,
  IconButton,
  InputLabel,
  LinearProgress,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Switch,
  SxProps,
  TextField,
  Theme,
  Typography,
} from '@mui/material';
import { Schema } from 'jtd';
import { FC, PropsWithChildren, useEffect } from 'react';
import { Controller, useFieldArray, useFormContext } from 'react-hook-form';
import { generateProperties, generateProperty, getRelatedValue } from '~/lib/jtd';
import { Choice, MetaData } from '~/lib/jtd/types';
import { useChoices } from '~/store/formState';
import { Close, Plus } from 'mdi-material-ui';
import { StepperForm } from './StepperForm';

export type WrapperComponentProps = PropsWithChildren<{ sx?: SxProps<Theme> }>;
const WrapperComponent: FC<WrapperComponentProps> = (props) => <Grid {...props} item xs={12} />;

export type PropertyInputProps = {
  prefixPropertyName?: string;
  propertyKey: string;
  propertyJtd: Schema & { metadata?: MetaData };
  rootJtd: Schema & { metadata?: MetaData };
  isEditing: boolean;
  isError?: boolean;
  parentComponentName?: 'StepperForm';
};

export const PropertyInput: FC<PropertyInputProps> = (props) => {
  const {
    prefixPropertyName = '',
    propertyKey,
    propertyJtd,
    rootJtd,
    isEditing,
    isError = false,
    parentComponentName,
  } = props;

  const { control, getValues, setValue } = useFormContext();
  const propertyName = prefixPropertyName + propertyKey;
  const { choices, isLoading } = useChoices(propertyJtd.metadata, getValues, propertyName);

  useEffect(() => {
    if (typeof propertyJtd.metadata?.default === 'function' && !getValues(propertyName)) {
      setValue(propertyName, propertyJtd.metadata.default(getRelatedValue(getValues, propertyName)));
    }
  }, [getValues, propertyName, propertyJtd.metadata, setValue]);

  if (propertyJtd.metadata?.hidden) {
    if (propertyJtd.metadata.hidden === true || propertyJtd.metadata.hidden(getRelatedValue(getValues, propertyName))) {
      return null;
    }
  }

  const labelPath = propertyJtd.metadata?.labelPath;
  const labelFromName = propertyJtd.metadata?.name || propertyKey;
  const labelFromPath = labelPath?.length && labelPath.reduce((acc, key) => acc?.[key], getValues(propertyName));
  const propertyLabel = ['string', 'number'].includes(typeof labelFromPath) ? labelFromPath : labelFromName;
  const propertyRequired = propertyJtd.metadata?.required !== false;
  const propertyReadonly = propertyJtd.metadata?.readonly;
  const propertySpread = parentComponentName === 'StepperForm' || propertyJtd.metadata?.spread;
  const hiddenPropertyLabel = parentComponentName === 'StepperForm' || propertyJtd.metadata?.hiddenLabel;

  if ('ref' in propertyJtd) {
    const refJtd = (rootJtd.definitions as any)[propertyJtd.ref] as Schema & { metadata?: MetaData };
    return (
      <PropertyInput
        prefixPropertyName={prefixPropertyName}
        propertyKey={propertyKey}
        propertyJtd={refJtd}
        rootJtd={rootJtd}
        isEditing={isEditing}
        isError={isError}
      />
    );
  }

  if (propertyJtd.metadata?.customType === 'stepper') {
    return <StepperForm {...props} />;
  }

  if ('properties' in propertyJtd) {
    return (
      <SpreadInputWrapper label={!hiddenPropertyLabel ? propertyLabel : undefined} spread={propertySpread}>
        {Object.entries(propertyJtd.properties as Schema).map(([nextPropertyKey, nextPropertyJtd]) => (
          <PropertyInput
            key={propertyKey ? `${propertyKey}.${nextPropertyKey}` : nextPropertyKey}
            prefixPropertyName={prefixPropertyName}
            propertyKey={propertyKey ? `${propertyKey}.${nextPropertyKey}` : nextPropertyKey}
            propertyJtd={nextPropertyJtd}
            rootJtd={rootJtd}
            isEditing={isEditing}
            isError={isError}
          />
        ))}
      </SpreadInputWrapper>
    );
  }

  if ('enum' in propertyJtd) {
    return (
      <WrapperComponent>
        <Controller
          name={propertyName}
          control={control}
          rules={{
            required: propertyRequired && `${propertyLabel} is required.`,
          }}
          render={({ field: { value, onChange }, fieldState: { error } }) => (
            <FormControl
              variant="outlined"
              required={propertyRequired}
              disabled={propertyReadonly}
              fullWidth
              error={!!error || isError}
            >
              <InputLabel id={propertyName}>{propertyLabel}</InputLabel>
              <Select
                label={propertyLabel}
                labelId={propertyName}
                inputProps={{ readOnly: !isEditing }}
                value={value}
                onChange={onChange}
              >
                {propertyJtd.enum.map((v: string) => (
                  <MenuItem key={`${propertyKey}.${v}`} value={v}>
                    {v === '' ? <em>None</em> : v}
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>{error?.message || ' '}</FormHelperText>
            </FormControl>
          )}
        />
      </WrapperComponent>
    );
  }

  if (propertyJtd.metadata && 'choices' in propertyJtd.metadata) {
    return (
      <WrapperComponent>
        <Controller
          name={propertyName}
          control={control}
          rules={{
            validate: (value: Choice['value']) => {
              if (propertyRequired && !value) {
                return `${propertyLabel} is required.`;
              }
              return true;
            },
          }}
          render={({ field: { value, onChange }, fieldState: { error } }) => (
            <FormControl
              variant="outlined"
              required={propertyRequired}
              disabled={propertyReadonly}
              fullWidth
              error={!!error || isError}
            >
              <InputLabel id={propertyName}>{propertyLabel}</InputLabel>
              {(propertyJtd as any).elements ? (
                <Select
                  label={propertyLabel}
                  labelId={propertyName}
                  multiple
                  inputProps={{ readOnly: !isEditing }}
                  value={value}
                  onChange={(e) => onChange(e.target.value)}
                  renderValue={(selectedValues: Choice['value'][]) => (
                    <Box component="div" sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selectedValues.map((v) => (
                        <Chip key={v} label={choices.find((c) => c.value === v)?.label} />
                      ))}
                    </Box>
                  )}
                >
                  {choices.map((c) => (
                    <MenuItem key={c.value} value={c.value}>
                      <Checkbox checked={(value as Choice['value'][]).indexOf(c.value) > -1} />
                      <ListItemText primary={c.label} />
                    </MenuItem>
                  ))}
                </Select>
              ) : (
                <Select
                  label={propertyLabel}
                  labelId={propertyName}
                  inputProps={{ readOnly: !isEditing }}
                  value={value || ''}
                  onChange={onChange}
                >
                  {!propertyRequired && (
                    <MenuItem value="">
                      <em>None</em>
                    </MenuItem>
                  )}
                  {isLoading && (
                    <MenuItem value={value}>
                      <em>Loading...</em>
                    </MenuItem>
                  )}
                  {choices.map((c, i) => (
                    <MenuItem key={`${propertyKey}.${i}`} value={c.value}>
                      {c.label}
                    </MenuItem>
                  ))}
                </Select>
              )}
              {isLoading && <LinearProgress sx={{ mt: -0.5 }} />}
              <FormHelperText>{error?.message || ' '}</FormHelperText>
            </FormControl>
          )}
        />
      </WrapperComponent>
    );
  }

  if ('discriminator' in propertyJtd) {
    const discriminator = propertyJtd.discriminator;
    const discriminatorName = propertyJtd.metadata?.discriminatorName || discriminator;
    return (
      <SpreadInputWrapper label={!hiddenPropertyLabel ? propertyLabel : undefined} spread={propertySpread}>
        {!propertyJtd.metadata?.hiddenDiscriminator && (
          <WrapperComponent>
            <Controller
              name={`${propertyName}.${discriminator}`}
              control={control}
              rules={{
                required: propertyRequired && `${discriminatorName} is required.`,
              }}
              render={({ field: { value }, fieldState: { error } }) => (
                <FormControl
                  variant="outlined"
                  required={propertyRequired}
                  disabled={propertyReadonly}
                  fullWidth
                  error={!!error || isError}
                >
                  {propertyJtd.metadata?.customType === 'mappingBoolean' ? (
                    <FormControlLabel
                      label={discriminatorName}
                      disabled={!isEditing}
                      control={
                        <Switch
                          checked={value === 'true'}
                          onChange={(e) => {
                            const newDiscriminatorValue = String(e.target.checked);
                            const mappingProperty = propertyJtd.mapping[newDiscriminatorValue] as any;
                            if (!mappingProperty) {
                              console.error(`Can't find mapping property for "${newDiscriminatorValue}".`);
                              return;
                            }
                            const newProperties = {
                              [discriminator]: newDiscriminatorValue,
                              ...generateProperties(mappingProperty.properties, rootJtd),
                            };
                            setValue(propertyName, newProperties, { shouldDirty: true });
                          }}
                        />
                      }
                      sx={{ mt: -2 }}
                    />
                  ) : (
                    <>
                      <InputLabel id={`${propertyName}.${discriminator}`}>{discriminatorName}</InputLabel>
                      <Select
                        label={discriminatorName}
                        labelId={`${propertyName}.${discriminator}`}
                        inputProps={{ readOnly: !isEditing }}
                        value={value || ''}
                        onChange={(e) => {
                          const newDiscriminatorValue = e.target.value;
                          const newProperties = {
                            [discriminator]: newDiscriminatorValue,
                            ...generateProperties(
                              (propertyJtd.mapping[newDiscriminatorValue] as any).properties,
                              rootJtd
                            ),
                          };
                          setValue(propertyName, newProperties, { shouldDirty: true });
                        }}
                      >
                        {Object.keys(propertyJtd.mapping).map((v: string) => (
                          <MenuItem key={`${propertyKey}.${v}`} value={v}>
                            {v}
                          </MenuItem>
                        ))}
                      </Select>
                    </>
                  )}
                  {propertyJtd.metadata?.customType !== 'mappingBoolean' && (
                    <FormHelperText>{error?.message || ' '}</FormHelperText>
                  )}
                </FormControl>
              )}
            />
          </WrapperComponent>
        )}
        <Controller
          name={`${propertyName}.${discriminator}`}
          control={control}
          render={({ field: { value } }) => (
            <>
              {Object.entries((propertyJtd.mapping[value] as any).properties as Schema).map(
                ([nextPropertyKey, nextPropertyJtd]) => (
                  <PropertyInput
                    key={`${propertyKey}.${nextPropertyKey}`}
                    prefixPropertyName={prefixPropertyName}
                    propertyKey={propertyKey ? `${propertyKey}.${nextPropertyKey}` : nextPropertyKey}
                    propertyJtd={nextPropertyJtd}
                    rootJtd={rootJtd}
                    isEditing={isEditing}
                    isError={isError}
                  />
                )
              )}
            </>
          )}
        />
      </SpreadInputWrapper>
    );
  }

  if ('elements' in propertyJtd) {
    if ((propertyJtd.elements as any).type === 'string') {
      return (
        <Controller
          name={propertyName}
          control={control}
          rules={{
            required: propertyRequired && `${propertyLabel} is required.`,
          }}
          render={({ field: { value, onChange }, fieldState: { error } }) => (
            <Autocomplete
              multiple
              value={value}
              options={[]}
              fullWidth
              freeSolo
              disableClearable={!isEditing}
              disabled={propertyReadonly}
              onChange={(_, newValue) => onChange(newValue)}
              renderTags={(tagValue, getTagProps) =>
                tagValue.map((reference, index) => (
                  <Chip
                    label={reference}
                    {...getTagProps({ index })}
                    key={index}
                    onDelete={isEditing && !propertyReadonly ? getTagProps({ index }).onDelete : undefined}
                  />
                ))
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={propertyLabel}
                  required={propertyRequired}
                  error={!!error || isError}
                  helperText={error?.message || ' '}
                  inputProps={{
                    ...params.inputProps,
                    readOnly: !isEditing,
                  }}
                />
              )}
            />
          )}
        />
      );
    }
    return <ElementsPropertyInput {...props} />;
  }

  if ('type' in propertyJtd) {
    if (propertyJtd.type === 'boolean') {
      return (
        <WrapperComponent>
          <Controller
            name={propertyName}
            control={control}
            rules={{
              required: propertyRequired && `${propertyLabel} is required.`,
            }}
            render={({ field: { value, onChange }, fieldState: { error } }) => (
              <FormControl required={propertyRequired} error={!!error || isError}>
                <FormControlLabel
                  label={propertyLabel}
                  disabled={!isEditing}
                  control={<Switch checked={value} onChange={onChange} />}
                />
                <FormHelperText>{error?.message || ' '}</FormHelperText>
              </FormControl>
            )}
          />
        </WrapperComponent>
      );
    }
    const isNumber = !['string', 'timestamp'].includes(propertyJtd.type);
    return (
      <WrapperComponent>
        <Controller
          name={propertyName}
          control={control}
          rules={{
            required: propertyRequired && `${propertyLabel} is required.`,
          }}
          render={({ field: { value, onChange }, fieldState: { error } }) => (
            <TextField
              label={propertyLabel}
              type={propertyJtd.metadata?.customType === 'password' ? 'password' : isNumber ? 'number' : 'text'}
              multiline={propertyJtd.metadata?.customType === 'textarea'}
              required={propertyRequired}
              disabled={propertyReadonly}
              fullWidth
              error={!!error || isError}
              helperText={error?.message || ' '}
              InputProps={{
                readOnly: !isEditing,
              }}
              value={value}
              onChange={(e) => (isNumber ? onChange(Number(e.target.value)) : onChange(e.target.value))}
            />
          )}
        />
      </WrapperComponent>
    );
  }

  return <div>{propertyKey}</div>;
};

type SpreadInputWrapperProps = PropsWithChildren<{
  label?: string;
  spread?: boolean;
}>;

const SpreadInputWrapper: FC<SpreadInputWrapperProps> = ({ children, label, spread }) => {
  if (spread) {
    return (
      <>
        {label && (
          <WrapperComponent sx={{ mb: 2 }}>
            <Divider>
              <Typography variant="subtitle1">{label}</Typography>
            </Divider>
          </WrapperComponent>
        )}
        {children}
        {label && (
          <WrapperComponent>
            <Divider />
          </WrapperComponent>
        )}
      </>
    );
  }
  return (
    <WrapperComponent>
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Grid container rowSpacing={2} sx={{ mt: !label ? 0 : undefined }}>
          {label && (
            <WrapperComponent sx={{ mb: 2 }}>
              <Typography variant="subtitle1">{label}</Typography>
            </WrapperComponent>
          )}
          {children}
        </Grid>
      </Paper>
    </WrapperComponent>
  );
};

const ElementsPropertyInput: FC<PropertyInputProps> = ({
  prefixPropertyName = '',
  propertyKey,
  propertyJtd,
  rootJtd,
  isEditing,
  isError,
}) => {
  const { control } = useFormContext();
  const { fields, insert, remove } = useFieldArray({
    control,
    name: prefixPropertyName + propertyKey,
  });

  const propertyLabel = propertyJtd.metadata?.name || propertyKey;
  const propertySpread = propertyJtd.metadata?.spread;
  const hiddenPropertyLabel = propertyJtd.metadata?.hiddenLabel;
  const editableArray = propertyJtd.metadata?.editableArray !== false;
  const elementsJtd = (propertyJtd as any).elements;

  if (!elementsJtd) {
    console.error(`Property "${propertyKey}" is not an array.`);
    return <div>{propertyKey}</div>;
  }

  const insertProperty = (index: number) => {
    const newChildPropertyValue = generateProperty(elementsJtd, rootJtd);
    insert(index, newChildPropertyValue);
  };

  const removeProperty = (index: number) => remove(index);

  return (
    <SpreadInputWrapper label={!hiddenPropertyLabel ? propertyLabel : undefined} spread={propertySpread}>
      <Box component="div" sx={{ width: '100%' }}>
        {editableArray && (
          <IconButton
            size="small"
            color="primary"
            sx={{ display: 'flex', mx: 'auto' }}
            onClick={() => insertProperty(0)}
          >
            <Plus />
          </IconButton>
        )}
        {fields.map((field, i) => (
          <div key={field.id}>
            <WrapperComponent sx={{ display: 'flex', mt: 2 }}>
              <PropertyInput
                prefixPropertyName={prefixPropertyName}
                propertyKey={propertyKey ? `${propertyKey}.${i}` : String(i)}
                propertyJtd={elementsJtd}
                rootJtd={rootJtd}
                isEditing={isEditing}
                isError={isError}
              />
              {editableArray && (
                <IconButton size="small" color="error" sx={{ ml: 1, my: 'auto' }} onClick={() => removeProperty(i)}>
                  <Close />
                </IconButton>
              )}
            </WrapperComponent>
            {editableArray && (
              <IconButton
                size="small"
                color="primary"
                sx={{ display: 'flex', mx: 'auto' }}
                onClick={() => insertProperty(i + 1)}
              >
                <Plus />
              </IconButton>
            )}
          </div>
        ))}
      </Box>
    </SpreadInputWrapper>
  );
};
