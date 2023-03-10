import type { NextPage } from 'next';
import nookies from 'nookies';
import { makeRequireLoginProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLoginProps(async (ctx) => {
  nookies.destroy(ctx, 'token', { path: '/' });

  return {
    redirect: {
      destination: '/login',
      permanent: false,
    },
  };
});

const Page: NextPage = () => {
  return null;
};

export default Page;
