import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { useSWRConfig } from 'swr';
import { JtdForm } from '~/components/JtdForm';
import { flavorsApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddFlavorDialog: FC<Props> = ({ open, onClose }) => {
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

  const handleAddFlavor = (data: FormData) => {
    return flavorsApi
      .createFlavor(data)
      .then(() => {
        enqueueNotistack('Flavor added.', { variant: 'success' });
        mutate('flavorsApi.getApiFlavorsApiFlavorsGet');
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add flavor.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Add Flavor"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddFlavor)}
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
        default: 'Ubuntu 20.04.4 LTS (Focal Fossa)',
      },
      type: 'string',
    },
    os: {
      metadata: {
        name: 'OS',
        default: 'Ubuntu 20.04 x64',
      },
      type: 'string',
    },
    manualUrl: {
      metadata: {
        name: 'Document URL',
        default: 'https://',
      },
      type: 'string',
    },
    icon: {
      metadata: {
        name: 'Icon',
        default: 'mdi-pentagon',
      },
      type: 'string',
    },
    description: {
      metadata: {
        name: 'Description',
        default: 'how to use',
      },
      type: 'string',
    },
    cloudInitReady: {
      metadata: {
        name: 'Cloud init ready',
        default: true,
        required: false,
      },
      type: 'boolean',
    },
  },
} as const;
