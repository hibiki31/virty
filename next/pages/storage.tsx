import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddStorageDialog } from '~/components/dialogs/AddStorageDialog';
import { AddStoragePoolDialog } from '~/components/dialogs/AddStoragePoolDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { StoragePoolsTable } from '~/components/tables/StoragePoolsTable';
import { StoragesTable } from '~/components/tables/StoragesTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Storage</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Storage</Typography>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Add" DialogComponent={AddStorageDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>
      <StoragesTable />

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Storage Pool</Typography>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Add" DialogComponent={AddStoragePoolDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>
      <StoragePoolsTable />
    </DefaultLayout>
  );
};

export default Page;
