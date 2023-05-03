import { Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddStoragePoolDialog } from '~/components/dialogs/AddStoragePoolDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { StoragePoolsTable } from '~/components/tables/StoragePoolsTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Storage Pools</title>
      </Head>

      <TitleHeader primary="Storage Pools">
        <OpenDialogButton label="Add" DialogComponent={AddStoragePoolDialog} buttonProps={{ variant: 'contained' }} />
      </TitleHeader>

      <StoragePoolsTable />
    </DefaultLayout>
  );
};

export default Page;
