import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { userApi } from '~/lib/api';
import useSWR from 'swr';
import { ScopeChip } from './ScopeChip';
import { GroupChip } from './GroupChip';

export const UsersTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    'userApi.getApiUsersApiUsersGet',
    () => userApi.getApiUsersApiUsersGet().then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch users.', { variant: 'error' });
  }

  return (
    <Box sx={{ height: '100%' }}>
      <DataGrid
        disableSelectionOnClick
        rowHeight={40}
        pageSize={25}
        getRowId={(row) => row.id}
        rows={data || []}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          { headerName: 'ID', field: 'id', disableColumnMenu: true, flex: 1, minWidth: 100 },
          {
            headerName: 'Scopes',
            field: 'scopes',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            renderCell: (params) => params.value.map((scope: any, i: number) => <ScopeChip key={i} scope={scope} />),
          },
          {
            headerName: 'Groups',
            field: 'projects',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            renderCell: (params) => params.value.map((group: any) => <GroupChip key={group.id} group={group} />),
          },
          { headerName: '', field: 'actions', disableColumnMenu: true, width: 40 },
        ]}
      />
    </Box>
  );
};
