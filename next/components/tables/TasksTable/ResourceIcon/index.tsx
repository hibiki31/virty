import { CubeOutline, Database, HelpRhombus, Server, Wan } from 'mdi-material-ui';
import { FC } from 'react';
import { TASK_METHOD, TASK_RESOURCE } from '~/lib/api/task';

type Props = {
  method: string;
  resource: string;
};

export const ResourceIcon: FC<Props> = ({ method, resource }) => {
  const color =
    method === TASK_METHOD.POST
      ? 'success'
      : method === TASK_METHOD.PUT
      ? 'primary'
      : method === TASK_METHOD.DELETE
      ? 'error'
      : 'warning';
  switch (resource) {
    case TASK_RESOURCE.VM:
      return <CubeOutline color={color} />;
    case TASK_RESOURCE.NODE:
      return <Server color={color} />;
    case TASK_RESOURCE.STORAGE:
      return <Database color={color} />;
    case TASK_RESOURCE.NETWORK:
      return <Wan color={color} />;
  }
  return <HelpRhombus color={color} />;
};
