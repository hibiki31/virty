import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { JtdForm } from '~/components/JtdForm';
import { nodesApi } from '~/lib/api';
import { generateProperty } from '~/lib/jtd';
import { useNotistack } from '~/lib/utils/notistack';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  onClose: () => void;
};

type FormData = JTDDataType<typeof formJtd>;

export const NodeKeyDialog: FC<Props> = ({ open, onClose }) => {
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
    nodesApi
      .getSshKeyPairApiNodesKeyGet()
      .then((res) => {
        reset(res.data);
      })
      .catch(() => {
        enqueueNotistack('Failed to get SSH key pair', { variant: 'error' });
      });
  }, [open, reset, enqueueNotistack]);

  const handleUpdateKeys = (data: FormData) => {
    return nodesApi
      .postSshKeyPairApiNodesKeyPost(data)
      .then(() => {
        enqueueNotistack('SSH key pair updated', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to update SSH key pair', { variant: 'error' });
      });
  };

  return (
    <BaseDialog
      open={open}
      title="Update SSH Keys"
      submitDisabled={!isValid || !isDirty}
      submitLoading={isSubmitting}
      persistent={isDirty}
      maxWidth="md"
      onClose={onClose}
      onSubmit={handleSubmit(handleUpdateKeys)}
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
    privateKey: {
      metadata: {
        name: 'Key',
        customType: 'textarea',
      },
      type: 'string',
    },
    publicKey: {
      metadata: {
        name: 'Pub',
        customType: 'textarea',
      },
      type: 'string',
    },
  },
} as const;
