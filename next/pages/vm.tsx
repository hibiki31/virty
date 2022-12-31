import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { VMTable } from '~/components/tables/VMTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const VMPage: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - VM</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">VM</Typography>
        </Grid>
      </Grid>

      <VMTable />
    </DefaultLayout>
  );
};

export default VMPage;
