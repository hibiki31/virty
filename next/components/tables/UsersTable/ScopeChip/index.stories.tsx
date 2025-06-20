import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { ScopeChip } from '.';

export default {
  title: 'Users/ScopeChip',
  component: ScopeChip,
} as ComponentMeta<typeof ScopeChip>;

export const Default: ComponentStoryObj<typeof ScopeChip> = {
  args: {
    scope: {
      name: 'user',
      user_id: 'user01',
    },
  },
};
