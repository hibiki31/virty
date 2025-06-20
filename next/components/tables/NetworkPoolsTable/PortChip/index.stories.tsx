import { ComponentMeta } from '@storybook/react';
import { PortChip } from '.';

export default {
  title: 'Network/PortChip',
  component: PortChip,
} as ComponentMeta<typeof PortChip>;

export const Default = {
  args: {
    port: {
      name: 'ovs-vlan01',
      vlanId: 1,
      network: {
        name: 'ovs-network',
        uuid: '550e8400-e29b-41d4-a716-446655440000',
        nodeName: 'node01',
        bridge: 'ovs-br01',
        type: 'openvswitch',
      },
    },
  },
};
