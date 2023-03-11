import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import useSWR from 'swr';
import { nodeApi } from '~/lib/api';
import { GetNodeRole } from '~/lib/api/generated';
import { useNotistack } from '~/lib/utils/notistack';
import { RoleChip } from './RoleChip';

export const NodesTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'nodeApi.getApiNodesApiNodesGet',
    () => nodeApi.getApiNodesApiNodesGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch nodes.', { variant: 'error' });
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
        columns={[
          { headerName: 'Status', field: 'status', disableColumnMenu: true, flex: 1, minWidth: 80 },
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'IP', field: 'domain', disableColumnMenu: true, flex: 2, minWidth: 150 },
          { headerName: 'Port', field: 'port', disableColumnMenu: true, align: 'right', flex: 1, minWidth: 80 },
          {
            headerName: 'RAM',
            field: 'memory',
            disableColumnMenu: true,
            align: 'right',
            flex: 1,
            minWidth: 80,
            renderCell: (params) => `${params.value} GB`,
          },
          {
            headerName: 'Core',
            field: 'core',
            disableColumnMenu: true,
            align: 'right',
            flex: 1,
            minWidth: 80,
            renderCell: (params) => `${params.value} Core`,
          },
          { headerName: 'CPU', field: 'cpuGen', disableColumnMenu: true, flex: 2, minWidth: 350 },
          { headerName: 'OS', field: 'osName', disableColumnMenu: true, flex: 1, minWidth: 80 },
          { headerName: 'QEMU', field: 'qemuVersion', disableColumnMenu: true, flex: 1, minWidth: 80 },
          { headerName: 'Libvirt', field: 'libvirtVersion', disableColumnMenu: true, flex: 1, minWidth: 80 },
          {
            headerName: 'Roles',
            field: 'roles',
            disableColumnMenu: true,
            flex: 2,
            minWidth: 200,
            renderCell: (params) => (
              <>
                {(params.value as GetNodeRole[]).map((role, i) => (
                  <RoleChip key={i} role={role} />
                ))}
              </>
            ),
          },
          { headerName: '', field: 'details', disableColumnMenu: true, flex: 1 },
        ]}
      />
    </Box>
  );
};
