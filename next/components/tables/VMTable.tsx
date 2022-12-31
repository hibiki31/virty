import { Box, Link } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC, useEffect, useState } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { vmsApi } from '~/lib/api';
import { GetDomain } from '~/lib/api/generated';
import { Cpu64Bit, Memory, PowerStandby } from 'mdi-material-ui';
import NextLink from 'next/link';

export const VMTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const [vms, setVMs] = useState<GetDomain[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    vmsApi
      .getApiDomainApiVmsGet()
      .then((res) => {
        setVMs(res.data);
      })
      .catch(() => {
        setIsError(true);
        enqueueNotistack('Failed to fetch VMs.', { variant: 'error' });
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [enqueueNotistack]);

  return (
    <Box component="div" sx={{ height: 500 }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        getRowId={(row) => row.uuid}
        rows={vms}
        loading={isLoading}
        error={isError || undefined}
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
              <NextLink href={`#${params.value}`} passHref>
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
