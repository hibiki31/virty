import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { TASK_STATUS } from '~/lib/api/task';
import { TaskStatusIcon } from '.';

export default {
  title: 'Tasks/TaskStatusIcon',
  component: TaskStatusIcon,
} as ComponentMeta<typeof TaskStatusIcon>;

export const Start: ComponentStoryObj<typeof TaskStatusIcon> = {
  args: {
    status: TASK_STATUS.START,
  },
};

export const Finish: ComponentStoryObj<typeof TaskStatusIcon> = {
  args: {
    status: TASK_STATUS.FINISH,
  },
};

export const Init: ComponentStoryObj<typeof TaskStatusIcon> = {
  args: {
    status: TASK_STATUS.INIT,
  },
};

export const Wait: ComponentStoryObj<typeof TaskStatusIcon> = {
  args: {
    status: TASK_STATUS.WAIT,
  },
};

export const Error: ComponentStoryObj<typeof TaskStatusIcon> = {
  args: {
    status: TASK_STATUS.ERROR,
  },
};

export const Lost: ComponentStoryObj<typeof TaskStatusIcon> = {
  args: {
    status: TASK_STATUS.LOST,
  },
};

export const Other: ComponentStoryObj<typeof TaskStatusIcon> = {
  args: {
    status: 'other',
  },
};
