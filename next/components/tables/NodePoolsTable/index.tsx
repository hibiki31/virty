import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import useSWR from 'swr';
import { nodeApi } from '~/lib/api';
import { useNotistack } from '~/lib/utils/notistack';

export const NodePoolsTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'nodeApi.getApiNodesPoolsApiNodesPoolsGet',
    () => nodeApi.getApiNodesPoolsApiNodesPoolsGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch node pools.', { variant: 'error' });
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
        columns={[{ headerName: 'ID', field: 'id', disableColumnMenu: true, flex: 1, minWidth: 80 }]}
      />
    </Box>
  );
};
