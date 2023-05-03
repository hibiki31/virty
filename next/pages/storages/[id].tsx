import { Button } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import useSWR from 'swr';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { ChangeStorageMetaDataDialog } from '~/components/dialogs/ChangeStorageMetaDataDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { storagesApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useConfirmDialog } from '~/store/confirmDialogState';
import Error404Page from '../404';
import ErrorPage from '../error';

type Props = {
  id: string;
};

export const getServerSideProps = makeRequireLoginProps(async ({ params }) => {
  const id = params?.id;
  if (typeof id !== 'string') {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      id,
    },
  };
});

const Page: NextPage<Props> = ({ id }) => {
  const { data, error, isValidating } = useSWR(
    'storagesApi.getApiStoragesApiStoragesGet',
    () =>
      storagesApi
        .getApiStoragesApiStoragesGet()
        .then((res) => res.data.find((storage) => storage.uuid === id))
        .catch((err) => {
          if (err.response.status === 404) {
            return null;
          }
          throw err;
        }),
    {
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    }
  );
  const { openConfirmDialog } = useConfirmDialog();

  if (isValidating) {
    return <DefaultLayout isLoading />;
  }

  if (error) {
    return <ErrorPage message={error.message} />;
  }

  if (!data) {
    return <Error404Page />;
  }

  const deleteStorage = async () => {
    const confirmed = await openConfirmDialog({
      title: 'Delete Storage',
      description: 'Are you sure you want to delete this storage?',
      submitText: 'Delete',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    console.log('delete storage');
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - {data.name}</title>
      </Head>

      <TitleHeader primary={data.name} secondary={data.uuid}>
        <OpenDialogButton
          label="MetaData"
          DialogComponent={ChangeStorageMetaDataDialog}
          buttonProps={{ variant: 'contained', size: 'small' }}
          dialogProps={{ uuid: id, metadata: data.metaData }}
        />
        <Button variant="contained" color="error" disableElevation size="small" onClick={deleteStorage}>
          Delete
        </Button>
      </TitleHeader>

      <pre>{JSON.stringify(data, null, 2)}</pre>
    </DefaultLayout>
  );
};

export default Page;
