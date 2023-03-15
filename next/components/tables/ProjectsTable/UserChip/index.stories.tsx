import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { UserChip } from '.';

export default {
  title: 'Projects/UserChip',
  component: UserChip,
} as ComponentMeta<typeof UserChip>;

export const Default: ComponentStoryObj<typeof UserChip> = {
  args: {
    user: {
      id: 'user01',
    },
  },
};
