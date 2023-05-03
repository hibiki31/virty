import { Button } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { TasksTable } from '~/components/tables/TasksTable';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useConfirmDialog } from '~/store/confirmDialogState';

export const getServerSideProps = makeRequireLoginProps();

const Page: NextPage = () => {
  const { openConfirmDialog } = useConfirmDialog();

  const deleteAllTasks = async () => {
    const confirmed = await openConfirmDialog({
      title: 'Delete all tasks',
      description:
        'Are you sure you want to delete all tasks?\nThis operation deletes everything, including the running and finished portions. Tasks in progress may be executed incompletely.',
      submitText: 'Delete',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    console.log('delete all tasks');
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - Tasks</title>
      </Head>

      <TitleHeader primary="Tasks">
        <Button variant="contained" color="error" onClick={deleteAllTasks}>
          Delete
        </Button>
      </TitleHeader>

      <TasksTable />
    </DefaultLayout>
  );
};

export default Page;
