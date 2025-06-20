import { JTDDataType } from 'ajv/dist/core';
import { FC, useCallback, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { networkApi } from '~/lib/api';
import { Network } from '~/lib/api/generated';
import { generateProperty } from '~/lib/jtd';
import { useChoicesFetchers } from '~/store/formState';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  network: Network;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const JoinNetworkPoolDialog: FC<Props> = ({ open, network, onClose }) => {
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

    setFetcher('ports', async () =>
      network.portgroups.map((portgroup) => ({ label: portgroup.name, value: portgroup.name }))
    );
    setFetcher('pools', () =>
      networkApi
        .getNetworkPools()
        .then((res) => res.data.map((pool) => ({ label: pool.name!, value: String(pool.id) })))
    );
  }, [open, reset, resetFetchers, setFetcher, network]);

  const handleJoinNetworkPool = useCallback((data: FormData) => {
    console.log('handleJoinNetworkPool', data);
  }, []);

  return (
    <BaseDialog
      open={open}
      title="Join Network Pool"
      submitText="Join"
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleJoinNetworkPool)}
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
    portName: {
      metadata: {
        customType: 'mappingBoolean',
        discriminatorName: 'Select Port',
        default: {
          selectPort: 'true',
        },
        spread: true,
        hiddenLabel: true,
      },
      discriminator: 'selectPort',
      mapping: {
        true: {
          properties: {
            value: {
              metadata: {
                name: 'Port',
                default: '',
                choices: 'ports',
              },
              type: 'string',
            },
          },
        },
        false: {
          properties: {},
        },
      },
    },
    poolId: {
      metadata: {
        name: 'Pool',
        default: '',
        choices: 'pools',
      },
      type: 'string',
    },
  },
} as const;
