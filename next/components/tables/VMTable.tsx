import { Box, Link } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { vmsApi } from '~/lib/api';
import { Cpu64Bit, Memory, PowerStandby } from 'mdi-material-ui';
import NextLink from 'next/link';
import useSWR from 'swr';

const IS_ADMIN = true;

export const VMTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    ['vmsApi.getApiDomainApiVmsGet', IS_ADMIN],
    ([, isAdmin]) => vmsApi.getApiDomainApiVmsGet(isAdmin).then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch VMs.', { variant: 'error' });
  }

  return (
    <Box component="div" sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        getRowId={(row) => row.uuid}
        rows={data || []}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          {
            headerName: 'Status',
            field: 'status',
            disableColumnMenu: true,
            renderCell: (params) => <PowerStandby color={getStatusColor(params.value)} />,
          },
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 1 },
          { headerName: 'Node', field: 'nodeName', disableColumnMenu: true, flex: 1 },
          {
            headerName: 'UUID',
            field: 'uuid',
            disableColumnMenu: true,
            flex: 2,
            renderCell: (params) => (
              <NextLink href={`/vm/${params.value}`} passHref>
                <Link>{params.value}</Link>
              </NextLink>
            ),
          },
          {
            headerName: 'RAM',
            field: 'memory',
            disableColumnMenu: true,
            valueGetter: (params) => `${params.value / 1024} G`,
            renderCell: (params) => (
              <>
                <Memory sx={{ mr: 1 }} />
                {params.value}
              </>
            ),
          },
          {
            headerName: 'CPU',
            field: 'core',
            disableColumnMenu: true,
            renderCell: (params) => (
              <>
                <Cpu64Bit sx={{ mr: 1 }} />
                {params.value}
              </>
            ),
          },
          { headerName: 'User', field: 'ownerUserId', disableColumnMenu: true },
          { headerName: 'Group', field: 'ownerProject', disableColumnMenu: true },
        ]}
      />
    </Box>
  );
};

const getStatusColor = (statusCode: number) => {
  switch (statusCode) {
    case 1:
      return 'primary';
    case 5:
      return 'disabled';
    case 7:
      return 'secondary';
    case 10:
      return 'error';
    case 20:
      return 'secondary';
    default:
      return 'warning';
  }
};
