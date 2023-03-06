import { LoadingButton } from '@mui/lab';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { storageApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useChoicesFetchers } from '~/store/formState';
import { JtdForm } from '../JtdForm';

type Props = {
  open: boolean;
  onClose: () => void;
  vmUuid: string;
  target?: string;
  nodeName: string;
};

type ChangeCDRomForm = JTDDataType<typeof changeCDRomFormJtd>;

export const StorageDetailDialog: FC<Props> = ({ open, onClose, vmUuid, target, nodeName }) => {
  const { setFetcher, reset: resetFetchers } = useChoicesFetchers();
  const formMethods = useForm<ChangeCDRomForm>({
    defaultValues: generateProperty(changeCDRomFormJtd),
  });
  const {
    reset,
    setValue,
    handleSubmit,
    formState: { isDirty, isValid, isSubmitting },
  } = formMethods;

  useEffect(() => {
    if (!open) {
      return;
    }
    reset();
    resetFetchers();
    setFetcher('images', () =>
      storageApi
        .getApiImagesApiImagesGet(nodeName, undefined, undefined, 'iso')
        .then((res) => res.data.map((image) => ({ value: image.path, label: image.name })))
    );
  }, [open, reset, resetFetchers, setValue, setFetcher, nodeName]);

  const handleChangeCDRom = async (data: ChangeCDRomForm) => {
    console.log('submit', data);
  };

  return (
    <Dialog maxWidth="sm" fullWidth open={open} onClose={!isDirty ? onClose : undefined}>
      <DialogTitle>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item>Storage Detail</Grid>
        </Grid>
      </DialogTitle>
      <DialogContent sx={{ px: 1, pb: 0 }}>
        <FormProvider {...formMethods}>
          <JtdForm rootJtd={changeCDRomFormJtd} isEditing />
        </FormProvider>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <LoadingButton
          onClick={handleSubmit(handleChangeCDRom)}
          variant="contained"
          disableElevation
          disabled={!isValid}
          loading={isSubmitting}
        >
          Submit
        </LoadingButton>
      </DialogActions>
    </Dialog>
  );
};

const changeCDRomFormJtd = {
  properties: {
    image: {
      metadata: {
        name: 'Image',
        default: '',
        required: true,
        choices: 'images',
      },
      type: 'string',
    },
  },
} as const;
