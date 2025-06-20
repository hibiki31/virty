import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC, useMemo, useState } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { imagesApi, nodesApi, storagesApi } from '~/lib/api';
import useSWR from 'swr';
import { FilterSettingsDrawer } from '~/components/utils/FilterSettingsDrawer';
import { JTDDataType } from 'ajv/dist/core';
import { generateProperty } from '~/lib/jtd';
import { usePagination } from '~/lib/utils/hooks';
import { useAuth } from '~/store/userState';
type Filters = JTDDataType<typeof filtersJtd>;

export const ImagesTable: FC = () => {
  const { user } = useAuth();
  const { enqueueNotistack } = useNotistack();
  const [filters, setFilters] = useState<Filters>(generateProperty(filtersJtd));
  const { page, limit, onPageChange, onLimitChange } = usePagination();
  const { data, error, isValidating } = useSWR(
    ['imagesApi.getImages', filters, limit, page, user],
    ([_, f, l, p, u]) =>
      imagesApi
        .getImages(
          limit, 
          page,
          u?.isAdminMode,
          f.node || undefined, 
          f.poolUuid || undefined, 
          f.name || undefined, 
          f.rool || undefined
        )
        .then((res) => res.data),
    { revalidateOnFocus: false }
  );

  const handleFiltersChange = (newFilters: Filters) => setFilters(newFilters);

  const choicesFetchers = useMemo(
    () => ({
      nodes: () =>
        nodesApi.getNodes(-1).then((res) => res.data.data.map((node) => ({ label: node.name, value: node.name }))),
      pools: async () => {
        const results = await Promise.all([
          storagesApi.getStorages(-1).then((res) =>
            res.data.data.map((storage) => ({
              label: storage.name,
              value: storage.uuid,
            }))
          ),
          storagesApi.getStoragePools().then((res) =>
            res.data.map((storage) => ({
              label: storage.name,
              value: storage.id,
            }))
          ),
        ]);
        return results.flat();
      },
    }),
    []
  );

  if (error) {
    enqueueNotistack('Failed to fetch images.', { variant: 'error' });
  }

  return (
    <Box sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        page={page}
        pageSize={limit}
        paginationMode="server"
        onPageChange={onPageChange}
        onPageSizeChange={onLimitChange}
        getRowId={(row) => row.name}
        rows={data?.data || []}
        rowCount={data?.count || 0}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          {
            headerName: 'Name',
            field: 'name',
            disableColumnMenu: true,
            flex: 3,
            minWidth: 500,
          },
          {
            headerName: 'Node',
            field: 'storage.node.name',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 150,
            valueGetter: (params) => params.row.storage.node.name,
          },
          {
            headerName: 'Pool',
            field: 'storage.name',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 150,
            valueGetter: (params) => params.row.storage.name,
          },
          { headerName: 'Capacity', field: 'capacity', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Allocation', field: 'allocation', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: 'Domain Name',
            field: 'domain.name',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 150,
            valueGetter: (params) => params.row.domain?.name,
          },
          {
            headerName: 'Flavor Name',
            field: 'flavor.name',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 150,
            valueGetter: (params) => params.row.flavor?.name,
          },
          { headerName: 'Path', field: 'path', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: '',
            field: 'actions',
            disableColumnMenu: true,
            width: 40,
            align: 'center',
          },
        ]}
        disableColumnFilter
        disableColumnSelector
        disableDensitySelector
      />

      <FilterSettingsDrawer filtersJtd={filtersJtd} choicesFetchers={choicesFetchers} onSubmit={handleFiltersChange} />
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
    node: {
      metadata: {
        name: 'Node',
        default: '',
        required: false,
        choices: 'nodes',
      },
      type: 'string',
    },
    poolUuid: {
      metadata: {
        name: 'Pool',
        default: '',
        required: false,
        choices: 'pools',
      },
      type: 'string',
    },
    rool: {
      metadata: {
        name: 'Role',
        default: '',
        required: false,
        choices: [
          { label: 'VM Image', value: 'img' },
          { label: 'ISO installer', value: 'iso' },
          { label: 'Template Image', value: 'template' },
          { label: 'Cloud-init', value: 'init-iso' },
        ],
      },
      type: 'string',
    },
  },
} as const;
