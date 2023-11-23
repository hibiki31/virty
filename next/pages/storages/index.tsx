import { Button } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddStorageDialog } from '~/components/dialogs/AddStorageDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { StoragesTable } from '~/components/tables/StoragesTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { tasksImagesApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  const { enqueueNotistack } = useNotistack();

  const reloadStorages = () => {
    tasksImagesApi
      .refreshImages()
      .then(() => enqueueNotistack('Storage list is being updated.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to update storage list.', { variant: 'error' }));
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Storages</title>
      </Head>

      <TitleHeader primary="Storages">
        <OpenDialogButton label="Add" DialogComponent={AddStorageDialog} buttonProps={{ variant: 'contained' }} />
        <Button variant="contained" color="primary" onClick={reloadStorages}>
          Reload
        </Button>
      </TitleHeader>

      <StoragesTable />
    </DefaultLayout>
  );
};

export default Page;
