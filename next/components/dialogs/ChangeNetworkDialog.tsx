import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { networkApi, tasksVmsApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { useChoicesFetchers } from '~/store/formState';
import { JtdForm } from '../JtdForm';
import { BaseDialog } from './BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
  vmUuid: string;
  macAddress?: string | null;
  nodeName: string;
};

type ChangeNetworkForm = JTDDataType<typeof changeNetworkFormJtd>;

export const ChangeNetworkDialog: FC<Props> = ({ open, onClose, vmUuid, macAddress, nodeName }) => {
  const { setFetcher, reset: resetFetchers } = useChoicesFetchers();
  const formMethods = useForm<ChangeNetworkForm>({
    defaultValues: generateProperty(changeNetworkFormJtd),
  });
  const {
    watch,
    reset,
    setValue,
    handleSubmit,
    formState: { isDirty, isValid, isSubmitting },
  } = formMethods;
  const [ovsNetworkUuids, setOvsNetworkUuids] = useState<string[]>([]);
  const { enqueueNotistack } = useNotistack();

  useEffect(() => {
    if (!open) {
      return;
    }
    reset();
    resetFetchers();
    setFetcher('networks', () =>
      networkApi.getNetworks(-1).then((res) => {
        const networks = res.data.data.filter((network) => network.nodeName === nodeName);
        setOvsNetworkUuids(networks.filter((network) => network.type === 'openvswitch').map((network) => network.uuid));
        return networks.map((network) => ({ value: network.uuid, label: network.name }));
      })
    );
  }, [open, reset, resetFetchers, setValue, setFetcher, nodeName]);

  useEffect(() => {
    watch((data, { name }) => {
      if (!name) {
        return;
      }
      switch (name) {
        case 'networkUuid':
          const networkUuid = data.networkUuid;
          if (!networkUuid) {
            return;
          }
          const isOvs = ovsNetworkUuids.includes(networkUuid);
          setValue('port.networkIsOvs', String(isOvs) as 'true' | 'false');
          setValue('port.value', '');
          if (!isOvs) {
            break;
          }
          setFetcher('', () => Promise.resolve([]));
          setFetcher(
            `ports-${networkUuid}`,
            () =>
              networkApi
                .getNetwork(networkUuid)
                .then((res) => res.data.portgroups.map((port) => ({ value: port.name, label: port.name }))),
            { useCache: true }
          );
          break;
      }
    });
  }, [watch, setValue, setFetcher, ovsNetworkUuids]);

  const handleChangeNetwork = async ({ networkUuid, port }: ChangeNetworkForm) => {
    if (!macAddress) {
      enqueueNotistack('MAC address is not specified.', { variant: 'error' });
      return;
    }
    return tasksVmsApi
      .updateVmNetwork(vmUuid, { mac: macAddress, networkUuid, port: (port as any).value })
      .then(() => {
        enqueueNotistack('Network changed successfully.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to change the network.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      title="Change Network"
      open={open}
      onClose={onClose}
      onSubmit={handleSubmit(handleChangeNetwork)}
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
    >
      <FormProvider {...formMethods}>
        <JtdForm rootJtd={changeNetworkFormJtd} isEditing />
      </FormProvider>
    </BaseDialog>
  );
};

const changeNetworkFormJtd = {
  metadata: {
    spread: true,
  },
  properties: {
    networkUuid: {
      metadata: {
        name: 'Network',
        default: '',
        required: true,
        choices: 'networks',
      },
      type: 'string',
    },
    port: {
      metadata: {
        customType: 'mappingBoolean',
        spread: true,
        hiddenDiscriminator: true,
        hiddenLabel: true,
        default: {
          networkIsOvs: 'false',
        },
      },
      discriminator: 'networkIsOvs',
      mapping: {
        true: {
          properties: {
            value: {
              metadata: {
                name: 'Port',
                default: '',
                required: true,
                choices: (get: any) => {
                  const network = get(2, 'networkUuid');
                  return network ? `ports-${network}` : '';
                },
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
  },
} as const;
