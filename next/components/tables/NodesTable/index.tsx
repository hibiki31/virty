import { Box, IconButton } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { DotsVertical } from 'mdi-material-ui';
import { FC, useState } from 'react';
import useSWR from 'swr';
import { NodeDetailsDialog } from '~/components/dialogs/NodeDetailsDialog';
import { NextLink } from '~/components/utils/NextLink';
import { nodesApi } from '~/lib/api';
import { Node, NodeRole } from '~/lib/api/generated';
import { useNotistack } from '~/lib/utils/notistack';
import { RoleChip } from './RoleChip';

export const NodesTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR('nodesApi.getNodes', () => nodesApi.getNodes().then((res) => res.data), {
    revalidateOnFocus: false,
  });
  const [selectedNode, setSelectedNode] = useState<Node | undefined>(undefined);

  if (error) {
    enqueueNotistack('Failed to fetch nodes.', { variant: 'error' });
  }

  return (
    <>
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
            {
              headerName: 'Name',
              field: 'name',
              disableColumnMenu: true,
              flex: 1,
              minWidth: 150,
              renderCell: (params) => <NextLink pathname={`/nodes/${params.value}`}>{params.value}</NextLink>,
            },
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
                <Box
                  sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {(params.value as NodeRole[]).map((role, i) => (
                    <RoleChip key={i} role={role} />
                  ))}
                </Box>
              ),
            },
            {
              headerName: '',
              field: 'menu',
              disableColumnMenu: true,
              align: 'center',
              width: 40,
              renderCell: (params) => (
                <IconButton size="small" onClick={() => setSelectedNode(params.row)}>
                  <DotsVertical />
                </IconButton>
              ),
            },
          ]}
        />
      </Box>

      <NodeDetailsDialog open={!!selectedNode} node={selectedNode} onClose={() => setSelectedNode(undefined)} />
    </>
  );
};
