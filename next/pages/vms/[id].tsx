import { Box, Button, Card, CardHeader, Grid, IconButton, Typography } from '@mui/material';
import { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { vmsApi, tasksVmsApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import useSWR from 'swr';
import { BaseTable } from '~/components/tables/BaseTable';
import { DomainDrive, DomainInterface } from '~/lib/api/generated';
import { Delete, Pencil, Play, Stop } from 'mdi-material-ui';
import Error404Page from '../404';
import ErrorPage from '../error';
import { ChangeNetworkDialog } from '~/components/dialogs/ChangeNetworkDialog';
import { MouseEvent, useState } from 'react';
import { StorageActionsMenu } from '~/components/menus/StorageActionsMenu';
import { VMConsoleCard } from '~/components/vm/VMConsoleCard';
import { VM_STATUS } from '~/lib/api/vm';
import { useNotistack } from '~/lib/utils/notistack';
import { useConfirmDialog } from '~/store/confirmDialogState';
import { VMStatusIcon } from '~/components/vm/VMStatusIcon';
import { TitleHeader } from '~/components/utils/TitleHeader';

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

const VMPage: NextPage<Props> = ({ id }) => {
  const { data, error, isValidating } = useSWR(
    ['vmsApi.getVm', id],
    ([, id]) =>
      vmsApi
        .getVm(id)
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
  const [macAddress, setMacAddress] = useState<string | undefined | null>(undefined);
  const [storageAnchorEl, setStorageAnchorEl] = useState<null | HTMLElement>(null);
  const [storage, setStorage] = useState<DomainDrive | undefined>(undefined);
  const { enqueueNotistack } = useNotistack();
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

  const startVM = () =>
    tasksVmsApi
      .updateVmPowerStatus(id, { status: 'on' })
      .then(() => enqueueNotistack('VM is starting.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to start VM.', { variant: 'error' }));

  const stopVM = async () => {
    const confirmed = await openConfirmDialog({
      title: 'Stop VM',
      description: 'Are you sure you want to stop this VM?',
      submitText: 'Stop',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    return tasksVmsApi
      .updateVmPowerStatus(id, { status: 'off' })
      .then(() => enqueueNotistack('VM is stopping.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to stop VM.', { variant: 'error' }));
  };

  const deleteVM = async () => {
    const confirmed = await openConfirmDialog({
      title: 'Delete VM',
      description: 'Are you sure you want to delete this VM?',
      submitText: 'Delete',
      color: 'error',
    });
    if (!confirmed) {
      return;
    }

    return tasksVmsApi
      .deleteVm(id)
      .then(() => enqueueNotistack('VM is deleting.', { variant: 'success' }))
      .catch(() => enqueueNotistack('Failed to delete VM.', { variant: 'error' }));
  };

  const openChangeNetworkDialog = (item: DomainInterface) => {
    setMacAddress(item.mac);
  };

  const openStorageActionsMenu = (e: MouseEvent<HTMLElement>, item: DomainDrive) => {
    setStorageAnchorEl(e.currentTarget);
    setStorage(item);
  };

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - {data.name}</title>
      </Head>

      <ChangeNetworkDialog
        open={!!macAddress}
        onClose={() => setMacAddress(undefined)}
        vmUuid={data.uuid}
        macAddress={macAddress}
        nodeName={data.nodeName}
      />

      <StorageActionsMenu
        anchorEl={storageAnchorEl}
        onClose={() => setStorageAnchorEl(null)}
        vmUuid={data.uuid}
        storage={storage}
        nodeName={data.nodeName}
      />

      <TitleHeader prefix={<VMStatusIcon status={data.status} />} primary={data.name} secondary={data.uuid} />

      <Grid container spacing={2} mb={2}>
        <Grid item xs={12} md={5} lg={4} xl={3}>
          <VMConsoleCard uuid={data.uuid} status={data.status} />
        </Grid>
        <Grid item container spacing={2} xs={12} md direction="column">
          <Grid item>
            <Card>
              <Grid container spacing={2} sx={{ p: 1 }}>
                <Grid item>
                  <Button color="success" size="small" disabled={data.status === VM_STATUS.POWER_ON} onClick={startVM}>
                    <Play sx={{ mr: 1 }} />
                    Start
                  </Button>
                </Grid>
                <Grid item>
                  <Button color="error" size="small" disabled={data.status === VM_STATUS.POWER_OFF} onClick={stopVM}>
                    <Stop sx={{ mr: 1 }} />
                    Stop
                  </Button>
                </Grid>
                <Grid item ml="auto">
                  <Button color="error" size="small" onClick={deleteVM}>
                    <Delete sx={{ mr: 1 }} />
                    Delete
                  </Button>
                </Grid>
              </Grid>
            </Card>
          </Grid>
          <Grid item container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Card sx={{ height: '100%' }}>
                <CardHeader title={<Typography variant="h6">Spec</Typography>} />
                <Grid item pb={2}>
                  <BaseTable
                    cols={[{ getItem: (item) => item.name }, { getItem: (item) => item.value }]}
                    items={[
                      { name: 'CPU', value: `${data.core} Core` },
                      { name: 'Memory', value: `${data.memory / 1024} GB` },
                    ]}
                    hiddenHeader
                    hiddenBorder
                    disableElevation
                    dense
                  />
                </Grid>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Card>
                <CardHeader title={<Typography variant="h6">Node</Typography>} />
                <Grid item pb={2}>
                  <BaseTable
                    cols={[{ getItem: (item) => item.name }, { getItem: (item) => item.value }]}
                    items={[
                      { name: 'Name', value: data.node.name },
                      { name: 'IP', value: data.node.domain },
                      { name: 'Status', value: data.node.status },
                      { name: 'VNC Port', value: data.vncPort },
                    ]}
                    hiddenHeader
                    hiddenBorder
                    disableElevation
                    dense
                  />
                </Grid>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title={<Typography variant="h6">Network</Typography>} />
            <BaseTable
              cols={[
                { name: 'Type', getItem: (item: DomainInterface) => item.type },
                { name: 'MAC Address', getItem: (item: DomainInterface) => item.mac },
                { name: 'Network Name', getItem: (item: DomainInterface) => item.network },
                { name: 'Bridge Device', getItem: (item: DomainInterface) => item.bridge },
                { name: 'OVS Port', getItem: (item: DomainInterface) => item.port },
                { name: 'Target', getItem: (item: DomainInterface) => item.target },
                {
                  name: 'Actions',
                  align: 'center',
                  getItem: (item: DomainInterface) => (
                    <IconButton
                      disabled={data.status !== VM_STATUS.POWER_OFF}
                      onClick={() => openChangeNetworkDialog(item)}
                    >
                      <Pencil />
                    </IconButton>
                  ),
                },
              ]}
              items={data.interfaces || []}
              disableElevation
              dense
            />
          </Card>
        </Grid>

        <Grid item xs={12} lg={6} mb={2}>
          <Card>
            <CardHeader title={<Typography variant="h6">Storage</Typography>} />
            <BaseTable
              cols={[
                { name: 'Device', getItem: (item: DomainDrive) => item.device },
                { name: 'Type', getItem: (item: DomainDrive) => item.type },
                { name: 'Source', getItem: (item: DomainDrive) => item.source },
                { name: 'Target', getItem: (item: DomainDrive) => item.target },
                {
                  name: 'Actions',
                  align: 'center',
                  getItem: (item: DomainDrive) =>
                    item.device === 'cdrom' ? (
                      <IconButton onClick={(e) => openStorageActionsMenu(e, item)}>
                        <Pencil />
                      </IconButton>
                    ) : (
                      <Box sx={{ width: 40, height: 40 }} />
                    ),
                },
              ]}
              items={data.drives || []}
              disableElevation
              dense
            />
          </Card>
        </Grid>
      </Grid>
    </DefaultLayout>
  );
};

export default VMPage;
