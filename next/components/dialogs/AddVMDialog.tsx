import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { imagesApi, networkApi, nodesApi, storagesApi, tasksVmsApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { useChoicesFetchers } from '~/store/formState';
import { JtdForm } from '../JtdForm';
import { BaseDialog } from './BaseDialog';

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
  const { enqueueNotistack } = useNotistack();

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
      nodesApi.getNodes(-1).then((res) => res.data.data.map((node) => ({ value: node.name, label: node.name })))
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
            storagesApi
              .getStorages(-1)
              .then((res) =>
                res.data.data
                  .filter((storage) => storage.nodeName === nodeName)
                  .map((storage) => ({ value: storage.uuid, label: storage.name }))
              )
          );
          setValue('form.networks', [
            {
              type: 'network',
              networkUuid: '',
              port: '',
            },
          ]);
          setFetcher('networks', () =>
            networkApi.getNetworks(-1).then((res) =>
              res.data.data
                .filter((network) => network.nodeName === nodeName)
                .map((network) => ({
                  value: network.uuid,
                  label: network.name,
                  extraData: {
                    networkType: network.type,
                  },
                }))
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
            imagesApi
              .getImages(undefined, undefined, undefined, undefined, -1)
              .then((res) =>
                res.data.data
                  .filter((image) => image.storageUuid === originalPoolUuid)
                  .map((image) => ({ value: image.name, label: image.name }))
              )
          );
          break;
      }
      const path = name.split('.');
      const networkUuid = data.form?.networks?.[Number(path[2])]?.networkUuid;
      if (path[1] === 'networks' && path[3] === 'networkUuid' && networkUuid) {
        const portName = (path.slice(0, 3).join('.') + '.port') as any;
        setValue(portName, '');
        setFetcher('', () => Promise.resolve([]));
        setFetcher(
          `ports-${networkUuid}`,
          () =>
            networkApi
              .getNetwork(networkUuid)
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

    return tasksVmsApi
      .createVm({
        type: 'manual',
        ...data.form.spec,
        disks: [data.form.storage],
        interface: data.form.networks.map((network) => ({
          type: network.type,
          networkUuid: network.networkUuid,
          port: network.port === '' ? undefined : network.port,
        })),
        cloudInit:
          data.form.cloudInit.useCloudInit === 'true'
            ? {
                hostname: (data.form.cloudInit as any).hostname || '',
                userData: (data.form.cloudInit as any).userData || '',
              }
            : undefined,
      })
      .then(() => {
        enqueueNotistack('Please wait for the task to be completed.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to add the task.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      title="Add VM"
      open={open}
      submitDisabled={!isValid}
      submitLoading={isSubmitting}
      persistent={isDirty}
      disabledPadding
      onClose={onClose}
      onSubmit={handleSubmit(handleAddVM)}
    >
      <FormProvider {...formMethods}>
        <JtdForm rootJtd={addVMFormJtd} isEditing />
      </FormProvider>
    </BaseDialog>
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
                  { value: 512, label: '512 MB' },
                  { value: 1024, label: '1 GB' },
                  { value: 2048, label: '2 GB' },
                  { value: 4096, label: '4 GB' },
                  { value: 8192, label: '8 GB' },
                  { value: 16384, label: '16 GB' },
                  { value: 32768, label: '32 GB' },
                ],
              },
              type: 'float64',
            },
            cpu: {
              metadata: {
                name: 'CPU',
                default: '',
                required: true,
                choices: [
                  { value: 1, label: '1 Core' },
                  { value: 2, label: '2 Cores' },
                  { value: 4, label: '4 Cores' },
                  { value: 8, label: '8 Cores' },
                  { value: 12, label: '12 Cores' },
                  { value: 16, label: '16 Cores' },
                  { value: 24, label: '24 Cores' },
                ],
              },
              type: 'float64',
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
                sizeGigaByte: {
                  metadata: {
                    name: 'Size (GB)',
                    default: 32,
                    required: true,
                  },
                  type: 'float64',
                },
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
                  name: 'Port',
                  default: '',
                  hidden: (_: any, extraData: any) => extraData.networkType !== 'openvswitch',
                  choices: (get: any) => {
                    const networkUuid = get(1, 'networkUuid');
                    return networkUuid ? `ports-${networkUuid}` : '';
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
