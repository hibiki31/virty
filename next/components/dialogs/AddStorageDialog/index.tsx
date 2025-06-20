import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { nodesApi, tasksStoragesApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { useChoicesFetchers } from '~/store/formState';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const AddStorageDialog: FC<Props> = ({ open, onClose }) => {
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

    setFetcher('nodes', () =>
      nodesApi
        .getNodes(-1)
        .then((res) => res.data.data.map((node) => ({ label: `${node.name} - ${node.domain}`, value: node.name })))
    );
  }, [open, reset, resetFetchers, setFetcher]);

  const handleAddStorage = ({ node, ...rest }: FormData) => {
    return tasksStoragesApi
      .createStorage({ nodeName: node, ...rest })
      .then(() => {
        enqueueNotistack('Storage added successfully.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add the storage.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Add Storage"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddStorage)}
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
    node: {
      metadata: {
        name: 'Node',
        default: '',
        choices: 'nodes',
      },
      type: 'string',
    },
    path: {
      metadata: {
        name: 'Path',
        default: '',
      },
      type: 'string',
    },
  },
} as const;
