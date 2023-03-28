import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { VMStatusIcon } from '.';

export default {
  title: 'VM/VMStatusIcon',
  component: VMStatusIcon,
} as ComponentMeta<typeof VMStatusIcon>;

export const On: ComponentStoryObj<typeof VMStatusIcon> = {
  args: {
    status: 1,
  },
};

export const Off: ComponentStoryObj<typeof VMStatusIcon> = {
  args: {
    status: 5,
  },
};

export const NodeIsMaintenanceMode: ComponentStoryObj<typeof VMStatusIcon> = {
  args: {
    status: 7,
  },
};

export const DeletedDomain: ComponentStoryObj<typeof VMStatusIcon> = {
  args: {
    status: 10,
  },
};

export const LostNode: ComponentStoryObj<typeof VMStatusIcon> = {
  args: {
    status: 20,
  },
};

export const Other: ComponentStoryObj<typeof VMStatusIcon> = {
  args: {
    status: 0,
  },
};
