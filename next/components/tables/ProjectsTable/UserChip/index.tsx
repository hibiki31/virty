import { Chip } from '@mui/material';
import { FC } from 'react';
import { ProjectUser } from '~/lib/api/generated';

type Props = {
  user: ProjectUser;
};

export const UserChip: FC<Props> = ({ user }) => {
  return <Chip label={user.username} size="small" sx={{ mr: 1 }} />;
};
