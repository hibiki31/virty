import { Button, Grid, Typography } from '@mui/material';
import type { NextPage } from 'next';
import Head from 'next/head';
import useSWR from 'swr';
import { OpenDialogButton } from '~/components/buttons/OpenDialogButton';
import { AddPortDialog } from '~/components/dialogs/AddPortDialog';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { BaseTable } from '~/components/tables/BaseTable';
import { PortsTable } from '~/components/tables/PortsTable';
import { networkApi, tasksNetworksApi } from '~/lib/api';
import { formatDate } from '~/lib/utils/date';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';
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
  const { enqueueNotistack } = useNotistack();

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

    return tasksNetworksApi
      .deleteApiStorageApiTasksNetworksUuidDelete(id)
      .then(() => enqueueNotistack('Network is deleting.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to delete network.', { variant: 'error' }));
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

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <BaseTable
            cols={[{ getItem: (item) => item.name }, { getItem: (item) => item.value }]}
            items={[
              { name: 'Description', value: data.description },
              { name: 'Node', value: data.nodeName },
              { name: 'Bridge', value: data.bridge },
              { name: 'Type', value: data.type },
              { name: 'Active', value: data.active },
              { name: 'Auto Start', value: data.autoStart },
              { name: 'DHCP', value: data.dhcp },
              { name: 'Token Updated At', value: formatDate(Number(data.updateToken) * 1000) },
            ]}
            hiddenHeader
            disableElevation
          />
        </Grid>
        <Grid item container xs={12} lg={6} direction="column" spacing={2}>
          <Grid item container spacing={2} alignItems="center">
            <Grid item>
              <Typography variant="h5">Virtual Port</Typography>
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
          <Grid item>
            <PortsTable networkUuid={data.uuid} ports={data.portgroups} />
          </Grid>
        </Grid>
      </Grid>
    </DefaultLayout>
  );
};

export default Page;
