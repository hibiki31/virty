import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddUserDialog } from '~/components/dialogs/AddUserDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { UsersTable } from '~/components/tables/UsersTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Users</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Users</Typography>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Add" DialogComponent={AddUserDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <UsersTable />
    </DefaultLayout>
  );
};

export default Page;
