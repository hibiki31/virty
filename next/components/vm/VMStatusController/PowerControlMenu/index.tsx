import { FC } from 'react';
import { BaseMenu } from '~/components/menus/BaseMenu';
import { tasksVmsApi } from '~/lib/api';
import { VM_STATUS } from '~/lib/api/vm';
import { useNotistack } from '~/lib/utils/notistack';
import { useConfirmDialog } from '~/store/confirmDialogState';

type Props = {
  open: boolean;
  anchorEl: HTMLElement | null;
  uuid: string;
  status: number;
  onClose: () => void;
};

export const PowerControlMenu: FC<Props> = ({ open, anchorEl, uuid, status, onClose }) => {
  const { enqueueNotistack } = useNotistack();
  const { openConfirmDialog } = useConfirmDialog();

  const startVM = () => {
    tasksVmsApi
      .patchApiTasksVmsUuidPowerApiTasksVmsUuidPowerPatch(uuid, { status: 'on' })
      .then(() => enqueueNotistack('VM is starting.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to start VM.', { variant: 'error' }));
  };

  const stopVM = async () => {
    const confirmed = await openConfirmDialog({
      title: 'Stop VM',
      description: `Are you sure you want to stop VM "${uuid}"?`,
      submitText: 'Stop',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }
    tasksVmsApi
      .patchApiTasksVmsUuidPowerApiTasksVmsUuidPowerPatch(uuid, { status: 'off' })
      .then(() => enqueueNotistack('VM is stopping.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to stop VM.', { variant: 'error' }));
  };

  return (
    <BaseMenu
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      items={[
        {
          primary: 'Start',
          disabled: status === VM_STATUS.POWER_ON,
          onClick: startVM,
        },
        {
          primary: 'Stop',
          color: 'error',
          disabled: status === VM_STATUS.POWER_OFF,
          onClick: stopVM,
        },
      ]}
    />
  );
};
