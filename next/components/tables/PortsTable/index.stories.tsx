import { Box } from '@mui/material';
import { ComponentMeta, Story } from '@storybook/react';
import { ComponentProps } from 'react';
import { PortsTable } from '.';

export default {
  title: 'Network/PortsTable',
  component: PortsTable,
} as ComponentMeta<typeof PortsTable>;

const Template: Story<ComponentProps<typeof PortsTable>> = (args) => (
  <Box sx={{ height: 'calc(100vh - 2rem)' }}>
    <PortsTable {...args} />
  </Box>
);

export const Default = Template.bind({});
Default.args = {
  ports: [
    {
      name: 'ovs-vlan01',
      vlanId: '1',
      isDefault: true,
    },
    {
      name: 'ovs-vlan02',
      vlanId: '2',
      isDefault: false,
    },
    {
      name: 'ovs-vlan03',
      vlanId: '3',
      isDefault: false,
    },
  ],
};
