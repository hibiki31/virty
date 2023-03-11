import { Box, Link } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { networkApi } from '~/lib/api';
import useSWR from 'swr';
import NextLink from 'next/link';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { ServerPlus } from 'mdi-material-ui';

export const NetworksTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'networkApi.getApiNetworksApiNetworksGet',
    () => networkApi.getApiNetworksApiNetworksGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch networks.', { variant: 'error' });
  }

  return (
    <Box sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        pageSize={25}
        getRowId={(row) => row.uuid!}
        rows={data || []}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Host Interface', field: 'hostInterface', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Node', field: 'nodeName', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'Type', field: 'type', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: 'UUID',
            field: 'uuid',
            disableColumnMenu: true,
            flex: 2,
            minWidth: 290,
            renderCell: (params) => (
              <NextLink href={`/networks/${params.value}`} passHref>
                <Link>{params.value}</Link>
              </NextLink>
            ),
          },
          { headerName: 'DHCP', field: 'dhcp', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: '',
            field: 'joinPool',
            disableColumnMenu: true,
            width: 40,
            align: 'center',
            renderCell: () => (
              <OpenDialogButton
                useIconButton
                label={<ServerPlus />}
                DialogComponent={() => <div />}
                buttonProps={{ size: 'small' }}
              />
            ),
          },
        ]}
      />
    </Box>
  );
};
