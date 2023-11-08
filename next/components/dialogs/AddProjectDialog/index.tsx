import { Typography } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { projectApi, usersApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { useChoicesFetchers } from '~/store/formState';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddProjectDialog: FC<Props> = ({ open, onClose }) => {
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

  const handleAddProject = (data: FormData) => {
    return projectApi
      .createProject(data)
      .then(() => {
        enqueueNotistack('Project added successfully.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add the project.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Add Project"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddProject)}
    >
      <Typography variant="body2" sx={{ mb: 2 }}>
        Project names need not be unique. It is identified by a 6-digit code issued when the project is created.
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
    projectName: {
      metadata: {
        name: 'Name',
        default: '',
      },
      type: 'string',
    },
    userIds: {
      metadata: {
        name: 'Users',
        default: [],
        choices: 'users',
      },
      elements: {
        type: 'string',
      },
    },
  },
} as const;
