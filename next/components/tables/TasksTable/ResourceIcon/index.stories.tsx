import { ComponentMeta, Story } from '@storybook/react';
import { ComponentProps } from 'react';
import { TASK_METHOD, TASK_RESOURCE } from '~/lib/api/task';
import { ResourceIcon } from '.';
import { BaseTable } from '../../BaseTable';

type Props = {
  propsArray: ComponentProps<typeof ResourceIcon>[];
};

const Template: Story<Props> = ({ propsArray }) => (
  <BaseTable
    cols={propsArray.map((props, i) => ({
      name: props.method,
      getItem: (row: any) => <ResourceIcon {...row[i]} />,
    }))}
    items={[propsArray]}
  />
);

export default {
  title: 'Tasks/ResourceIcon',
  component: Template,
} as ComponentMeta<typeof ResourceIcon>;

export const VM = Template.bind({});
VM.args = {
  propsArray: [
    { method: TASK_METHOD.POST, resource: TASK_RESOURCE.VM },
    { method: TASK_METHOD.PUT, resource: TASK_RESOURCE.VM },
    { method: TASK_METHOD.DELETE, resource: TASK_RESOURCE.VM },
    { method: 'other', resource: TASK_RESOURCE.VM },
  ],
};

export const Node = Template.bind({});
Node.args = {
  propsArray: [
    { method: TASK_METHOD.POST, resource: TASK_RESOURCE.NODE },
    { method: TASK_METHOD.PUT, resource: TASK_RESOURCE.NODE },
    { method: TASK_METHOD.DELETE, resource: TASK_RESOURCE.NODE },
    { method: 'other', resource: TASK_RESOURCE.NODE },
  ],
};

export const Storage = Template.bind({});
Storage.args = {
  propsArray: [
    { method: TASK_METHOD.POST, resource: TASK_RESOURCE.STORAGE },
    { method: TASK_METHOD.PUT, resource: TASK_RESOURCE.STORAGE },
    { method: TASK_METHOD.DELETE, resource: TASK_RESOURCE.STORAGE },
    { method: 'other', resource: TASK_RESOURCE.STORAGE },
  ],
};

export const Network = Template.bind({});
Network.args = {
  propsArray: [
    { method: TASK_METHOD.POST, resource: TASK_RESOURCE.NETWORK },
    { method: TASK_METHOD.PUT, resource: TASK_RESOURCE.NETWORK },
    { method: TASK_METHOD.DELETE, resource: TASK_RESOURCE.NETWORK },
    { method: 'other', resource: TASK_RESOURCE.NETWORK },
  ],
};

export const Other = Template.bind({});
Other.args = {
  propsArray: [
    { method: TASK_METHOD.POST, resource: 'other' },
    { method: TASK_METHOD.PUT, resource: 'other' },
    { method: TASK_METHOD.DELETE, resource: 'other' },
    { method: 'other', resource: 'other' },
  ],
};
