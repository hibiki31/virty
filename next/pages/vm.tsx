import { Button, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { useState } from 'react';
import { AddVMDialog } from '~/components/dialogs/AddVMDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { VMTable } from '~/components/tables/VMTable';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const VMPage: NextPage = () => {
  const [addVMDialogOpen, setAddVMDialogOpen] = useState<boolean>(false);

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - VM</title>
      </Head>

      <AddVMDialog open={addVMDialogOpen} onClose={() => setAddVMDialogOpen(false)} />

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">VM</Typography>
        </Grid>
        <Grid item>
          <Button variant="contained" color="primary" onClick={() => setAddVMDialogOpen(true)}>
            Add
          </Button>
        </Grid>
      </Grid>

      <VMTable />
    </DefaultLayout>
  );
};

export default VMPage;
