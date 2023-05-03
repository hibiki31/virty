import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { useSWRConfig } from 'swr';
import { JtdForm } from '~/components/JtdForm';
import { networkApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddNetworkPoolDialog: FC<Props> = ({ open, onClose }) => {
  const formMethods = useForm<FormData>({
    defaultValues: generateProperty(formJtd),
  });
  const {
    reset,
    handleSubmit,
    formState: { isDirty, isValid, isSubmitting },
  } = formMethods;
  const { enqueueNotistack } = useNotistack();
  const { mutate } = useSWRConfig();

  useEffect(() => {
    if (open) {
      reset();
    }
  }, [open, reset]);

  const handleAddNetworkPool = (data: FormData) => {
    return networkApi
      .postApiNetworksPoolsApiTasksNetworksPoolsPost(data)
      .then(() => {
        enqueueNotistack('Network pool added.', { variant: 'success' });
        mutate('networkApi.getApiNetworksPoolsApiNetworksPoolsGet');
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add network pool.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Add Network Pool"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddNetworkPool)}
    >
      <FormProvider {...formMethods}>
        <JtdForm rootJtd={formJtd} isEditing />
      </FormProvider>
    </BaseDialog>
  );
};

const formJtd = {
  metadata: {
    spread: true,
  },
  properties: {
    name: {
      metadata: {
        name: 'Name',
        default: '',
      },
      type: 'string',
    },
  },
} as const;
