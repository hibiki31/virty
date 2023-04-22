import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { IncompleteTasksButton } from '.';

export default {
  title: 'Layouts/IncompleteTasksButton',
  component: IncompleteTasksButton,
} as ComponentMeta<typeof IncompleteTasksButton>;

export const Zero: ComponentStoryObj<typeof IncompleteTasksButton> = {
  args: {
    count: 0,
  },
};

export const OneDigit: ComponentStoryObj<typeof IncompleteTasksButton> = {
  args: {
    count: 1,
  },
};

export const TwoDigits: ComponentStoryObj<typeof IncompleteTasksButton> = {
  args: {
    count: 10,
  },
};

export const OverLimit: ComponentStoryObj<typeof IncompleteTasksButton> = {
  args: {
    count: 100,
  },
};
