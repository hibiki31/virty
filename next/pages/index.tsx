import type { NextPage } from 'next';
import { DefaultLayout } from '~/components/layouts/DefaultLayout';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps();

const HomePage: NextPage = () => {
  return (
    <DefaultLayout>
      <h1>Home</h1>
    </DefaultLayout>
  );
};

export default HomePage;
