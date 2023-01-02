import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const HomePage: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Home</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Home</Typography>
        </Grid>
      </Grid>
    </DefaultLayout>
  );
};

export default HomePage;
