import { Button, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import useSWR from 'swr';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
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
    ['networkApi.getApiNetworksUuidApiNetworksUuidGet'],
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

      <Grid container alignItems="baseline" spacing={2} sx={{ mt: 0, mb: 2 }}>
        <Grid item>
          <Typography variant="h6">{data.name}</Typography>
        </Grid>
        <Grid item>
          <Typography variant="subtitle1">{data.uuid}</Typography>
        </Grid>
        <Grid item>
          <Button variant="contained" color="error" disableElevation size="small" onClick={deleteStorage}>
            Delete
          </Button>
        </Grid>
      </Grid>

      <pre>{JSON.stringify(data, null, 2)}</pre>
    </DefaultLayout>
  );
};

export default Page;
