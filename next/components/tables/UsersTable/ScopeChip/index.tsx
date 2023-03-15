import { Chip } from '@mui/material';
import { FC } from 'react';

type Props = {
  scope: {
    name: string;
    user_id: string;
  };
};

export const ScopeChip: FC<Props> = ({ scope }) => {
  return <Chip label={scope.name} size="small" sx={{ mr: 1 }} />;
};
