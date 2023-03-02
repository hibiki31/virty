import { Button, Card, CardHeader, Grid, Typography } from '@mui/material';
import { NextPage } from 'next';
import Head from 'next/head';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { vmsApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import { useNotistack } from '~/lib/utils/notistack';
import useSWR from 'swr';
import { BaseTable } from '~/components/tables/BaseTable';

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
                  cols={[{ getItem: (row) => row.name }, { getItem: (row) => row.value }]}
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
                cols={[{ getItem: (row) => row.name }, { getItem: (row) => row.value }]}
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
          Network
        </Grid>

        <Grid item xs={12} lg={6}>
          Storage
        </Grid>
      </Grid>
    </DefaultLayout>
  );
};

export default VMPage;
