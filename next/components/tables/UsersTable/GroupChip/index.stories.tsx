import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { GroupChip } from '.';

export default {
  title: 'Users/GroupChip',
  component: GroupChip,
} as ComponentMeta<typeof GroupChip>;

export const Default: ComponentStoryObj<typeof GroupChip> = {
  args: {
    group: {
      id: '1',
      name: 'default',
    },
  },
};
