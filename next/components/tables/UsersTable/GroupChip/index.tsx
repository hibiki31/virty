import { Chip } from '@mui/material';
import { FC } from 'react';

type Props = {
  group: {
    id: string;
    name: string;
  };
};

export const GroupChip: FC<Props> = ({ group }) => {
  return <Chip label={group.name} size="small" sx={{ mr: 1 }} />;
};
