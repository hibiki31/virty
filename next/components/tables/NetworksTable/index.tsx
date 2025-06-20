import { Box, Link } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { networkApi } from '~/lib/api';
import useSWR from 'swr';
import NextLink from 'next/link';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { ServerPlus } from 'mdi-material-ui';
import { JoinNetworkPoolDialog } from '~/components/dialogs/JoinNetworkPoolDialog';
import { usePagination } from '~/lib/utils/hooks';

export const NetworksTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { page, limit, onPageChange, onLimitChange } = usePagination();
  const { data, error, isValidating } = useSWR(
    ['networkApi.getNetworks', limit, page],
    () => networkApi.getNetworks(limit, page).then((res) => res.data),
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
        page={page}
        pageSize={limit}
        paginationMode="server"
        onPageChange={onPageChange}
        onPageSizeChange={onLimitChange}
        getRowId={(row) => row.uuid!}
        rows={data?.data || []}
        rowCount={data?.count || 0}
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
            renderCell: (params) => (
              <OpenDialogButton
                useIconButton
                label={<ServerPlus />}
                DialogComponent={JoinNetworkPoolDialog}
                buttonProps={{ size: 'small' }}
                dialogProps={{ network: params.row }}
              />
            ),
          },
        ]}
      />
    </Box>
  );
};
