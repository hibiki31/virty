import { Button, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddNetworkDialog } from '~/components/dialogs/AddNetworkDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NetworksTable } from '~/components/tables/NetworksTable';
import { networkApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  const { enqueueNotistack } = useNotistack();

  const reloadNetworks = () => {
    networkApi
      .putApiNetworksApiTasksNetworksPut()
      .then(() => enqueueNotistack('Network list is being updated.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to update network list.', { variant: 'error' }));
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Networks</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Networks</Typography>
        </Grid>
        <Grid item>
          <Button variant="contained" color="primary" onClick={reloadNetworks}>
            Reload
          </Button>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Add" DialogComponent={AddNetworkDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <NetworksTable />
    </DefaultLayout>
  );
};

export default Page;
