import { Chip } from '@mui/material';
import { FC } from 'react';
import { StorageContainerForStoragePool } from '~/lib/api/generated';

type Props = {
  storage: StorageContainerForStoragePool;
};

export const StorageChip: FC<Props> = ({ storage }) => {
  return <Chip label={`${storage.storage.name}@${storage.storage.nodeName}`} size="small" sx={{ mr: 1 }} />;
};
