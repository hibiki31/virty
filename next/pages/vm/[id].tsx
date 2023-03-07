import { Box, Button, Card, CardHeader, Grid, IconButton, Typography } from '@mui/material';
import { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { vmsApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import useSWR from 'swr';
import { BaseTable } from '~/components/tables/BaseTable';
import { GetDomainDrives, GetDomainInterfaces } from '~/lib/api/generated';
import { Pencil } from 'mdi-material-ui';
import Error404Page from '../404';
import ErrorPage from '../error';
import { ChangeNetworkDialog } from '~/components/dialogs/ChangeNetworkDialog';
import { MouseEvent, useState } from 'react';
import { StorageActionsMenu } from '~/components/menus/StorageActionsMenu';

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
    ['vmsApi.getApiDomainUuidApiVmsUuidGet', id],
    ([, id]) =>
      vmsApi
        .getApiDomainUuidApiVmsUuidGet(id)
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
  const [macAddress, setMacAddress] = useState<string | undefined>(undefined);
  const [storageAnchorEl, setStorageAnchorEl] = useState<null | HTMLElement>(null);
  const [storage, setStorage] = useState<GetDomainDrives | undefined>(undefined);

  if (isValidating) {
    return <DefaultLayout isLoading />;
  }

  if (error) {
    return <ErrorPage message={error.message} />;
  }

  if (!data) {
    return <Error404Page />;
  }

  const openChangeNetworkDialog = (item: GetDomainInterfaces) => {
    setMacAddress(item.mac);
  };

  const openStorageActionsMenu = (e: MouseEvent<HTMLElement>, item: GetDomainDrives) => {
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
        onClose={() => setStorage(undefined)}
        vmUuid={data.uuid}
        storage={storage}
        nodeName={data.nodeName}
      />

      <Grid container alignItems="center" sx={{ m: 2 }}>
        <Typography variant="h6" sx={{ mr: 2 }}>
          {data.name}
        </Typography>
        <Typography variant="subtitle1">{data.uuid}</Typography>
      </Grid>

      <Grid container spacing={2}>
        <Grid item container spacing={2} direction="column" xs={12} md={6} lg={3}>
          <Grid item>
            <Card>
              <Grid container spacing={2} sx={{ p: 2 }}>
                <Grid item xs={6}>
                  <Button variant="contained" disableElevation fullWidth size="small" disabled>
                    Console
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button variant="contained" color="error" disableElevation fullWidth size="small">
                    Delete
                  </Button>
                </Grid>
              </Grid>
            </Card>
          </Grid>

          <Grid item>
            <Card>
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
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
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

        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title={<Typography variant="h6">Network</Typography>} />
            <BaseTable
              cols={[
                { name: 'Type', getItem: (item: GetDomainInterfaces) => item.type },
                { name: 'MAC Address', getItem: (item: GetDomainInterfaces) => item.mac },
                { name: 'Network Name', getItem: (item: GetDomainInterfaces) => item.network },
                { name: 'Bridge Device', getItem: (item: GetDomainInterfaces) => item.bridge },
                { name: 'OVS Port', getItem: (item: GetDomainInterfaces) => item.port },
                { name: 'Target', getItem: (item: GetDomainInterfaces) => item.target },
                {
                  name: 'Actions',
                  align: 'center',
                  getItem: (item: GetDomainInterfaces) => (
                    <IconButton onClick={() => openChangeNetworkDialog(item)}>
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

        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title={<Typography variant="h6">Storage</Typography>} />
            <BaseTable
              cols={[
                { name: 'Device', getItem: (item: GetDomainDrives) => item.device },
                { name: 'Type', getItem: (item: GetDomainDrives) => item.type },
                { name: 'Source', getItem: (item: GetDomainDrives) => item.source },
                { name: 'Target', getItem: (item: GetDomainDrives) => item.target },
                {
                  name: 'Actions',
                  align: 'center',
                  getItem: (item: GetDomainDrives) =>
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
