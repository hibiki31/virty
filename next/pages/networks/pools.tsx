import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddNetworkPoolDialog } from '~/components/dialogs/AddNetworkPoolDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NetworkPoolsTable } from '~/components/tables/NetworkPoolsTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Network Pools</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Network Pools</Typography>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Add" DialogComponent={AddNetworkPoolDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <NetworkPoolsTable />
    </DefaultLayout>
  );
};

export default Page;