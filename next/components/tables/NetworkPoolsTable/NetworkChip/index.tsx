import { Chip } from '@mui/material';
import { FC } from 'react';
import { NetworkForNetworkPool } from '~/lib/api/generated';

type Props = {
  network: NetworkForNetworkPool;
};

export const NetworkChip: FC<Props> = ({ network }) => {
  return <Chip label={`${network.name}@${network.nodeName}`} size="small" sx={{ mr: 1 }} />;
};
