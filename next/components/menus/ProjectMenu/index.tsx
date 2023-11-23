import { FC } from 'react';
import { AddProjectMemberDialog } from '~/components/dialogs/AddProjectMemberDialog';
import { Project } from '~/lib/api/generated';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { BaseMenu } from '../BaseMenu';

type Props = {
  open?: boolean;
  anchorEl: HTMLElement | null;
  project: Project;
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
        {
          primary: 'Add Member',
          DialogComponent: AddProjectMemberDialog,
          dialogProps: { project },
        },
        { primary: 'Delete', color: 'error', onClick: deleteProject },
      ]}
    />
  );
};
