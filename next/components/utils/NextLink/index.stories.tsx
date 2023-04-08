import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { NextLink } from '.';

export default {
  title: 'Utils/NextLink',
  component: NextLink,
} as ComponentMeta<typeof NextLink>;

export const Default: ComponentStoryObj<typeof NextLink> = {
  args: {
    pathname: '/test',
    children: 'test',
  },
};

export const WithoutUnderline: ComponentStoryObj<typeof NextLink> = {
  args: {
    pathname: '/test',
    underline: 'none',
    children: 'test',
  },
};

export const WithoutColor: ComponentStoryObj<typeof NextLink> = {
  args: {
    pathname: '/test',
    color: 'inherit',
    children: 'test',
  },
};
