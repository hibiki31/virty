import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { usersApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddUserDialog: FC<Props> = ({ open, onClose }) => {
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

  const handleAddUser = (data: FormData) => {
    return usersApi
      .createUser(data)
      .then(() => {
        enqueueNotistack('User added successfully.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add the user.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Add User"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddUser)}
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
    userId: {
      metadata: {
        name: 'ID',
        default: '',
      },
      type: 'string',
    },
    password: {
      metadata: {
        name: 'Password',
        default: '',
      },
      type: 'string',
    },
  },
} as const;
