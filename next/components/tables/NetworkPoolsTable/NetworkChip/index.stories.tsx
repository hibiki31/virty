import { ComponentMeta } from '@storybook/react';
import { NetworkChip } from '.';

export default {
  title: 'Network/NetworkChip',
  component: NetworkChip,
} as ComponentMeta<typeof NetworkChip>;

export const Default = {
  args: {
    network: {
      name: 'ovs-network',
      uuid: '550e8400-e29b-41d4-a716-446655440000',
      nodeName: 'node01',
      bridge: 'ovs-br01',
      type: 'openvswitch',
    },
  },
};
