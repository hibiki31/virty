import { Box, Grid, Tooltip } from '@mui/material';
import { AlertOutline, DeleteForever, DotsVertical, PowerStandby, ServerRemove, Wrench } from 'mdi-material-ui';
import { FC, memo } from 'react';
import { VM_STATUS } from '~/lib/api/vm';
import { OpenMenuButton } from '../buttons/OpenMenuButton';
import { PowerControlMenu } from './PowerControlMenu';

type Props = {
  statusCode: number;
};

export const VMStatusController: FC<Props> = memo(function NotMemoVMStatusController({ statusCode }) {
  return (
    <Grid container alignItems="center">
      <Tooltip
        title={
          statusCode === VM_STATUS.POWER_ON
            ? 'Power ON'
            : statusCode === VM_STATUS.POWER_OFF
            ? 'Power OFF'
            : statusCode === VM_STATUS.MAINTENANCE_MODE
            ? 'Maintenance mode'
            : statusCode === VM_STATUS.DELETED_DOMAIN
            ? 'Deleted domain'
            : statusCode === VM_STATUS.LOST_NODE
            ? 'Lost node'
            : `Unknown status code: ${statusCode}`
        }
        placement="right"
      >
        <Box
          sx={{
            mr: 1,
            '> *': {
              display: 'block !important',
            },
          }}
        >
          <StatusIcon statusCode={statusCode} />
        </Box>
      </Tooltip>
      <OpenMenuButton
        useIconButton
        label={<DotsVertical />}
        MenuComponent={PowerControlMenu}
        buttonProps={{ size: 'small' }}
      />
    </Grid>
  );
});

const StatusIcon: FC<Props> = ({ statusCode }) => {
  switch (statusCode) {
    case VM_STATUS.POWER_ON:
      return <PowerStandby color="primary" />;
    case VM_STATUS.POWER_OFF:
      return <PowerStandby color="disabled" />;
    case VM_STATUS.MAINTENANCE_MODE:
      return <Wrench color="secondary" />;
    case VM_STATUS.DELETED_DOMAIN:
      return <DeleteForever color="error" />;
    case VM_STATUS.LOST_NODE:
      return <ServerRemove color="secondary" />;
  }
  return <AlertOutline color="warning" />;
};
