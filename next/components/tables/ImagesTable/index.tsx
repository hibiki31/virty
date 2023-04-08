import { Box } from '@mui/material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import { FC, useMemo, useState } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { imagesApi, storagesApi } from '~/lib/api';
import useSWR from 'swr';
import { FilterSettingsDrawer } from '~/components/utils/FilterSettingsDrawer';
import { JTDDataType } from 'ajv/dist/core';
import { generateProperty } from '~/lib/jtd';

type Filters = JTDDataType<typeof filtersJtd>;

export const ImagesTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'imagesApi.getApiImagesApiImagesGet',
    () => imagesApi.getApiImagesApiImagesGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );
  const [filters, setFilters] = useState<Filters>(generateProperty(filtersJtd));

  const handleFiltersChange = (newFilters: Filters) => {
    console.log(newFilters);
    setFilters(newFilters);
  };

  const choicesFetchers = useMemo(
    () => ({
      pools: async () => {
        const results = await Promise.all([
          storagesApi.getApiStoragesApiStoragesGet().then((res) =>
            res.data.map((storage) => ({
              label: storage.name,
              value: storage.uuid,
            }))
          ),
          storagesApi.getApiStoragesPoolsApiStoragesPoolsGet().then((res) =>
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
        pageSize={25}
        getRowId={(row) => row.name}
        rows={data || []}
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
        components={{ Toolbar: GridToolbar }}
        componentsProps={{
          toolbar: {
            csvOptions: { disableToolbarButton: true },
            printOptions: { disableToolbarButton: true },
            showQuickFilter: true,
            quickFilterProps: { debounceMs: 500 },
          },
        }}
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
    nodeName: {
      metadata: {
        name: 'Node Name',
        default: '',
        required: false,
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
        name: 'Rool',
        default: '',
        required: false,
      },
      type: 'string',
    },
  },
} as const;
