import { Chip } from '@mui/material';
import { FC } from 'react';
import { UserBase } from '~/lib/api/generated';

type Props = {
  user: UserBase;
};

export const UserChip: FC<Props> = ({ user }) => {
  return <Chip label={user.id} size="small" sx={{ mr: 1 }} />;
};
