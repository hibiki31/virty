import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { networkApi, nodeApi, storageApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useChoicesFetchers } from '~/store/formState';
import { JtdForm } from '../JtdForm';

type Props = {
  open: boolean;
  onClose: () => void;
};

type AddVMForm = JTDDataType<typeof addVMFormJtd>;

export const AddVMDialog: FC<Props> = ({ open, onClose }) => {
  const { setFetcher, reset: resetFetchers } = useChoicesFetchers();
  const formMethods = useForm<AddVMForm>({
    defaultValues: generateProperty(addVMFormJtd),
  });
  const { watch, reset, setValue } = formMethods;

  useEffect(() => {
    if (open) {
      reset();
      resetFetchers();
    }
  }, [open, reset, resetFetchers]);

  useEffect(() => {
    if (!open) {
      return;
    }
    setValue('spec.nodeName', '');
    setFetcher('nodes', () =>
      nodeApi.getApiNodesApiNodesGet().then((res) => res.data.map((node) => ({ value: node.name, label: node.name })))
    );
  }, [open, setValue, setFetcher]);

  useEffect(() => {
    watch((data, { name }) => {
      if (!name) {
        return;
      }
      switch (name) {
        case 'spec.nodeName':
          const nodeName = data.spec?.nodeName;
          if (!nodeName) {
            return;
          }
          setValue('storage.originalPoolUuid', '');
          setValue('storage.savePoolUuid', '');
          setFetcher('storages', () =>
            storageApi
              .getApiStoragesApiStoragesGet()
              .then((res) =>
                res.data
                  .filter((storage) => storage.nodeName === nodeName)
                  .map((storage) => ({ value: storage.uuid, label: storage.name }))
              )
          );
          setValue('networks', []);
          setFetcher('networks', () =>
            networkApi
              .getApiNetworksApiNetworksGet()
              .then((res) =>
                res.data
                  .filter((network) => network.nodeName === nodeName)
                  .map((network) => ({ value: network.uuid, label: network.name }))
              )
          );
          break;
        case 'storage.type':
          if (data.storage?.type !== 'copy') {
            setFetcher('images', () => Promise.resolve([]));
            return;
          }
          break;
        case 'storage.originalPoolUuid':
          const originalPoolUuid = (data.storage as any)?.originalPoolUuid;
          setValue('storage.originalName', '');
          setFetcher('images', () =>
            storageApi
              .getApiImagesApiImagesGet()
              .then((res) =>
                res.data
                  .filter((image) => image.storageUuid === originalPoolUuid)
                  .map((image) => ({ value: image.name, label: image.name }))
              )
          );
          break;
      }
      const path = name.split('.');
      const networkUuid = data.networks?.[Number(path[1])]?.network;
      if (path[0] === 'networks' && path[2] === 'network' && networkUuid) {
        const portName = (path.slice(0, 2).join('.') + '.port') as any;
        setValue(portName, '');
        setFetcher('', () => Promise.resolve([]));
        setFetcher(
          `ports-${networkUuid}`,
          () =>
            networkApi
              .getApiNetworksUuidApiNetworksUuidGet(networkUuid)
              .then((res) => res.data.portgroups.map((port) => ({ value: port.name, label: port.name }))),
          { useCache: true }
        );
      }
    });
  }, [watch, setValue, setFetcher]);

  const persistent = false;
  const handleSubmit = () => {
    console.log('submit');
  };

  return (
    <Dialog maxWidth="sm" fullWidth open={open} onClose={!persistent ? onClose : undefined}>
      <DialogTitle>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item>Add VM</Grid>
        </Grid>
      </DialogTitle>
      <DialogContent sx={{ pt: '10px !important' }}>
        <FormProvider {...formMethods}>
          <JtdForm rootJtd={addVMFormJtd} isEditing />
        </FormProvider>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disableElevation disabled={false}>
          Submit
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const addVMFormJtd = {
  metadata: {
    customType: 'stepper',
    spread: true,
  },
  properties: {
    spec: {
      properties: {
        name: {
          metadata: {
            name: 'Name',
            default: '',
          },
          type: 'string',
        },
        memoryMegaByte: {
          metadata: {
            name: 'Memory',
            default: '',
            choices: [
              { value: '512', label: '512 MB' },
              { value: '1024', label: '1 GB' },
              { value: '2048', label: '2 GB' },
              { value: '4096', label: '4 GB' },
              { value: '8192', label: '8 GB' },
              { value: '16384', label: '16 GB' },
              { value: '32768', label: '32 GB' },
            ],
          },
          type: 'string',
        },
        cpu: {
          metadata: {
            name: 'CPU',
            default: '',
            choices: [
              { value: '1', label: '1 Core' },
              { value: '2', label: '2 Cores' },
              { value: '4', label: '4 Cores' },
              { value: '8', label: '8 Cores' },
              { value: '12', label: '12 Cores' },
              { value: '16', label: '16 Cores' },
              { value: '24', label: '24 Cores' },
            ],
          },
        },
        nodeName: {
          metadata: {
            name: 'Node',
            default: '',
            choices: 'nodes',
          },
          type: 'string',
        },
      },
    },
    storage: {
      metadata: {
        discriminatorName: 'Storage Type',
        default: {
          type: 'empty',
        },
      },
      discriminator: 'type',
      mapping: {
        empty: {
          properties: {
            sizeGigaByte: {
              metadata: {
                name: 'Size (GB)',
                default: 32,
              },
              type: 'float64',
            },
            savePoolUuid: {
              metadata: {
                name: 'Dest Pool',
                default: '',
                choices: 'storages',
              },
              type: 'string',
            },
          },
        },
        copy: {
          properties: {
            originalPoolUuid: {
              metadata: {
                name: 'Src Pool',
                default: '',
                choices: 'storages',
              },
              type: 'string',
            },
            originalName: {
              metadata: {
                name: 'Src Image',
                default: '',
                choices: 'images',
              },
              type: 'string',
            },
            savePoolUuid: {
              metadata: {
                name: 'Dest Pool',
                default: '',
                choices: 'storages',
              },
              type: 'string',
            },
          },
        },
      },
    },
    networks: {
      elements: {
        properties: {
          type: {
            metadata: {
              name: 'Network Type',
              default: 'network',
              choices: [
                {
                  value: 'network',
                  label: 'Network',
                },
              ],
            },
            type: 'string',
          },
          network: {
            metadata: {
              name: 'Network',
              default: '',
              choices: 'networks',
            },
            type: 'string',
          },
          port: {
            metadata: {
              name: 'Port',
              default: '',
              hidden: (get: any) => !get(1, 'network'),
              choices: (get: any) => {
                const network = get(1, 'network');
                return network ? `ports-${network}` : '';
              },
            },
            type: 'string',
          },
        },
      },
    },
    cloudInit: {
      metadata: {
        customType: 'mappingBoolean',
        discriminatorName: 'Use cloud-init',
        default: {
          useCloudInit: false,
        },
      },
      discriminator: 'useCloudInit',
      mapping: {
        true: {
          properties: {
            hostname: {
              metadata: {
                name: 'Hostname',
                default: '',
              },
              type: 'string',
            },
            userData: {
              metadata: {
                name: 'User Data',
                default: `#cloud-config
password: password
chpasswd: {expire: False}
ssh_pwauth: True
ssh_authorized_keys:
  - ssh-rsa AAA...fHQ== sample@example.com`,
                customType: 'textarea',
              },
              type: 'string',
            },
            networkConfig: {
              metadata: {
                name: 'Network Config',
                default: 'network:\n  version: 2\n  ethernets: []',
                customType: 'textarea',
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
