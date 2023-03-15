import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddFlavorDialog } from '~/components/dialogs/AddFlavorDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { FlavorsTable } from '~/components/tables/FlavorsTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Flavor</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Flavor</Typography>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Add" DialogComponent={AddFlavorDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <FlavorsTable />
    </DefaultLayout>
  );
};

export default Page;
