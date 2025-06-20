import { Button } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddNetworkDialog } from '~/components/dialogs/AddNetworkDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NetworksTable } from '~/components/tables/NetworksTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { tasksNetworksApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  const { enqueueNotistack } = useNotistack();

  const reloadNetworks = () => {
    tasksNetworksApi
      .refreshNetworks()
      .then(() => enqueueNotistack('Network list is being updated.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to update network list.', { variant: 'error' }));
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Networks</title>
      </Head>

      <TitleHeader primary="Networks">
        <OpenDialogButton label="Add" DialogComponent={AddNetworkDialog} buttonProps={{ variant: 'contained' }} />
        <Button variant="contained" color="primary" onClick={reloadNetworks}>
          Reload
        </Button>
      </TitleHeader>

      <NetworksTable />
    </DefaultLayout>
  );
};

export default Page;
