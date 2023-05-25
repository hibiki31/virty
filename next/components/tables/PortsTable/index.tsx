import { IconButton } from '@mui/material';
import { Box } from '@mui/system';
import { DataGrid } from '@mui/x-data-grid';
import { CheckboxOutline, Delete } from 'mdi-material-ui';
import { FC } from 'react';
import { tasksNetworksApi } from '~/lib/api';
import { NetworkPortgroup } from '~/lib/api/generated';
import { useNotistack } from '~/lib/utils/notistack';
import { useConfirmDialog } from '~/store/confirmDialogState';

type Props = {
  networkUuid: string;
  ports: NetworkPortgroup[];
};

export const PortsTable: FC<Props> = ({ networkUuid, ports }) => {
  const { openConfirmDialog } = useConfirmDialog();
  const { enqueueNotistack } = useNotistack();

  const deletePort = async (name: string) => {
    const confirmed = await openConfirmDialog({
      title: 'Delete Port',
      description: `Are you sure you want to delete port "${name}"?\nData will remain and VM will not be affected.`,
      submitText: 'Delete',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    return tasksNetworksApi
      .postApiNetworksUuidOvsApiTasksNetworksUuidOvsNameDelete(networkUuid, name)
      .then(() => enqueueNotistack('Port deleted successfully.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to delete the port.', { variant: 'error' }));
  };

  return (
    <Box sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        autoHeight
        pageSize={25}
        getRowId={(row) => row.name}
        rows={ports}
        columns={[
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 1, minWidth: 150 },
          { headerName: 'VLAN ID', field: 'vlanId', disableColumnMenu: true, flex: 1, minWidth: 150 },
          {
            headerName: 'Default',
            field: 'isDefault',
            disableColumnMenu: true,
            width: 80,
            align: 'center',
            renderCell: (params) => {
              return params.value && <CheckboxOutline />;
            },
          },
          {
            headerName: '',
            field: 'actions',
            disableColumnMenu: true,
            width: 40,
            renderCell: (params) => (
              <IconButton size="small" color="error" onClick={() => deletePort(params.row.name)}>
                <Delete />
              </IconButton>
            ),
          },
        ]}
      />
    </Box>
  );
};
