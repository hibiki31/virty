import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { storageApi } from '~/lib/api';
import useSWR from 'swr';
import { GetStoragePoolStorages } from '~/lib/api/generated';
import { StorageChip } from './StorageChip';

export const StoragePoolsTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'storageApi.getApiStoragesPoolsApiStoragesPoolsGet',
    () => storageApi.getApiStoragesPoolsApiStoragesPoolsGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch storage pools.', { variant: 'error' });
  }
  console.log(data);

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
          { headerName: 'ID', field: 'id', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Node', field: 'name', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: 'Storages',
            field: 'storages',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 150,
            renderCell: (params) =>
              (params.value as GetStoragePoolStorages[]).map((storage, i) => <StorageChip key={i} storage={storage} />),
          },
        ]}
      />
    </Box>
  );
};
