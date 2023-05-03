import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddNetworkPoolDialog } from '~/components/dialogs/AddNetworkPoolDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NetworkPoolsTable } from '~/components/tables/NetworkPoolsTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Network Pools</title>
      </Head>

      <TitleHeader primary="Network Pools">
        <OpenDialogButton label="Add" DialogComponent={AddNetworkPoolDialog} buttonProps={{ variant: 'contained' }} />
      </TitleHeader>

      <NetworkPoolsTable />
    </DefaultLayout>
  );
};

export default Page;
