import { ListItemText, Menu, MenuItem } from '@mui/material';
import { JTDDataType } from 'ajv/dist/core';
import { FC, useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { storageApi } from '~/lib/api';
import { GetDomainDrives } from '~/lib/api/generated';
import { generateProperty } from '~/lib/jtd';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { useChoicesFetchers } from '~/store/formState';
import { JtdForm } from '../JtdForm';
import { BaseDialog } from './BaseDialog';

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

  useEffect(() => {
    if (!changeImageOpen) {
      return;
    }
    reset();
    resetFetchers();
    setFetcher('images', () =>
      storageApi
        .getApiImagesApiImagesGet(nodeName, undefined, undefined, 'iso')
        .then((res) => res.data.map((image) => ({ value: image.path, label: image.name })))
    );
  }, [changeImageOpen, reset, resetFetchers, setValue, setFetcher, nodeName]);

  const handleMenuClick = (func: () => void) => () => {
    func();
    onClose();
  };

  const handleUnmount = async () => {
    const confirmed = await openConfirmDialog({
      description: `Are you sure you want to unmount this storage?\n\n${storage?.source}`,
      submitText: 'Continue',
    });
    if (!confirmed) {
      return;
    }

    console.log('unmount');
  };

  const handleChangeImage = async (data: ChangeImageForm) => {
    console.log('submit', data);
  };

  return (
    <>
      <Menu
        anchorEl={anchorEl}
        open={!!storage}
        onClose={onClose}
        transformOrigin={{ horizontal: 'left', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'left', vertical: 'bottom' }}
        sx={{ mt: 1, '& .MuiPaper-root': { minWidth: 200 } }}
      >
        <MenuItem onClick={handleMenuClick(handleUnmount)} disabled={!storage?.source}>
          <ListItemText primary="Unmount" primaryTypographyProps={{ color: 'error' }} />
        </MenuItem>
        <MenuItem onClick={handleMenuClick(() => setChangeImageOpen(true))}>
          <ListItemText primary="Change" />
        </MenuItem>
      </Menu>

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
    image: {
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
