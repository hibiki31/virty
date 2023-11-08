import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { useSWRConfig } from 'swr';
import { JtdForm } from '~/components/JtdForm';
import { storagesApi } from '~/lib/api';
import { StorageMetadata } from '~/lib/api/generated';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  uuid: string;
  metadata?: StorageMetadata;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const ChangeStorageMetaDataDialog: FC<Props> = ({ open, uuid, metadata, onClose }) => {
  const formMethods = useForm<FormData>({
    defaultValues: generateProperty(formJtd),
  });
  const {
    reset,
    handleSubmit,
    formState: { isDirty, isValid, isSubmitting },
  } = formMethods;
  const { enqueueNotistack } = useNotistack();
  const { mutate } = useSWRConfig();

  useEffect(() => {
    if (!open) {
      return;
    }
    reset(metadata);
  }, [open, reset, metadata]);

  const handleChangeMetaData = (data: FormData) => {
    return storagesApi
      .updateStorageMetadata({ uuid, ...data })
      .then(() => {
        enqueueNotistack('Storage metadata changed.', { variant: 'success' });
        mutate(['storagesApi.getApiStoragesApiStoragesGet', uuid]);
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to change storage metadata.', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Change MetaData"
      submitText="Change"
      submitDisabled={!isValid || !isDirty}
      submitLoading={isSubmitting}
      persistent={isDirty}
      onClose={onClose}
      onSubmit={handleSubmit(handleChangeMetaData)}
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
    deviceType: {
      metadata: {
        name: 'Device Type',
        default: '',
        choices: [
          { label: 'NVME SSD', value: 'nvme' },
          { label: 'SATA SSD', value: 'ssd' },
          { label: 'HDD', value: 'hdd' },
          { label: 'Ohter', value: 'other' },
        ],
      },
      type: 'string',
    },
    protocol: {
      metadata: {
        name: 'Protocol',
        default: '',
        choices: [
          { label: 'Local', value: 'local' },
          { label: 'NFS', value: 'nfs' },
          { label: 'Ohter', value: 'other' },
        ],
      },
      type: 'string',
    },
    rool: {
      metadata: {
        name: 'Role',
        default: '',
        choices: [
          { label: 'VM Image', value: 'img' },
          { label: 'ISO installer', value: 'iso' },
          { label: 'Template Image', value: 'template' },
          { label: 'Cloud-init', value: 'init-iso' },
        ],
      },
      type: 'string',
    },
  },
} as const;
