import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NodesTable } from '~/components/tables/NodesTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Node</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Node</Typography>
        </Grid>
      </Grid>

      <NodesTable />
    </DefaultLayout>
  );
};

export default Page;
