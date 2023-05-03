import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { tasksNodesApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const JoinNodeDialog: FC<Props> = ({ open, onClose }) => {
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

  const handleJoinNode = (data: FormData) => {
    return tasksNodesApi
      .postTasksNodesApiTasksNodesPost(data)
      .then(() => {
        enqueueNotistack('Please wait for the task to be completed.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add the task.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Join Node"
      submitText="Join"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleJoinNode)}
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
    userName: {
      metadata: {
        name: 'User',
        default: '',
      },
      type: 'string',
    },
    domain: {
      metadata: {
        name: 'IP or Domain',
        default: '',
      },
      type: 'string',
    },
    port: {
      metadata: {
        name: 'Port',
        default: '',
      },
      type: 'float64',
    },
    description: {
      metadata: {
        name: 'Description',
        customType: 'textarea',
        default: '',
      },
      type: 'string',
    },
    libvirtRole: {
      metadata: {
        name: 'Provisioning as kvm host',
        required: false,
        default: true,
      },
      type: 'boolean',
    },
  },
} as const;
