import { IconButton } from '@mui/material';
import { FlaskEmptyPlusOutline, ServerRemove } from 'mdi-material-ui';
import { FC, useCallback } from 'react';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { BaseTable } from '~/components/tables/BaseTable';
import { RoleChip } from '~/components/tables/NodesTable/RoleChip';
import { Node } from '~/lib/api/generated';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { AssignRoleDialog } from '../AssignRoleDialog';
import { BaseDialog } from '../BaseDialog';

type Props = {
  open: boolean;
  node?: Node['data'][0];
  onClose: () => void;
};

export const NodeDetailsDialog: FC<Props> = ({ open, node, onClose }) => {
  const { openConfirmDialog } = useConfirmDialog();

  const leaveNode = useCallback(async () => {
    const confirmed = await openConfirmDialog({
      title: 'Leave Node',
      description: 'Are you sure you want to leave this node?',
      submitText: 'Leave',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    console.log('leave node', node?.name);
  }, [openConfirmDialog, node]);

  if (!node) {
    return null;
  }

  return (
    <BaseDialog
      title="Node Details"
      headerActions={
        <IconButton onClick={leaveNode}>
          <ServerRemove color="error" />
        </IconButton>
      }
      maxWidth="md"
      open={open}
      onClose={onClose}
    >
      <BaseTable
        cols={[
          { name: 'Label', getItem: (item) => item.label },
          { name: 'Value', getItem: (item) => item.value },
        ]}
        items={[
          { label: 'Name', value: node.name },
          { label: 'Domain : Port', value: `${node.domain} : ${node.port}` },
          {
            label: 'Roles',
            value: (
              <>
                {node.roles.map((role, i) => (
                  <RoleChip key={i} role={role} />
                ))}
                <OpenDialogButton
                  useIconButton
                  label={<FlaskEmptyPlusOutline />}
                  DialogComponent={AssignRoleDialog}
                  dialogProps={{ nodeName: node.name }}
                />
              </>
            ),
          },
        ]}
        hiddenHeader
        disableElevation
      />
    </BaseDialog>
  );
};
