import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddNetworkDialog } from '~/components/dialogs/AddNetworkDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NetworksTable } from '~/components/tables/NetworksTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
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
          <OpenDialogButton label="Add" DialogComponent={AddNetworkDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <NetworksTable />
    </DefaultLayout>
  );
};

export default Page;
