import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddUserDialog } from '~/components/dialogs/AddUserDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { UsersTable } from '~/components/tables/UsersTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Users</title>
      </Head>

      <TitleHeader primary="Users">
        <OpenDialogButton label="Add" DialogComponent={AddUserDialog} buttonProps={{ variant: 'contained' }} />
      </TitleHeader>

      <UsersTable />
    </DefaultLayout>
  );
};

export default Page;
