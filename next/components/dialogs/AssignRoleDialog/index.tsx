import { JTDDataType } from 'ajv/dist/core';
import { FC, useCallback, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { generateProperty } from '~/lib/jtd';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  nodeName: string;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AssignRoleDialog: FC<Props> = ({ open, nodeName, onClose }) => {
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

  const handleAsignRole = useCallback(
    (data: FormData) => {
      console.log('handleAsignRole', nodeName, data.role);
    },
    [nodeName]
  );

  return (
    <BaseDialog
      open={open}
      title="Assign Role"
      submitText="Assign"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAsignRole)}
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
    role: {
      metadata: {
        name: 'Role',
        choices: [
          { label: 'libvirt', value: 'libvirt' },
          { label: 'ovs', value: 'ovs' },
        ],
      },
      type: 'string',
    },
  },
} as const;
