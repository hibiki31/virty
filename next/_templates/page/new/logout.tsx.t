---
to: "<%= pageType === 'logout' ? `pages/${url}.tsx` : null %>"
---

import type { NextPage } from 'next';
import Head from 'next/head';
import { NoAuthLayout } from '~/components/layouts/NoAuthLayout';
import { makeRequireLogoutProps } from '~/lib/utils/makeGetServerSideProps';

export const getServerSideProps = makeRequireLogoutProps();

const Page: NextPage = () => {
  return (
    <NoAuthLayout>
      <Head>
        <title>Virty</title>
      </Head>
    </NoAuthLayout>
  );
};

export default Page;
