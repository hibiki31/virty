import { AlertOutline, DeleteForever, PowerStandby, ServerRemove, Wrench } from 'mdi-material-ui';
import { FC } from 'react';
import { VM_STATUS } from '~/lib/api/vm';

type Props = {
  status: number;
};

export const VMStatusIcon: FC<Props> = ({ status }) => {
  const sx = { display: 'block' };

  switch (status) {
    case VM_STATUS.POWER_ON:
      return <PowerStandby color="primary" sx={sx} />;
    case VM_STATUS.POWER_OFF:
      return <PowerStandby color="disabled" sx={sx} />;
    case VM_STATUS.MAINTENANCE_MODE:
      return <Wrench color="secondary" sx={sx} />;
    case VM_STATUS.DELETED_DOMAIN:
      return <DeleteForever color="error" sx={sx} />;
    case VM_STATUS.LOST_NODE:
      return <ServerRemove color="secondary" sx={sx} />;
  }
  return <AlertOutline color="warning" sx={sx} />;
};
