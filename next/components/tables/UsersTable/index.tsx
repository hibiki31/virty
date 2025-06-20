import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { usersApi } from '~/lib/api';
import useSWR from 'swr';
import { ScopeChip } from './ScopeChip';
import { GroupChip } from './GroupChip';
import { usePagination } from '~/lib/utils/hooks';

export const UsersTable: FC = () => {
  const { enqueueNotistack } = useNotistack();
  const { page, limit, onPageChange, onLimitChange } = usePagination();
  const { data, error, isValidating } = useSWR(
    ['usersApi.getUsers', limit, page],
    () => usersApi.getUsers(limit, page).then((res) => res.data),
    {
      revalidateOnFocus: false,
    }
  );

  if (error) {
    enqueueNotistack('Failed to fetch users.', { variant: 'error' });
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
        getRowId={(row) => row.username}
        rows={data?.data || []}
        rowCount={data?.count || 0}
        loading={!data || isValidating}
        error={!!error || undefined}
        columns={[
          { headerName: 'Username', field: 'username', disableColumnMenu: true, flex: 1, minWidth: 100 },
          {
            headerName: 'Scopes',
            field: 'scopes',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            renderCell: (params) => (
              <Box
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {params.value.map((scope: any, i: number) => (
                  <ScopeChip key={i} scope={scope} />
                ))}
              </Box>
            ),
          },
          {
            headerName: 'Groups',
            field: 'projects',
            disableColumnMenu: true,
            flex: 1,
            minWidth: 100,
            renderCell: (params) => (
              <Box
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {params.value.map((group: any) => (
                  <GroupChip key={group.id} group={group} />
                ))}
              </Box>
            ),
          },
          { headerName: '', field: 'actions', disableColumnMenu: true, width: 40 },
        ]}
      />
    </Box>
  );
};
