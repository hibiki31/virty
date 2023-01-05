import { Button, Card, CardActions, CardContent, FormHelperText, Step, StepLabel, Stepper } from '@mui/material';
import { Schema } from 'jtd';
import { FC, ReactNode, useMemo, useState } from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import { ajv } from '~/lib/jtd';
import { PropertyInput, PropertyInputProps } from './PropertyInput';

type Step = {
  title: string;
  body: ReactNode;
};

export const StepperForm: FC<PropertyInputProps> = (props) => {
  const { prefixPropertyName = '', propertyKey, propertyJtd, rootJtd, isEditing, isError = false } = props;
  const { getValues } = useFormContext();

  const [activeStep, setActiveStep] = useState(0);
  const steps = useMemo<Step[]>(
    () =>
      !('properties' in propertyJtd)
        ? []
        : Object.entries(propertyJtd.properties as Schema).map(([nextPropertyKey, nextPropertyJtd]) => ({
            title: nextPropertyJtd.metadata?.name || nextPropertyKey,
            body: (
              <PropertyInput
                key={propertyKey ? `${propertyKey}.${nextPropertyKey}` : nextPropertyKey}
                prefixPropertyName={prefixPropertyName}
                propertyKey={propertyKey ? `${propertyKey}.${nextPropertyKey}` : nextPropertyKey}
                propertyJtd={nextPropertyJtd}
                rootJtd={rootJtd}
                isEditing={isEditing}
                isError={isError}
              />
            ),
          })),
    [propertyKey, propertyJtd, rootJtd, isEditing, isError, prefixPropertyName]
  );

  if (steps.length === 0) {
    return null;
  }

  const propertyName = prefixPropertyName + propertyKey;
  const labelPath = propertyJtd.metadata?.labelPath;
  const labelFromName = propertyJtd.metadata?.name || propertyKey;
  const labelFromPath = labelPath?.length && labelPath.reduce((acc, key) => acc?.[key], getValues(propertyName));
  const propertyLabel = ['string', 'number'].includes(typeof labelFromPath) ? labelFromPath : labelFromName;

  return (
    <Card sx={{ width: '100%' }}>
      <CardContent>
        <Stepper activeStep={activeStep}>
          {steps.map((step, i) => (
            <Step key={i}>
              <StepLabel>{step.title}</StepLabel>
            </Step>
          ))}
        </Stepper>
        <Controller
          name={propertyName}
          rules={{
            validate: () => {
              return 'Validator is not ready.';
              const validate = ajv.getSchema('JTD');
              if (!validate) {
                return 'Validator is not ready.';
              }
              validate(getValues());
              console.log(getValues(), !!validate.errors?.length, validate.errors);
              return !!validate.errors?.length ? `${propertyLabel} is invalid.` : true;
            },
          }}
          render={({ fieldState: { error } }) => (
            <>
              {steps[activeStep].body}
              <FormHelperText error sx={{ mx: '14px' }}>
                {error?.message || ' '}
              </FormHelperText>
            </>
          )}
        />
      </CardContent>
      <CardActions>
        {activeStep > 0 && (
          <Button onClick={() => setActiveStep(activeStep - 1)} color="primary">
            Back
          </Button>
        )}
        {activeStep < steps.length - 1 && (
          <Button onClick={() => setActiveStep(activeStep + 1)} color="primary">
            Next
          </Button>
        )}
        {activeStep === steps.length - 1 && <Button color="primary">Submit</Button>}
      </CardActions>
    </Card>
  );
};
