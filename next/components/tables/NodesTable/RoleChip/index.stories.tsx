import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { RoleChip } from '.';

export default {
  title: 'Node/RoleChip',
  component: RoleChip,
} as ComponentMeta<typeof RoleChip>;

export const Ssh: ComponentStoryObj<typeof RoleChip> = {
  args: {
    role: {
      roleName: 'ssh',
      extraJson: {},
    },
  },
};

export const Libvirt: ComponentStoryObj<typeof RoleChip> = {
  args: {
    role: {
      roleName: 'libvirt',
      extraJson: {},
    },
  },
};

export const Ovs: ComponentStoryObj<typeof RoleChip> = {
  args: {
    role: {
      roleName: 'ovs',
      extraJson: {
        localIp: '192.168.0.1',
      },
    },
  },
};
