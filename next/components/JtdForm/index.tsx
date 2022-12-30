import { Grid } from '@mui/material';
import { Schema } from 'jtd';
import { FC, useEffect } from 'react';
import { useJtdForm } from '~/store/formState';
import { MetaData } from '~/lib/jtd/types';
import { PropertyInput } from './PropertyInput';

type Props = {
  prefixPropertyName?: string;
  propertyJtd?: Schema & { metadata?: MetaData };
  rootJtd: Schema & { metadata?: MetaData };
  isEditing: boolean;
  isError?: boolean;
};

export const JtdForm: FC<Props> = ({ prefixPropertyName, propertyJtd, rootJtd, isEditing, isError = false }) => {
  const { reset } = useJtdForm(rootJtd);
  const propertiesJtd: Schema = (propertyJtd as any)?.properties || (rootJtd as any).properties;

  useEffect(
    () => () => {
      reset();
    },
    [reset]
  );

  return (
    <Grid container rowSpacing={2}>
      {Object.entries(propertiesJtd).map(([propertyKey, jtd]) => (
        <PropertyInput
          key={propertyKey}
          prefixPropertyName={prefixPropertyName}
          propertyKey={propertyKey}
          propertyJtd={jtd}
          rootJtd={rootJtd}
          isEditing={isEditing}
          isError={isError}
        />
      ))}
    </Grid>
  );
};
