import { JTDDataType } from 'ajv/dist/core';
import { FC, useCallback, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { generateProperty } from '~/lib/jtd';
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

  useEffect(() => {
    if (open) {
      reset();
    }
  }, [open, reset]);

  const handleJoinNode = useCallback((data: FormData) => {
    console.log('handleJoinNode', data);
  }, []);

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
        default: false,
      },
      type: 'boolean',
    },
  },
} as const;
