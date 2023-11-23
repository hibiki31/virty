import { Box, IconButton, Link, Typography } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC, useState } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { tasksApi } from '~/lib/api';
import useSWR from 'swr';
import { formatDate } from '~/lib/utils/date';
import { DotsVertical } from 'mdi-material-ui';
import { useAuth } from '~/store/userState';
import { Task } from '~/lib/api/generated';
import { TaskDetailsDialog } from '~/components/dialogs/TaskDetailsDialog';
import NextLink from 'next/link';
import { ResourceIcon } from './ResourceIcon';
import { TaskStatusIcon } from './TaskStatusIcon';
import { useIncompleteTasks } from '~/store/tasksState';
import { FilterSettingsDrawer } from '~/components/utils/FilterSettingsDrawer';
import { JTDDataType } from 'ajv/dist/core';
import { generateProperty } from '~/lib/jtd';
import { usePagination } from '~/lib/utils/hooks';

type Filters = JTDDataType<typeof filtersJtd>;

export const TasksTable: FC = () => {
  const { user } = useAuth();
  const { enqueueNotistack } = useNotistack();
  const { hash } = useIncompleteTasks();
  const [filters, setFilters] = useState<Filters>(generateProperty(filtersJtd));
  const { page, limit, onPageChange, onLimitChange } = usePagination();
  const { data, error, isValidating } = useSWR(
    ['tasksApi.getTasks', user, hash, page, limit, filters],
    ([, u, _h, p, l, f]) =>
      tasksApi
        .getTasks(
          u?.isAdminMode,
          l,
          p,
          f.resource || undefined,
          f.object || undefined,
          f.method || undefined,
          f.status || undefined
        )
        .then((res) => res.data),
    { revalidateOnFocus: false }
  );
  const [selectedTask, setSelectedTask] = useState<Task | undefined>(undefined);

  const handleFiltersChange = (newFilters: Filters) => setFilters(newFilters);

  if (error) {
    enqueueNotistack('Failed to fetch tasks.', { variant: 'error' });
  }

  return (
    <>
      <Box component="div" sx={{ height: '100%' }}>
        <DataGrid
          disableSelectionOnClick
          rowHeight={40}
          page={page}
          pageSize={limit}
          paginationMode="server"
          onPageChange={onPageChange}
          onPageSizeChange={onLimitChange}
          getRowId={(row) => row.uuid!}
          rows={data?.data || []}
          rowCount={data?.count || 0}
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
                  <TaskStatusIcon status={params.value} />
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
              headerName: 'RunTime',
              field: 'runTime',
              disableColumnMenu: true,
              flex: 1,
              renderCell: (params) => (params.value ? `${Math.round(params.value! * 100) / 100} s` : '-'),
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

        <FilterSettingsDrawer filtersJtd={filtersJtd} onSubmit={handleFiltersChange} />
      </Box>

      <TaskDetailsDialog open={!!selectedTask} task={selectedTask} onClose={() => setSelectedTask(undefined)} />
    </>
  );
};

const filtersJtd = {
  properties: {
    status: {
      metadata: {
        name: 'Status',
        default: '',
        required: false,
        choices: [
          { label: 'Init', value: 'init' },
          { label: 'Start', value: 'start' },
          { label: 'Finish', value: 'finish' },
          { label: 'Wait', value: 'wait' },
          { label: 'Error', value: 'error' },
          { label: 'Lost', value: 'lost' },
        ],
      },
      type: 'string',
    },
    resource: {
      metadata: {
        name: 'Resource',
        default: '',
        required: false,
        choices: [
          { label: 'VM', value: 'vm' },
          { label: 'Node', value: 'node' },
          { label: 'Storage', value: 'storage' },
          { label: 'Network', value: 'network' },
        ],
      },
      type: 'string',
    },
    object: {
      metadata: {
        name: 'Object',
        default: '',
        required: false,
      },
      type: 'string',
    },
    method: {
      metadata: {
        name: 'Method',
        default: '',
        required: false,
        choices: [
          { label: 'POST', value: 'post' },
          { label: 'PUT', value: 'put' },
          { label: 'DELETE', value: 'delete' },
        ],
      },
      type: 'string',
    },
  },
} as const;
