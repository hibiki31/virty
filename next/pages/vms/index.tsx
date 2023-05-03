import { Button, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { useState } from 'react';
import { AddVMDialog } from '~/components/dialogs/AddVMDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { VMTable } from '~/components/tables/VMTable';
import { tasksVmsApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';

export const getServerSideProps = makeRequireLoginProps();

const VMsPage: NextPage = () => {
  const [addVMDialogOpen, setAddVMDialogOpen] = useState<boolean>(false);
  const { enqueueNotistack } = useNotistack();

  const reloadVMs = () => {
    tasksVmsApi
      .publishTaskToUpdateVmListApiTasksVmsPut()
      .then(() => enqueueNotistack('VM list is being updated.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to update VM list.', { variant: 'error' }));
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - VMs</title>
      </Head>

      <AddVMDialog open={addVMDialogOpen} onClose={() => setAddVMDialogOpen(false)} />

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">VMs</Typography>
        </Grid>
        <Grid item>
          <Button variant="contained" color="primary" onClick={reloadVMs}>
            Reload
          </Button>
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

export default VMsPage;
