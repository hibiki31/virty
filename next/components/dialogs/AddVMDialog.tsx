import { LoadingButton } from '@mui/lab';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, Grid } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { networkApi, nodeApi, storageApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useConfirmDialog } from '~/store/confirmDialogState';
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
    mode: 'onChange',
  });
  const {
    watch,
    reset,
    setValue,
    handleSubmit,
    formState: { isDirty, isValid, isSubmitting },
  } = formMethods;
  const { openConfirmDialog } = useConfirmDialog();

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
    setValue('form.spec.nodeName', '');
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
        case 'form.spec.nodeName':
          const nodeName = data.form?.spec?.nodeName;
          if (!nodeName) {
            return;
          }
          if (data.form?.storage?.type === 'copy') {
            setValue('form.storage.originalPoolUuid', '');
          }
          setValue('form.storage.savePoolUuid', '');
          setFetcher('storages', () =>
            storageApi
              .getApiStoragesApiStoragesGet()
              .then((res) =>
                res.data
                  .filter((storage) => storage.nodeName === nodeName)
                  .map((storage) => ({ value: storage.uuid, label: storage.name }))
              )
          );
          setValue('form.networks', [
            {
              type: 'network',
              network: '',
              port: '',
            },
          ]);
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
        case 'form.storage.type':
          if (data.form?.storage?.type !== 'copy') {
            setFetcher('images', () => Promise.resolve([]));
            return;
          }
          break;
        case 'form.storage.originalPoolUuid':
          const originalPoolUuid = (data.form?.storage as any)?.originalPoolUuid;
          setValue('form.storage.originalName', '');
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
      const networkUuid = data.form?.networks?.[Number(path[2])]?.network;
      if (path[1] === 'networks' && path[3] === 'network' && networkUuid) {
        const portName = (path.slice(0, 3).join('.') + '.port') as any;
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

  const handleAddVM = async (data: AddVMForm) => {
    const confirmed = await openConfirmDialog({
      description: 'Are you sure you want to add this VM?',
      submitText: 'Continue',
    });
    if (!confirmed) {
      return;
    }

    console.log('submit', data);
  };

  return (
    <Dialog maxWidth="sm" fullWidth open={open} onClose={!isDirty ? onClose : undefined}>
      <DialogTitle>
        <Grid container justifyContent="space-between" alignItems="center">
          <Grid item>Add VM</Grid>
        </Grid>
      </DialogTitle>
      <DialogContent sx={{ px: 1, pb: 0 }}>
        <FormProvider {...formMethods}>
          <JtdForm rootJtd={addVMFormJtd} isEditing />
        </FormProvider>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <LoadingButton
          onClick={handleSubmit(handleAddVM)}
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

const addVMFormJtd = {
  metadata: {
    spread: true,
  },
  properties: {
    form: {
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
                required: true,
              },
              type: 'string',
            },
            memoryMegaByte: {
              metadata: {
                name: 'Memory',
                default: '',
                required: true,
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
                required: true,
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
                required: true,
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
                    required: true,
                  },
                  type: 'float64',
                },
                savePoolUuid: {
                  metadata: {
                    name: 'Dest Pool',
                    default: '',
                    required: true,
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
                    required: true,
                    choices: 'storages',
                  },
                  type: 'string',
                },
                originalName: {
                  metadata: {
                    name: 'Src Image',
                    default: '',
                    required: true,
                    choices: 'images',
                  },
                  type: 'string',
                },
                savePoolUuid: {
                  metadata: {
                    name: 'Dest Pool',
                    default: '',
                    required: true,
                    choices: 'storages',
                  },
                  type: 'string',
                },
              },
            },
          },
        },
        networks: {
          metadata: {
            default: [
              {
                type: 'network',
                network: '',
                port: '',
              },
            ],
            spread: true,
            hiddenLabel: true,
          },
          elements: {
            metadata: {
              spread: true,
              hiddenLabel: true,
            },
            properties: {
              type: {
                metadata: {
                  name: 'Network Type',
                  default: 'network',
                  required: true,
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
                  required: true,
                  choices: 'networks',
                },
                type: 'string',
              },
              port: {
                metadata: {
                  name: 'Port',
                  default: '',
                  required: true,
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
              useCloudInit: 'false',
            },
          },
          discriminator: 'useCloudInit',
          mapping: {
            true: {
              properties: {
                hostname: {
                  metadata: {
                    name: 'Hostname',
                    default: (get: any) => get(2, 'spec.name'),
                    required: true,
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
                    required: true,
                    customType: 'textarea',
                  },
                  type: 'string',
                },
                networkConfig: {
                  metadata: {
                    name: 'Network Config',
                    default: 'network:\n  version: 2\n  ethernets: []',
                    required: true,
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
    },
  },
} as const;
