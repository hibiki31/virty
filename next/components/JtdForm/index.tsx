import { Grid } from '@mui/material';
import { Schema } from 'jtd';
import { FC, useEffect } from 'react';
import { useFormExtraData, useJtdForm } from '~/store/formState';
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
  const { resetExtraData } = useFormExtraData();

  useEffect(
    () => () => {
      reset();
      resetExtraData();
    },
    [reset, resetExtraData]
  );

  return (
    <Grid container rowSpacing={2}>
      <PropertyInput
        prefixPropertyName={prefixPropertyName}
        propertyKey=""
        propertyJtd={propertyJtd || rootJtd}
        rootJtd={rootJtd}
        isEditing={isEditing}
        isError={isError}
      />
    </Grid>
  );
};
