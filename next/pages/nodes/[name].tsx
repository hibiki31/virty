import type { NextPage } from 'next';
import Head from 'next/head';
import useSWR from 'swr';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { TitleHeader } from '~/components/utils/TitleHeader';
import { nodesApi } from '~/lib/api';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';
import Error404Page from '../404';
import ErrorPage from '../error';

type Props = {
  name: string;
};

export const getServerSideProps = makeRequireLoginProps(async ({ params }) => {
  const name = params?.name;
  if (typeof name !== 'string') {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      name,
    },
  };
});

const Page: NextPage<Props> = ({ name }) => {
  const { data, error, isValidating } = useSWR(
    ['nodesApi.getApiNodesApiNodesNameGet', name],
    ([, name]) =>
      nodesApi
        .getApiNodesApiNodesNameGet(name)
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
        <title>Virty - {name}</title>
      </Head>

      <TitleHeader primary={name} />

      <pre>{JSON.stringify(data, null, 2)}</pre>
    </DefaultLayout>
  );
};

export default Page;
