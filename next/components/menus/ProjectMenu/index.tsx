import { FC } from 'react';
import { ProjectSelect } from '~/lib/api/generated';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { BaseMenu } from '../BaseMenu';

type Props = {
  open?: boolean;
  anchorEl: HTMLElement | null;
  project: ProjectSelect;
  onClose: () => void;
};

export const ProjectMenu: FC<Props> = ({ open, anchorEl, project, onClose }) => {
  const { openConfirmDialog } = useConfirmDialog();

  const deleteProject = async () => {
    const confirmed = await openConfirmDialog({
      title: 'Delete Project',
      description: `Are you sure you want to delete the project "${project.name}"?\nAll associated VMs, images, networks, etc. will be deleted.`,
      submitText: 'Delete',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    console.log('delete project');
  };

  return (
    <BaseMenu
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      menuProps={{
        anchorOrigin: { vertical: 'bottom', horizontal: 'right' },
        transformOrigin: { vertical: 'top', horizontal: 'right' },
      }}
      items={[
        { primary: 'Add Member', onClick: () => {} },
        { primary: 'Delete', color: 'error', onClick: deleteProject },
      ]}
    />
  );
};
