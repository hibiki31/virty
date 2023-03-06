import { LoadingButton } from '@mui/lab';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { networkApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useChoicesFetchers } from '~/store/formState';
import { JtdForm } from '../JtdForm';

type Props = {
  open: boolean;
  onClose: () => void;
  vmUuid: string;
  macAddress?: string;
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

  useEffect(() => {
    if (!open) {
      return;
    }
    reset();
    resetFetchers();
    setFetcher('networks', () =>
      networkApi.getApiNetworksApiNetworksGet().then((res) => {
        const networks = res.data.filter((network) => network.nodeName === nodeName);
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
        case 'network':
          const networkUuid = data.network;
          if (!networkUuid) {
            return;
          }
          setValue('port.networkIsOvs', String(ovsNetworkUuids.includes(networkUuid)) as 'true' | 'false');
          setValue('port.value', '');
          setFetcher('', () => Promise.resolve([]));
          setFetcher(
            `ports-${networkUuid}`,
            () =>
              networkApi
                .getApiNetworksUuidApiNetworksUuidGet(networkUuid)
                .then((res) => res.data.portgroups.map((port) => ({ value: port.name, label: port.name }))),
            { useCache: true }
          );
          break;
      }
    });
  }, [watch, setValue, setFetcher, ovsNetworkUuids]);

  const handleChangeNetwork = async (data: ChangeNetworkForm) => {
    console.log('submit', data);
  };

  return (
    <Dialog maxWidth="sm" fullWidth open={open} onClose={!isDirty ? onClose : undefined}>
      <DialogTitle>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item>Change Network</Grid>
        </Grid>
      </DialogTitle>
      <DialogContent sx={{ px: 1, pb: 0 }}>
        <FormProvider {...formMethods}>
          <JtdForm rootJtd={changeNetworkFormJtd} isEditing />
        </FormProvider>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <LoadingButton
          onClick={handleSubmit(handleChangeNetwork)}
          variant="contained"
          disableElevation
          disabled={!isValid}
          loading={isSubmitting}
        >
          Submit
        </LoadingButton>
      </DialogActions>
    </Dialog>
  );
};

const changeNetworkFormJtd = {
  properties: {
    network: {
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
                  const network = get(2, 'network');
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
