import { Chip } from '@mui/material';
import { FC } from 'react';
import { GetNetworkPoolPort } from '~/lib/api/generated';

type Props = {
  port: GetNetworkPoolPort;
};

export const PortChip: FC<Props> = ({ port }) => {
  return <Chip label={`${port.network.name}@${port.network.nodeName}#${port.name}`} size="small" sx={{ mr: 1 }} />;
};
