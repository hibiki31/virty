import { ComponentMeta } from '@storybook/react';
import { VMStatusController } from '.';

export default {
  title: 'VM/VMStatusController',
  component: VMStatusController,
} as ComponentMeta<typeof VMStatusController>;

export const On = {
  args: {
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    status: 1,
  },
};

export const Off = {
  args: {
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    status: 5,
  },
};

export const NodeIsMaintenanceMode = {
  args: {
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    status: 7,
  },
};

export const DeletedDomain = {
  args: {
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    status: 10,
  },
};

export const LostNode = {
  args: {
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    status: 20,
  },
};

export const Other = {
  args: {
    uuid: '550e8400-e29b-41d4-a716-446655440000',
    status: 0,
  },
};
