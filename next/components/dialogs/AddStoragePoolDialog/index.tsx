import { JTDDataType } from 'ajv/dist/core';
import { FC, useCallback, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { storagesApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
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

  useEffect(() => {
    if (!open) {
      return;
    }
    reset();
    resetFetchers();

    setFetcher('storages', () =>
      storagesApi.getApiStoragesApiStoragesGet().then((res) =>
        res.data.map((storage) => ({
          label: storage.name,
          value: storage.name,
        }))
      )
    );
  }, [open, reset, resetFetchers, setFetcher]);

  const handleAddStoragePool = useCallback((data: FormData) => {
    console.log('handleAddStoragePool', data);
  }, []);

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
