import { Grid, IconButton, useMediaQuery, useTheme } from '@mui/material';
import { FilterSettings } from 'mdi-material-ui';
import type { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { ImagesTable } from '~/components/tables/ImagesTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
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

      <TitleHeader primary="Images">
        {isMediumScreen && (
          <Grid item sx={{ ml: 'auto' }}>
            <IconButton onClick={toggleRightDrawer}>
              <FilterSettings />
            </IconButton>
          </Grid>
        )}
      </TitleHeader>

      <ImagesTable />
    </DefaultLayout>
  );
};

export default Page;
