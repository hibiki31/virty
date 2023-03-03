import { Button, Card, CardHeader, Grid, IconButton, Typography } from '@mui/material';
import { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { vmsApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';
import useSWR from 'swr';
import { BaseTable } from '~/components/tables/BaseTable';
import { GetDomainDrives, GetDomainInterfaces } from '~/lib/api/generated';
import { Pencil } from 'mdi-material-ui';

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
    ([, id]) => vmsApi.getApiDomainUuidApiVmsUuidGet(id).then((res) => res.data),
    { revalidateOnFocus: false }
  );
  const { enqueueNotistack } = useNotistack();

  if (error) {
    enqueueNotistack('Failed to fetch VM.', { variant: 'error' });
    return null;
  }

  if (!data || isValidating) {
    return null;
  }

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - {data.name}</title>
      </Head>

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
          <Card sx={{ height: '100%' }}>
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
                    <IconButton>
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
                    item.device === 'cdrom' && (
                      <IconButton>
                        <Pencil />
                      </IconButton>
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
