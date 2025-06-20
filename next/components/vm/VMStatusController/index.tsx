import { Box, Grid, Tooltip } from '@mui/material';
import { DotsVertical } from 'mdi-material-ui';
import { FC, memo } from 'react';
import { VM_STATUS } from '~/lib/api/vm';
import { OpenMenuButton } from '../../buttons/OpenMenuButton';
import { VMStatusIcon } from '../VMStatusIcon';
import { PowerControlMenu } from './PowerControlMenu';

type VMStatusControllerProps = {
  uuid: string;
  status: number;
};

export const VMStatusController: FC<VMStatusControllerProps> = memo(function NotMemoVMStatusController({
  uuid,
  status,
}) {
  return (
    <Grid container alignItems="center">
      <Tooltip
        title={
          status === VM_STATUS.POWER_ON
            ? 'Power ON'
            : status === VM_STATUS.POWER_OFF
            ? 'Power OFF'
            : status === VM_STATUS.MAINTENANCE_MODE
            ? 'Maintenance mode'
            : status === VM_STATUS.DELETED_DOMAIN
            ? 'Deleted domain'
            : status === VM_STATUS.LOST_NODE
            ? 'Lost node'
            : `Unknown status code: ${status}`
        }
        placement="right"
      >
        <Box sx={{ mr: 1 }}>
          <VMStatusIcon status={status} />
        </Box>
      </Tooltip>
      <OpenMenuButton
        useIconButton
        label={<DotsVertical />}
        MenuComponent={PowerControlMenu}
        buttonProps={{ size: 'small' }}
        menuProps={{ uuid, status }}
      />
    </Grid>
  );
});
