import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { JoinNodeDialog } from '~/components/dialogs/JoinNodeDialog';
import { NodeKeyDialog } from '~/components/dialogs/NodeKeyDialog';
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
        <Grid item>
          <OpenDialogButton label="Key" DialogComponent={NodeKeyDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
        <Grid item>
          <OpenDialogButton label="Join" DialogComponent={JoinNodeDialog} buttonProps={{ variant: 'contained' }} />
        </Grid>
      </Grid>

      <NodesTable />
    </DefaultLayout>
  );
};

export default Page;
