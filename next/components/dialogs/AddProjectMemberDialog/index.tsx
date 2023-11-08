import { Typography } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { FC, useCallback, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { usersApi } from '~/lib/api';
import { Project } from '~/lib/api/generated';
import { generateProperty } from '~/lib/jtd';
import { useChoicesFetchers } from '~/store/formState';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  project: Project;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddProjectMemberDialog: FC<Props> = ({ open, project, onClose }) => {
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

    setFetcher('users', () =>
      usersApi.getUsers().then((res) => res.data.map((user: any) => ({ label: user.username, value: user.username })))
    );
  }, [open, reset, resetFetchers, setFetcher]);

  const handleAddMember = useCallback((data: FormData) => {
    console.log('handleAddMember', data);
  }, []);

  return (
    <BaseDialog
      open={open}
      title="Add Member"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddMember)}
    >
      <Typography variant="body2" sx={{ mb: 2 }}>
        Add a member to the project {`"${project.name}"`}.
      </Typography>
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
    user: {
      metadata: {
        name: 'User',
        default: '',
        choices: 'users',
      },
      type: 'string',
    },
  },
} as const;
