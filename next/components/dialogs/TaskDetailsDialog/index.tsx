import { FC } from 'react';
import { BaseTable } from '~/components/tables/BaseTable';
import { Task } from '~/lib/api/generated';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  task?: Task;
  onClose: () => void;
};

export const TaskDetailsDialog: FC<Props> = ({ open, task, onClose }) => {
  if (!task) {
    return null;
  }

  return (
    <BaseDialog title="Task Details" maxWidth="md" open={open} onClose={onClose}>
      <BaseTable
        cols={[
          { name: 'Label', getItem: (item) => item.label },
          { name: 'Value', getItem: (item) => item.value },
        ]}
        items={[
          { label: 'UUID', value: task.uuid },
          { label: 'Message', value: task.message },
          { label: 'Request', value: <pre>{JSON.stringify(task.request, null, 2)}</pre> },
        ]}
        hiddenHeader
        disableElevation
      />
    </BaseDialog>
  );
};
