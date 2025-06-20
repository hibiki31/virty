import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddFlavorDialog } from '~/components/dialogs/AddFlavorDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { FlavorsTable } from '~/components/tables/FlavorsTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Flavors</title>
      </Head>

      <TitleHeader primary="Flavors">
        <OpenDialogButton label="Add" DialogComponent={AddFlavorDialog} buttonProps={{ variant: 'contained' }} />
      </TitleHeader>

      <FlavorsTable />
    </DefaultLayout>
  );
};

export default Page;
