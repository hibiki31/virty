import { Accordion, AccordionDetails, AccordionSummary, Box, Grid, Link, Typography } from '@mui/material';
import { ChevronDown } from 'mdi-material-ui';
import type { NextPage } from 'next';
import Head from 'next/head';
import NextLink from 'next/link';
import useSWR from 'swr';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { BaseTable } from '~/components/tables/BaseTable';
import { ResourceIcon } from '~/components/tables/TasksTable/ResourceIcon';
import { TaskStatusIcon } from '~/components/tables/TasksTable/TaskStatusIcon';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { tasksApi } from '~/lib/api';
import { formatDate } from '~/lib/utils/date';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
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
    ['tasksApi.getTask', id],
    ([, id]) =>
      tasksApi
        .getTask(id)
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

  if (isValidating) {
    return <DefaultLayout isLoading />;
  }

  if (error) {
    return <ErrorPage message={error.message} />;
  }

  if (!data) {
    return <Error404Page />;
  }

  return (
    <DefaultLayout>
      <Head>
        <title>Virty - {id}</title>
      </Head>

      <TitleHeader primary={id} />

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item sx={{ ml: -2 }}>
          <BaseTable
            cols={[
              {
                name: <Typography variant="body2">Status</Typography>,
                getItem: (item) => (
                  <Box display="flex" alignItems="center">
                    <TaskStatusIcon status={data.status!} />
                    <Typography variant="subtitle1" sx={{ ml: 1 }}>
                      {item.status}
                    </Typography>
                  </Box>
                ),
              },
              {
                name: <Typography variant="body2">Request</Typography>,
                getItem: (item) => (
                  <Box display="flex" alignItems="center">
                    <ResourceIcon method={item.method!} resource={item.resource!} />
                    <Typography variant="subtitle1" sx={{ ml: 1 }}>
                      {item.method}.{item.resource}.{item.object}
                    </Typography>
                  </Box>
                ),
              },
              {
                name: <Typography variant="body2">User</Typography>,
                getItem: (item) => <Typography variant="subtitle1">{item.userId}</Typography>,
              },
              {
                name: <Typography variant="body2">Created At</Typography>,
                getItem: (item) => <Typography variant="subtitle1">{formatDate(item.postTime!)}</Typography>,
              },
              {
                name: <Typography variant="body2">Started At</Typography>,
                getItem: (item) => (
                  <Typography variant="subtitle1">{item.startTime ? formatDate(item.startTime) : '-'}</Typography>
                ),
              },
              {
                name: <Typography variant="body2">Updated At</Typography>,
                getItem: (item) => (
                  <Typography variant="subtitle1">{item.updateTime ? formatDate(item.updateTime) : '-'}</Typography>
                ),
              },
              {
                name: <Typography variant="body2">Run Time</Typography>,
                getItem: (item) => (
                  <Typography variant="subtitle1">
                    {item.runTime ? `${Math.round(item.runTime! * 100) / 100} s` : '-'}
                  </Typography>
                ),
              },
              {
                name: <Typography variant="body2">Dependence Task</Typography>,
                getItem: (item) =>
                  item.dependenceUuid ? (
                    <NextLink href={`/tasks/${item.dependenceUuid}`} passHref>
                      <Link variant="subtitle1">{item.dependenceUuid}</Link>
                    </NextLink>
                  ) : (
                    <Typography variant="subtitle1">-</Typography>
                  ),
              },
            ]}
            items={[data]}
            disableElevation
            hiddenBorder
            dense
          />
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Accordion defaultExpanded={!!data.result} disableGutters disabled={!data.result}>
            <AccordionSummary expandIcon={<ChevronDown />}>
              <Typography>Result</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ overflow: 'auto' }}>
              <pre>{JSON.stringify(data.result, null, 2)}</pre>
            </AccordionDetails>
          </Accordion>
        </Grid>
        <Grid item xs={12}>
          <Accordion defaultExpanded={!!data.message} disableGutters disabled={!data.message}>
            <AccordionSummary expandIcon={<ChevronDown />}>
              <Typography>Message</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ overflow: 'auto' }}>
              <pre>{data.message}</pre>
            </AccordionDetails>
          </Accordion>
        </Grid>
        <Grid item xs={12}>
          <Accordion defaultExpanded={!!data.log} disableGutters disabled={!data.log}>
            <AccordionSummary expandIcon={<ChevronDown />}>
              <Typography>Log</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ overflow: 'auto' }}>
              <pre>{data.log}</pre>
            </AccordionDetails>
          </Accordion>
        </Grid>
        <Grid item xs={12} sx={{ mb: 2 }}>
          <Accordion defaultExpanded={!!data.request} disableGutters disabled={!data.request}>
            <AccordionSummary expandIcon={<ChevronDown />}>
              <Typography>Request Details</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ overflow: 'auto' }}>
              <pre>{JSON.stringify(data.request, null, 2)}</pre>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>
    </DefaultLayout>
  );
};

export default Page;
