import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { flavorsApi } from '~/lib/api';
import useSWR from 'swr';

export const FlavorsTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'flavorsApi.getApiFlavorsApiFlavorsGet',
    () => flavorsApi.getApiFlavorsApiFlavorsGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch flavors.', { variant: 'error' });
  }

  return (
    <Box sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        pageSize={25}
        getRowId={(row) => row.id}
        rows={data || []}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          { headerName: 'ID', field: 'id', disableColumnMenu: true, flex: 1, minWidth: 100 },
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 2, minWidth: 300 },
          { headerName: 'OS', field: 'os', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Manual URL', field: 'manualUrl', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Icon', field: 'icon', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Cloud Init Ready', field: 'cloudInitReady', disableColumnMenu: true, flex: 1, minWidth: 150 },
        ]}
      />
    </Box>
  );
};
