import { Chip, SvgIconProps } from '@mui/material';
import { Connection, Lan, Penguin } from 'mdi-material-ui';
import { FC } from 'react';
import { GetNodeRole } from '~/lib/api/generated';

type Props = {
  role: GetNodeRole;
};

export const RoleChip: FC<Props> = ({ role }) => {
  return <Chip icon={<RoleIcon roleName={role.roleName} fontSize="small" />} label={role.roleName} sx={{ mr: 1 }} />;
};

type RoleIconProps = {
  roleName: string;
} & SvgIconProps;

const RoleIcon: FC<RoleIconProps> = ({ roleName, ...props }) => {
  switch (roleName) {
    case 'ssh':
      return <Connection {...props} />;
    case 'libvirt':
      return <Penguin {...props} />;
    case 'ovs':
      return <Lan {...props} />;
  }
  return null;
};
