import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddProjectDialog } from '~/components/dialogs/AddProjectDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { ProjectsTable } from '~/components/tables/ProjectsTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Projects</title>
      </Head>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Projects</Typography>
        </Grid>
        <Grid item>
          <OpenDialogButton label="Create" DialogComponent={AddProjectDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <ProjectsTable />
    </DefaultLayout>
  );
};

export default Page;
