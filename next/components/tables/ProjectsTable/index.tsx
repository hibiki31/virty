import { Box } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { FC } from 'react';
import { useNotistack } from '~/lib/utils/notistack';
import { projectApi } from '~/lib/api';
import useSWR from 'swr';
import { useAuth } from '~/store/userState';
import { UserChip } from './UserChip';
import { UserBase } from '~/lib/api/generated';
import { OpenMenuButton } from '~/components/buttons/OpenMenuButton';
import { ProjectMenu } from '~/components/menus/ProjectMenu';
import { DotsVertical } from 'mdi-material-ui';

export const ProjectsTable: FC = () => {
  const { user } = useAuth();
  const { enqueueNotistack } = useNotistack();
  const { data, error, isValidating } = useSWR(
    ['projectApi.getProjects', user],
    ([, user]) => projectApi.getProjects(user?.isAdminMode).then((res) => res.data),
    { revalidateOnFocus: false }
  );

  if (error) {
    enqueueNotistack('Failed to fetch projects.', { variant: 'error' });
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
          { headerName: 'Name', field: 'name', disableColumnMenu: true, flex: 1, minWidth: 100 },
          {
            headerName: 'Users',
            field: 'users',
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
                {(params.value as UserBase[]).map((user, i) => (
                  <UserChip key={i} user={user} />
                ))}
              </Box>
            ),
          },
          {
            headerName: '',
            field: 'actions',
            disableColumnMenu: true,
            width: 40,
            align: 'center',
            renderCell: (params) => (
              <OpenMenuButton
                useIconButton
                label={<DotsVertical />}
                MenuComponent={ProjectMenu}
                menuProps={{ project: params.row }}
              />
            ),
          },
        ]}
      />
    </Box>
  );
};
