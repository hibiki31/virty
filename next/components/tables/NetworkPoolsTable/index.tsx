import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { networkApi } from '~/lib/api';
import useSWR from 'swr';
import { PortChip } from './PortChip';
import { GetNEtworkPoolNetworksNetwork, GetNetworkPoolPort } from '~/lib/api/generated';
import { NetworkChip } from './NetworkChip';

export const NetworkPoolsTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'networkApi.getApiNetworksPoolsApiNetworksPoolsGet',
    () => networkApi.getApiNetworksPoolsApiNetworksPoolsGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch network pools.', { variant: 'error' });
  }

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
            renderCell: (params) =>
              (params.value as GetNEtworkPoolNetworksNetwork[]).map((network) => (
                <NetworkChip key={network.uuid} network={network} />
              )),
          },
          {
            headerName: 'Ports',
            field: 'ports',
            disableColumnMenu: true,
            flex: 2,
            minWidth: 150,
            renderCell: (params) =>
              (params.value as GetNetworkPoolPort[]).map((port, i) => <PortChip key={i} port={port} />),
          },
        ]}
      />
    </Box>
  );
};
