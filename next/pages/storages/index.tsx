import { Button, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddStorageDialog } from '~/components/dialogs/AddStorageDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { StoragesTable } from '~/components/tables/StoragesTable';
import { tasksImagesApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  const { enqueueNotistack } = useNotistack();

  const reloadStorages = () => {
    tasksImagesApi
      .putApiImagesApiTasksImagesPut()
      .then(() => enqueueNotistack('Storage list is being updated.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to update storage list.', { variant: 'error' }));
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Storages</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Storages</Typography>
        </Grid>
        <Grid item>
          <Button variant="contained" color="primary" onClick={reloadStorages}>
            Reload
          </Button>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Add" DialogComponent={AddStorageDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <StoragesTable />
    </DefaultLayout>
  );
};

export default Page;
