import { Button, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import useSWR from 'swr';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddPortDialog } from '~/components/dialogs/AddPortDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { PortsTable } from '~/components/tables/PortsTable';
import { networkApi } from '~/lib/api';
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
    ['networkApi.getApiNetworksUuidApiNetworksUuidGet', id],
    ([, id]) =>
      networkApi
        .getApiNetworksUuidApiNetworksUuidGet(id)
        .then((res) => res.data)
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

  const deleteNetwork = async () => {
    const confirmed = await openConfirmDialog({
      title: 'Delete Network',
      description: `Are you sure you want to delete the network "${data.name}"?\nRunning VMs will not be affected.`,
      submitText: 'Delete',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    console.log('delete network');
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
          <Button variant="contained" color="error" disableElevation size="small" onClick={deleteNetwork}>
            Delete
          </Button>
        </Grid>
      </Grid>

      <Grid container alignItems="center" spacing={2} sx={{ mt: 0, mb: 1 }}>
        <Grid item>
          <Typography variant="h4">Virtual Port</Typography>
        </Grid>
        <Grid item>
          <OpenDialogButton
            label="Add"
            DialogComponent={AddPortDialog}
            buttonProps={{ variant: 'contained' }}
            dialogProps={{ networkUuid: data.uuid }}
          />
        </Grid>
      </Grid>
      <PortsTable networkUuid={data.uuid} ports={data.portgroups} />
    </DefaultLayout>
  );
};

export default Page;
