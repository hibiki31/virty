import { Grid, IconButton, Typography, useMediaQuery, useTheme } from '@mui/material';
import { FilterSettings } from 'mdi-material-ui';
import type { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { ImagesTable } from '~/components/tables/ImagesTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useDrawer } from '~/store/drawerState';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  const theme = useTheme();
  const isMediumScreen = useMediaQuery(theme.breakpoints.down('md'));
  const { toggleRightDrawer } = useDrawer();

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Images</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Images</Typography>
        </Grid>
        {isMediumScreen && (
          <Grid item sx={{ ml: 'auto' }}>
            <IconButton onClick={toggleRightDrawer}>
              <FilterSettings />
            </IconButton>
          </Grid>
        )}
      </Grid>

      <ImagesTable />
    </DefaultLayout>
  );
};

export default Page;
