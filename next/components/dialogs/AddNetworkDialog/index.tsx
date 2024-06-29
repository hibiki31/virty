import { JTDDataType } from 'ajv/dist/core';
import { FC, useCallback, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { nodesApi, tasksNetworksApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { useChoicesFetchers } from '~/store/formState';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd> & {
  type: 'bridge' | 'ovs';
};

export const AddNetworkDialog: FC<Props> = ({ open, onClose }) => {
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

  const handleAddNetwork = useCallback(
    ({ node, ...rest }: FormData) => {
      return tasksNetworksApi
        .createNetwork({ nodeName: node, ...rest })
        .then(() => {
          enqueueNotistack('Network added successfully.', { variant: 'success' });
          onClose();
        })
        .catch(() => {
          enqueueNotistack('Failed to add the network.', { variant: 'error' });
        });
    },
    [enqueueNotistack, onClose]
  );

  return (
    <BaseDialog
      open={open}
      title="Add Network"
      submitText="Add"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleAddNetwork)}
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
    type: {
      metadata: {
        name: 'Type',
        default: 'bridge',
        choices: [
          { label: 'Linux bridge', value: 'bridge' },
          { label: 'Open vSwitch', value: 'ovs' },
        ],
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
    bridgeDevice: {
      metadata: {
        name: 'Bridge Name',
        default: '',
      },
      type: 'string',
    },
  },
} as const;
