import type { NextPage } from 'next';
import Head from 'next/head';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddProjectDialog } from '~/components/dialogs/AddProjectDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { ProjectsTable } from '~/components/tables/ProjectsTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Projects</title>
      </Head>

      <TitleHeader primary="Projects">
        <OpenDialogButton label="Create" DialogComponent={AddProjectDialog} buttonProps={{ variant: 'contained' }} />
      </TitleHeader>

      <ProjectsTable />
    </DefaultLayout>
  );
};

export default Page;
