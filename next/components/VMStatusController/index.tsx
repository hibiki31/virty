import { PowerStandby } from 'mdi-material-ui';
import { FC } from 'react';

type Props = {
  statusCode: number;
};

export const VMStatusController: FC<Props> = ({ statusCode }) => {
  return <PowerStandby color={getStatusColor(statusCode)} sx={{ display: 'block' }} />;
};

const getStatusColor = (statusCode: number) => {
  switch (statusCode) {
    case 1:
      return 'primary';
    case 5:
      return 'disabled';
    case 7:
      return 'secondary';
    case 10:
      return 'error';
    case 20:
      return 'secondary';
    default:
      return 'warning';
  }
};
