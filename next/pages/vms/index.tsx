import { Button } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { useState } from 'react';
import { AddVMDialog } from '~/components/dialogs/AddVMDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { VMTable } from '~/components/tables/VMTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { tasksVmsApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';

export const getServerSideProps = makeRequireLoginProps();

const VMsPage: NextPage = () => {
  const [addVMDialogOpen, setAddVMDialogOpen] = useState<boolean>(false);
  const { enqueueNotistack } = useNotistack();

  const reloadVMs = () => {
    tasksVmsApi
      .refreshVms()
      .then(() => enqueueNotistack('VM list is being updated.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to update VM list.', { variant: 'error' }));
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - VMs</title>
      </Head>

      <AddVMDialog open={addVMDialogOpen} onClose={() => setAddVMDialogOpen(false)} />

      <TitleHeader primary="VMs">
        <Button variant="contained" color="primary" onClick={() => setAddVMDialogOpen(true)}>
          Add
        </Button>
        <Button variant="contained" color="primary" onClick={reloadVMs}>
          Reload
        </Button>
      </TitleHeader>

      <VMTable />
    </DefaultLayout>
  );
};

export default VMsPage;
