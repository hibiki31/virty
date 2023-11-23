import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { useSWRConfig } from 'swr';
import { JtdForm } from '~/components/JtdForm';
import { storagesApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { useChoicesFetchers } from '~/store/formState';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddStoragePoolDialog: FC<Props> = ({ open, onClose }) => {
  const { setFetcher, reset: resetFetchers } = useChoicesFetchers();
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
    if (!open) {
      return;
    }
    reset();
    resetFetchers();

    setFetcher('storages', () =>
      storagesApi.getStorages().then((res) =>
        res.data.map((storage) => ({
          label: storage.name,
          value: storage.name,
        }))
      )
    );
  }, [open, reset, resetFetchers, setFetcher]);

  const handleAddStoragePool = (data: FormData) => {
    return storagesApi
      .createStoragePool(data)
      .then(() => {
        enqueueNotistack('Storage pool added.', { variant: 'success' });
        mutate('storagesApi.getApiStoragesPoolsApiStoragesPoolsGet');
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add storage pool.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Add Storage Pool"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddStoragePool)}
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
    storageUuids: {
      metadata: {
        name: 'Storages',
        default: [],
        choices: 'storages',
      },
      elements: {
        type: 'string',
      },
    },
  },
} as const;
