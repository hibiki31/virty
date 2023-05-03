import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { imagesApi, vmsApi } from '~/lib/api';
import { GetDomainDrives } from '~/lib/api/generated';
import { generateProperty } from '~/lib/jtd';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { useChoicesFetchers } from '~/store/formState';
import { JtdForm } from '../JtdForm';
import { BaseDialog } from '../dialogs/BaseDialog';
import { BaseMenu } from './BaseMenu';
import { useNotistack } from '~/lib/utils/notistack';

type Props = {
  anchorEl: HTMLElement | null;
  onClose: () => void;
  vmUuid: string;
  storage?: GetDomainDrives;
  nodeName: string;
};

type ChangeImageForm = JTDDataType<typeof changeImageFormJtd>;

export const StorageActionsMenu: FC<Props> = ({ anchorEl, onClose, vmUuid, storage, nodeName }) => {
  const { setFetcher, reset: resetFetchers } = useChoicesFetchers();
  const formMethods = useForm<ChangeImageForm>({
    defaultValues: generateProperty(changeImageFormJtd),
  });
  const {
    reset,
    setValue,
    handleSubmit,
    formState: { isDirty, isValid, isSubmitting },
  } = formMethods;
  const [changeImageOpen, setChangeImageOpen] = useState(false);
  const { openConfirmDialog } = useConfirmDialog();
  const { enqueueNotistack } = useNotistack();

  useEffect(() => {
    if (!changeImageOpen) {
      return;
    }
    reset();
    resetFetchers();
    setFetcher('images', () =>
      imagesApi
        .getApiImagesApiImagesGet(nodeName, undefined, undefined, 'iso')
        .then((res) => res.data.map((image) => ({ value: image.path, label: image.name })))
    );
  }, [changeImageOpen, reset, resetFetchers, setValue, setFetcher, nodeName]);

  const handleUnmount = async () => {
    const confirmed = await openConfirmDialog({
      description: `Are you sure you want to unmount this storage?\n\n${storage?.source}`,
      submitText: 'Continue',
    });
    if (!confirmed) {
      return;
    }

    return vmsApi
      .patchApiTasksVmsUuidCdromApiTasksVmsUuidCdromPatch(vmUuid, { target: storage?.target })
      .then(() => {
        enqueueNotistack('CD-ROM unmounted successfully.', { variant: 'success' });
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to unmount the CD-ROM.', { variant: 'error' });
      });
  };

  const handleChangeImage = async (data: ChangeImageForm) => {
    return vmsApi
      .patchApiTasksVmsUuidCdromApiTasksVmsUuidCdromPatch(vmUuid, { target: storage?.target, ...data })
      .then(() => {
        enqueueNotistack('CD-ROM changed successfully.', { variant: 'success' });
        setChangeImageOpen(false);
        onClose();
      })
      .catch(() => {
        enqueueNotistack('Failed to change the CD-ROM.', { variant: 'error' });
      });
  };

  return (
    <>
      <BaseMenu
        open={!!anchorEl}
        anchorEl={anchorEl}
        onClose={onClose}
        menuProps={{
          transformOrigin: { horizontal: 'left', vertical: 'top' },
          anchorOrigin: { horizontal: 'left', vertical: 'bottom' },
        }}
        items={[
          {
            primary: 'Unmount',
            color: 'error',
            disabled: !storage?.source,
            onClick: handleUnmount,
          },
          {
            primary: 'Change',
            onClick: () => setChangeImageOpen(true),
          },
        ]}
      />

      <BaseDialog
        title="Change Image"
        open={changeImageOpen}
        onClose={() => setChangeImageOpen(false)}
        onSubmit={handleSubmit(handleChangeImage)}
        submitDisabled={!isValid}
        submitLoading={isSubmitting}
        persistent={isDirty}
      >
        <FormProvider {...formMethods}>
          <JtdForm rootJtd={changeImageFormJtd} isEditing />
        </FormProvider>
      </BaseDialog>
    </>
  );
};

const changeImageFormJtd = {
  metadata: {
    spread: true,
  },
  properties: {
    path: {
      metadata: {
        name: 'Image',
        default: '',
        required: true,
        choices: 'images',
      },
      type: 'string',
    },
  },
} as const;
