import { ComponentMeta } from '@storybook/react';
import { VMStatusController } from '.';

export default {
  title: 'VM/VMStatusController',
  component: VMStatusController,
} as ComponentMeta<typeof VMStatusController>;

export const On = {
  args: {
    statusCode: 1,
  },
};

export const Off = {
  args: {
    statusCode: 5,
  },
};

export const NodeIsMaintenanceMode = {
  args: {
    statusCode: 7,
  },
};

export const DeletedDomain = {
  args: {
    statusCode: 10,
  },
};

export const LostNode = {
  args: {
    statusCode: 20,
  },
};

export const Other = {
  args: {
    statusCode: 0,
  },
};
