import { Box, Grid, LinearProgress, Typography } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { storagesApi } from '~/lib/api';
import useSWR from 'swr';
import { CheckboxBlankOutline, CheckboxOutline } from 'mdi-material-ui';
import { NextLink } from '~/components/utils/NextLink';

export const StoragesTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'storagesApi.getStorages',
    () => storagesApi.getStorages().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch storages.', { variant: 'error' });
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
          { headerName: 'Node', field: 'nodeName', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: 'UUID',
            field: 'uuid',
            disableColumnMenu: true,
            flex: 2,
            minWidth: 290,
            renderCell: (params) => <NextLink pathname={`/storages/${params.value}`}>{params.value}</NextLink>,
          },
          {
            headerName: 'Capacity',
            field: 'capacity',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 80,
            align: 'right',
            renderCell: (params) => `${params.value} GB`,
          },
          {
            headerName: 'Used',
            field: 'used',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 80,
            align: 'right',
            valueGetter: (params) => params.row.capacity! - params.row.available!,
            renderCell: (params) => `${params.value} GB`,
          },
          {
            headerName: 'Available',
            field: 'available',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            valueGetter: (params) => ((params.row.capacity! - params.row.available!) / params.row.capacity!) * 100,
            renderCell: (params) => (
              <Grid container sx={{ width: '100%', height: '100%' }} alignItems="center" justifyContent="center">
                <Grid item sx={{ width: '100%', height: '50%' }}>
                  <LinearProgress variant="determinate" value={params.value} sx={{ height: '100%' }} />
                </Grid>
                <Grid item sx={{ position: 'absolute' }}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {params.row.available} GB
                  </Typography>
                </Grid>
              </Grid>
            ),
          },
          {
            headerName: 'Over Commit',
            field: 'overcommit',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 110,
            align: 'right',
            valueGetter: (params) => params.row.capacityCommit! - params.row.allocationCommit! - params.row.available!,
            renderCell: (params) => (
              <Typography variant="body2" color={params.value > 0 ? 'error' : 'primary'} sx={{ fontWeight: 'bold' }}>
                {params.value} GB
              </Typography>
            ),
          },
          {
            headerName: 'Active',
            field: 'active',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 70,
            align: 'center',
            renderCell: (params) => (params.value ? <CheckboxOutline /> : <CheckboxBlankOutline />),
          },
          {
            headerName: 'Auto',
            field: 'autoStart',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 70,
            align: 'center',
            renderCell: (params) => (params.value ? <CheckboxOutline /> : <CheckboxBlankOutline />),
          },
          { headerName: 'Path', field: 'path', disableColumnMenu: true, flex: 1, minWidth: 200 },
          {
            headerName: 'Device',
            field: 'metaData.deviceType',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            valueGetter: (params) => params.row.metaData?.deviceType,
          },
          {
            headerName: 'Protocol',
            field: 'metaData.protocol',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            valueGetter: (params) => params.row.metaData?.protocol,
          },
          {
            headerName: 'Rool',
            field: 'metaData.rool',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            valueGetter: (params) => params.row.metaData?.rool,
          },
          {
            headerName: '',
            field: 'joinPool',
            disableColumnMenu: true,
            width: 40,
            align: 'center',
          },
        ]}
      />
    </Box>
  );
};
