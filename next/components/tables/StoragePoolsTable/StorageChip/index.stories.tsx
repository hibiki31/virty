import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { StorageChip } from '.';

export default {
  title: 'Storage/StorageChip',
  component: StorageChip,
} as ComponentMeta<typeof StorageChip>;

export const Default: ComponentStoryObj<typeof StorageChip> = {
  args: {
    storage: {
      storage: {
        name: 'storage01',
        uuid: '550e8400-e29b-41d4-a716-446655440000',
        nodeName: 'node01',
      },
    },
  },
};
