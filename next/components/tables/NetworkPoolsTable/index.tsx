import { Box, IconButton } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { networkApi } from '~/lib/api';
import useSWR from 'swr';
import { PortChip } from './PortChip';
import { NetworkForNetworkPool, NetworkPoolPort } from '~/lib/api/generated';
import { NetworkChip } from './NetworkChip';
import { Delete } from 'mdi-material-ui';
import { useConfirmDialog } from '~/store/confirmDialogState';

export const NetworkPoolsTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { openConfirmDialog } = useConfirmDialog();
  const { data, error, isValidating } = useSWR(
    'networkApi.getNetworkPools',
    () => networkApi.getNetworkPools().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch network pools.', { variant: 'error' });
  }

  const deleteNetworkPool = async (id: number) => {
    const confirmed = await openConfirmDialog({
      title: 'Delete Network Pool',
      description: `Are you sure you want to delete network pool "${id}"?`,
      submitText: 'Delete',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    console.log('delete network pool', id);
  };

  return (
    <Box sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        pageSize={25}
        getRowId={(row) => row.id!}
        rows={data || []}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          { headerName: 'ID', field: 'id', disableColumnMenu: true, flex: 1, minWidth: 80 },
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 2, minWidth: 150 },
          {
            headerName: 'Networks',
            field: 'networks',
            disableColumnMenu: true,
            flex: 2,
            minWidth: 150,
            renderCell: (params) => (
              <Box
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {(params.value as NetworkForNetworkPool[]).map((network) => (
                  <NetworkChip key={network.uuid} network={network} />
                ))}
              </Box>
            ),
          },
          {
            headerName: 'Ports',
            field: 'ports',
            disableColumnMenu: true,
            flex: 2,
            minWidth: 150,
            renderCell: (params) => (
              <Box
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {(params.value as NetworkPoolPort[]).map((port, i) => (
                  <PortChip key={i} port={port} />
                ))}
              </Box>
            ),
          },
          {
            headerName: '',
            field: 'actions',
            disableColumnMenu: true,
            width: 40,
            renderCell: (params) => (
              <IconButton size="small" color="error" onClick={() => deleteNetworkPool(params.row.id!)}>
                <Delete />
              </IconButton>
            ),
          },
        ]}
      />
    </Box>
  );
};
