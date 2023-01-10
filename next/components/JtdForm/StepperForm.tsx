import { Button, Card, CardActions, CardContent, Step, StepLabel, Stepper } from '@mui/material';
import { Schema } from 'jtd';
import { nextTick } from 'process';
import { FC, useMemo, useState } from 'react';
import { Controller, useFormContext } from 'react-hook-form';
import { ajv } from '~/lib/jtd';
import { PropertyInput, PropertyInputProps } from './PropertyInput';

type Step = {
  name: string;
  title: string;
  props: PropertyInputProps;
};

export const StepperForm: FC<PropertyInputProps> = (props) => {
  const { prefixPropertyName = '', propertyKey, propertyJtd, rootJtd, isEditing, isError = false } = props;
  const {
    getValues,
    trigger,
    formState: { errors },
  } = useFormContext();

  const [activeStep, setActiveStep] = useState(0);
  const steps = useMemo<Step[]>(
    () =>
      !('properties' in propertyJtd)
        ? []
        : Object.entries(propertyJtd.properties as Schema).map(([nextPropertyKey, nextPropertyJtd]) => ({
            name: nextPropertyKey,
            title: nextPropertyJtd.metadata?.name || nextPropertyKey,
            props: {
              prefixPropertyName,
              propertyKey: propertyKey ? `${propertyKey}.${nextPropertyKey}` : nextPropertyKey,
              propertyJtd: nextPropertyJtd,
              rootJtd,
              isEditing,
              isError,
            },
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

  const moveNextStep = () => {
    trigger(propertyName);
    nextTick(() => {
      const path = propertyName.split('.');
      const formErrors = path.reduce((acc, key) => acc?.[key] as any, errors);
      if (!formErrors?.[steps[activeStep].name]) {
        setActiveStep(activeStep + 1);
      }
    });
  };

  return (
    <Card elevation={0} sx={{ width: '100%', backgroundColor: 'transparent' }}>
      <CardContent sx={{ pb: 0 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
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
              const validate = ajv.getSchema('JTD');
              if (!validate) {
                return 'Validator is not ready.';
              }
              validate(getValues());
              return !!validate.errors?.length ? `${propertyLabel} is invalid.` : activeStep === steps.length - 1;
            },
          }}
          render={() => <PropertyInput {...steps[activeStep].props} parentComponentName="StepperForm" />}
        />
      </CardContent>
      <CardActions>
        {activeStep > 0 && (
          <Button onClick={() => setActiveStep(activeStep - 1)} color="primary">
            Back
          </Button>
        )}
        {activeStep < steps.length - 1 && (
          <Button onClick={moveNextStep} color="primary" sx={{ ml: 'auto !important' }}>
            Next
          </Button>
        )}
      </CardActions>
    </Card>
  );
};
