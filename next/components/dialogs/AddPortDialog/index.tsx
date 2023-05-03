import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { tasksNetworksApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  networkUuid: string;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddPortDialog: FC<Props> = ({ open, networkUuid, onClose }) => {
  const formMethods = useForm<FormData>({
    defaultValues: generateProperty(formJtd),
  });
  const {
    reset,
    handleSubmit,
    formState: { isDirty, isValid, isSubmitting },
  } = formMethods;
  const { enqueueNotistack } = useNotistack();

  useEffect(() => {
    if (open) {
      reset();
    }
  }, [open, reset]);

  const handleAddPort = (data: FormData) => {
    return tasksNetworksApi
      .postApiNetworksUuidOvsApiTasksNetworksOvsPost({ uuid: networkUuid, ...data })
      .then(() => {
        enqueueNotistack('Port added successfully.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add the port.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Add Port"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddPort)}
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
    vlanId: {
      metadata: {
        name: 'VLAN ID',
        default: '',
      },
      type: 'float64',
    },
    default: {
      metadata: {
        name: 'Change to default',
        default: false,
        required: false,
      },
      type: 'boolean',
    },
  },
} as const;
