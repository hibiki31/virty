import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { JoinNodeDialog } from '~/components/dialogs/JoinNodeDialog';
import { NodeKeyDialog } from '~/components/dialogs/NodeKeyDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { NodesTable } from '~/components/tables/NodesTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Nodes</title>
      </Head>

      <TitleHeader primary="Nodes">
        <OpenDialogButton label="Key" DialogComponent={NodeKeyDialog} buttonProps={{ variant: 'contained' }} />
        <OpenDialogButton label="Join" DialogComponent={JoinNodeDialog} buttonProps={{ variant: 'contained' }} />
      </TitleHeader>

      <NodesTable />
    </DefaultLayout>
  );
};

export default Page;
