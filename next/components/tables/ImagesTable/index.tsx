import { Box } from '@mui/material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { storageApi } from '~/lib/api';
import useSWR from 'swr';

export const ImagesTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'storageApi.getApiImagesApiImagesGet',
    () => storageApi.getApiImagesApiImagesGet().then((res) => res.data),
    { revalidateOnFocus: false }
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
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 3, minWidth: 500 },
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
    </Box>
  );
};
