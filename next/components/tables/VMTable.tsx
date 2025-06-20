import { Box, IconButton, Link, Typography } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC, useState } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { vmsApi } from '~/lib/api';
import { DotsVertical } from 'mdi-material-ui';
import NextLink from 'next/link';
import useSWR from 'swr';
import { VMStatusController } from '../vm/VMStatusController';
import { useAuth } from '~/store/userState';
import { FilterSettingsDrawer } from '../utils/FilterSettingsDrawer';
import { JTDDataType } from 'ajv/dist/core';
import { generateProperty } from '~/lib/jtd';
import { usePagination } from '~/lib/utils/hooks';

type Filters = JTDDataType<typeof filtersJtd>;

export const VMTable: FC = () => {
  const { user } = useAuth();
  const { enqueueNotistack } = useNotistack();
  const [filters, setFilters] = useState<Filters>(generateProperty(filtersJtd));
  const { page, limit, onPageChange, onLimitChange } = usePagination();
  const { data, error, isValidating } = useSWR(
    ['vmsApi.getVms', user, page, limit, filters],
    ([, u, p, l, f]) => vmsApi.getVms(l, p, u?.isAdminMode, f.name, f.nodeName).then((res) => res.data),
    { revalidateOnFocus: false }
  );

  const handleFiltersChange = (newFilters: Filters) => setFilters(newFilters);

  if (error) {
    enqueueNotistack('Failed to fetch VMs.', { variant: 'error' });
  }

  return (
    <Box component="div" sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        page={page}
        pageSize={limit}
        paginationMode="server"
        onPageChange={onPageChange}
        onPageSizeChange={onLimitChange}
        getRowId={(row) => row.uuid}
        rows={data?.data || []}
        rowCount={data?.count || 0}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          {
            headerName: 'Status',
            field: 'status',
            disableColumnMenu: true,
            renderCell: (params) => <VMStatusController uuid={params.row.uuid} status={params.value} />,
          },
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Node', field: 'nodeName', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: 'UUID',
            field: 'uuid',
            disableColumnMenu: true,
            flex: 2,
            minWidth: 290,
            renderCell: (params) => (
              <NextLink href={`/vms/${params.value}`} passHref>
                <Link>{params.value}</Link>
              </NextLink>
            ),
          },
          {
            headerName: 'RAM',
            field: 'memory',
            disableColumnMenu: true,
            align: 'right',
            flex: 1,
            minWidth: 80,
            renderCell: (params) => `${params.value / 1024} GB`,
          },
          {
            headerName: 'CPU',
            field: 'core',
            disableColumnMenu: true,
            align: 'right',
            flex: 1,
            minWidth: 80,
            renderCell: (params) => `${params.value} Core`,
          },
          {
            headerName: 'User',
            field: 'ownerUserId',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 150,
            renderCell: (params) => (
              <>
                <Typography variant="body2" sx={{ mr: 'auto' }}>
                  {params.value}
                </Typography>
                <IconButton size="small">
                  <DotsVertical />
                </IconButton>
              </>
            ),
          },
          {
            headerName: 'Group',
            field: 'ownerProjectId',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 150,
            renderCell: (params) => (
              <>
                <Typography variant="body2" sx={{ mr: 'auto' }}>
                  {params.value}
                </Typography>
                <IconButton size="small">
                  <DotsVertical />
                </IconButton>
              </>
            ),
          },
        ]}
      />

      <FilterSettingsDrawer filtersJtd={filtersJtd} onSubmit={handleFiltersChange} />
    </Box>
  );
};

const filtersJtd = {
  properties: {
    name: {
      metadata: {
        name: 'Name',
        default: '',
        required: false,
      },
      type: 'string',
    },
    nodeName: {
      metadata: {
        name: 'Node Name',
        default: '',
        required: false,
      },
      type: 'string',
    },
  },
} as const;
