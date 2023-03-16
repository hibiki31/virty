import { Box, IconButton, Link, Typography } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC, useState } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { tasksApi } from '~/lib/api';
import useSWR from 'swr';
import { formatDate } from '~/lib/utils/date';
import { CheckCircle, DotsVertical } from 'mdi-material-ui';
import { TASK_STATUS } from '~/lib/api/task';
import { useAuth } from '~/store/userState';
import { TaskSelect } from '~/lib/api/generated';
import { TaskDetailsDialog } from '~/components/dialogs/TaskDetailsDialog';
import NextLink from 'next/link';
import { ResourceIcon } from './ResourceIcon';

export const TasksTable: FC = () => {
  const { user } = useAuth();
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    ['tasksApi.getTasksApiTasksGet', user],
    ([, user]) => tasksApi.getTasksApiTasksGet(user?.isAdminMode).then((res) => res.data),
    { revalidateOnFocus: false }
  );
  const [selectedTask, setSelectedTask] = useState<TaskSelect | undefined>(undefined);

  if (error) {
    enqueueNotistack('Failed to fetch tasks.', { variant: 'error' });
  }

  return (
    <>
      <Box component="div" sx={{ height: '100%' }}>
        <DataGrid
          disableSelectionOnClick
          rowHeight={40}
          pageSize={25}
          getRowId={(row) => row.uuid!}
          rows={data || []}
          loading={!data || isValidating}
          error={!!error || undefined}
          columns={[
            {
              headerName: 'Status',
              field: 'status',
              disableColumnMenu: true,
              flex: 1,
              renderCell: (params) => (
                <>
                  <StatusIcon status={params.value} />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    {params.value}
                  </Typography>
                </>
              ),
            },
            {
              headerName: 'UUID',
              field: 'uuid',
              disableColumnMenu: true,
              flex: 2,
              renderCell: (params) => (
                <NextLink href={`/tasks/${params.value}`} passHref>
                  <Link>{params.value}</Link>
                </NextLink>
              ),
            },
            {
              headerName: 'Request',
              field: 'request',
              disableColumnMenu: true,
              flex: 1,
              minWidth: 150,
              valueGetter: (params) => `${params.row.method}.${params.row.resource}.${params.row.object}`,
              renderCell: (params) => (
                <>
                  <ResourceIcon method={params.row.method!} resource={params.row.resource!} />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    {params.value}
                  </Typography>
                </>
              ),
            },
            { headerName: 'User', field: 'userId', disableColumnMenu: true, flex: 1 },
            {
              headerName: 'PostTime',
              field: 'postTime',
              disableColumnMenu: true,
              flex: 1,
              minWidth: 160,
              renderCell: (params) => formatDate(params.row.postTime!),
            },
            {
              headerName: 'TunTime',
              field: 'runTime',
              disableColumnMenu: true,
              flex: 1,
              renderCell: (params) => `${Math.round(params.row.runTime! * 100) / 100} s`,
            },
            {
              headerName: '',
              field: 'details',
              disableColumnMenu: true,
              sortable: false,
              width: 40,
              align: 'center',
              renderCell: (params) => (
                <IconButton size="small" onClick={() => setSelectedTask(params.row)}>
                  <DotsVertical />
                </IconButton>
              ),
            },
          ]}
        />
      </Box>

      <TaskDetailsDialog open={!!selectedTask} task={selectedTask} onClose={() => setSelectedTask(undefined)} />
    </>
  );
};

type StatusIconProps = {
  status: string;
};

const StatusIcon: FC<StatusIconProps> = ({ status }) => {
  const color =
    status === TASK_STATUS.FINISH
      ? 'primary.main'
      : status === TASK_STATUS.INIT
      ? 'grey.500'
      : status === TASK_STATUS.ERROR
      ? 'error.main'
      : 'warning.main';
  return <CheckCircle sx={{ color }} />;
};
