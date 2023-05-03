import { Button } from '@mui/material';
import { ComponentMeta, ComponentStoryObj } from '@storybook/react';
import { TitleHeader } from '.';

export default {
  title: 'Utils/TitleHeader',
  component: TitleHeader,
} as ComponentMeta<typeof TitleHeader>;

const Buttons = () => (
  <>
    <Button variant="contained">Button1</Button>
    <Button variant="contained">Button2</Button>
  </>
);

export const Primary: ComponentStoryObj<typeof TitleHeader> = {
  args: {
    primary: 'Primary',
  },
};

export const PrimaryWithChildren: ComponentStoryObj<typeof TitleHeader> = {
  args: {
    primary: 'Primary',
    children: <Buttons />,
  },
};

export const Secondary: ComponentStoryObj<typeof TitleHeader> = {
  args: {
    primary: 'Primary',
    secondary: 'Secondary',
  },
};

export const SecondaryWithChildren: ComponentStoryObj<typeof TitleHeader> = {
  args: {
    primary: 'Primary',
    secondary: 'Secondary',
    children: <Buttons />,
  },
};

export const Spacer: ComponentStoryObj<typeof TitleHeader> = {
  args: {
    primary: 'Primary',
    secondary: 'Secondary',
    spacer: true,
    children: <Buttons />,
  },
};
